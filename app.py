import os
import mimetypes
import json
import uuid
from datetime import datetime
from typing import Optional
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pdf_processing.infrastructure.pdf_processor import MuPDFProcessor
from pdf_processing.infrastructure.pdf_repository import FileSystemPDFRepository
from pdf_processing.application.pdf_service import PDFService
from config import SECRET_KEY

# MIME type configuration
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('text/javascript', '.mjs')
mimetypes.add_type('text/css', '.css')

# Set default JavaScript MIME type
mimetypes.init()
mimetypes.types_map['.js'] = 'application/javascript'
mimetypes.types_map['.mjs'] = 'application/javascript'

# Supported file types
ALLOWED_EXTENSIONS = {'pdf'}

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
SECTIONS_FOLDER = os.path.join(BASE_DIR, 'sections')
METADATA_FOLDER = os.path.join(BASE_DIR, 'metadata')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SECTIONS_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

# Initialize PDF processing components
pdf_repository = FileSystemPDFRepository()
pdf_processor = MuPDFProcessor(repository=pdf_repository)
pdf_service = PDFService(processor=pdf_processor, repository=pdf_repository)

# Flask app initialization
app = Flask(__name__, static_folder='frontend/dist')
app.secret_key = SECRET_KEY

# Enable CORS with more permissive configuration for development
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:4173", "http://0.0.0.0:4173", "http://172.31.196.62:4173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "expose_headers": ["Content-Type", "X-Total-Count"],
        "supports_credentials": True,
        "max_age": 600
    }
})

# Set default response headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers',
                      'Content-Type, Authorization, X-Requested-With, Accept')
    response.headers.add('Access-Control-Allow-Methods',
                      'GET, PUT, POST, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '600')

    # Set proper MIME types for static files
    if response.mimetype == 'text/html':
        if request.path.endswith('.js') or request.path.endswith('.mjs'):
            response.mimetype = 'application/javascript'
        elif request.path.endswith('.css'):
            response.mimetype = 'text/css'

    return response

# Serve SPA for all non-API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, 'index.html')

# Helper Functions
def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_metadata(book_id: str, metadata: dict):
    """Save metadata to a JSON file."""
    filepath = os.path.join(METADATA_FOLDER, f"{book_id}.json")
    try:
        with open(filepath, 'w') as f:
            json.dump(metadata, f)
        return True
    except Exception as e:
        app.logger.error(f"Failed to save metadata for {book_id}: {e}")
        return False

def load_metadata(book_id: str) -> Optional[dict]:
    """Load metadata from a JSON file."""
    filepath = os.path.join(METADATA_FOLDER, f"{book_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            app.logger.error(f"Failed to load metadata for {book_id}: {e}")
    return None

async def process_pdf_file(file):
    """Process and extract metadata from a PDF file."""
    if not file or not file.filename:
        raise ValueError("No file selected")

    if not allowed_file(file.filename):
        raise ValueError("Invalid file type. Only PDF files are allowed")

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        processed_pdf = await pdf_service.process_pdf(file_path)

        metadata = {
            "title": os.path.splitext(filename)[0],
            "author": "Unknown",
            "filename": filename,
            "id": filename,
            "uploadDate": datetime.now().isoformat(),
            "status": processed_pdf.progress.status.value,
            "current_page": processed_pdf.progress.current_page,
            "total_pages": processed_pdf.progress.total_pages,
            "processed_sections": processed_pdf.progress.processed_sections,
            "processed_images": len(processed_pdf.images),
            "error_message": processed_pdf.progress.error_message,
            "cover_image": None
        }

        save_metadata(filename, metadata)
        return metadata
    except Exception as e:
        error_metadata = {
            "title": os.path.splitext(filename)[0],
            "author": "Unknown",
            "filename": filename,
            "id": filename,
            "uploadDate": datetime.now().isoformat(),
            "status": "failed",
            "error_message": str(e)
        }
        save_metadata(filename, error_metadata)
        raise

# Routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    app.logger.info("Login route called with method: %s", request.method)
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == 'admin' and password == 'admin':
        response = {'id': 1, 'username': 'admin', 'email': 'admin@example.com'}
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/books/upload', methods=['POST'])
async def upload_pdfs():
    """Upload and process PDF files."""
    try:
        uploaded_files = request.files.getlist('pdf_files')
        if not uploaded_files:
            return jsonify({
                "status": "error",
                "message": "No files selected",
                "code": 400
            }), 400

        processed_files = []
        errors = []

        for file in uploaded_files:
            try:
                metadata = await process_pdf_file(file)
                processed_files.append(metadata)
            except Exception as e:
                errors.append({"filename": file.filename, "error": str(e)})

        if not processed_files:
            return jsonify({
                "status": "error",
                "message": "All files failed to process",
                "errors": errors,
                "code": 400
            }), 400

        response_data = {"status": "success", "books": processed_files}
        if errors:
            response_data["errors"] = errors

        return jsonify(response_data)
    except Exception as e:
        app.logger.error(f"Upload processing error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500

@app.route('/api/books')
def get_books():
    """Retrieve the list of all books."""
    try:
        books = []
        # First check for processed PDFs in sections folder
        for book_dir in os.listdir(SECTIONS_FOLDER):
            book_path = os.path.join(SECTIONS_FOLDER, book_dir)
            if os.path.isdir(book_path):
                histoire_path = os.path.join(book_path, "histoire")
                if os.path.exists(histoire_path):
                    chapters = [f for f in os.listdir(histoire_path) if f.endswith('.md')]
                    if chapters:
                        book_id = f"{book_dir}.pdf"
                        metadata = load_metadata(book_id)
                        if not metadata:
                            metadata = {
                                "title": book_dir,
                                "author": "Unknown",
                                "filename": book_id,
                                "id": book_id,
                                "uploadDate": datetime.now().isoformat(),
                                "status": "processed",
                                "total_chapters": len(chapters)
                            }
                        books.append(metadata)
        
        # Then check metadata folder for any additional books
        for metadata_file in os.listdir(METADATA_FOLDER):
            if metadata_file.endswith('.json'):
                book_id = os.path.splitext(metadata_file)[0]
                if not any(book['id'] == book_id for book in books):
                    metadata = load_metadata(book_id)
                    if metadata:
                        books.append(metadata)
        
        return jsonify({"status": "success", "books": books})
    except Exception as e:
        app.logger.error(f"Error retrieving books: {e}")
        return jsonify({
            "status": "error",
            "message": "Une erreur est survenue lors de la récupération des livres",
            "details": str(e),
            "code": 500
        }), 500

@app.route('/api/books/<book_id>')
def get_book(book_id):
    """Retrieve metadata for a specific book."""
    try:
        metadata = load_metadata(book_id)
        if not metadata:
            return jsonify({
                "status": "error",
                "message": "Book not found",
                "code": 404
            }), 404
        return jsonify(metadata)
    except Exception as e:
        app.logger.error(f"Error retrieving book metadata for {book_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500

@app.route('/api/books/<book_id>/chapters/<int:chapter_index>')
def get_book_chapter(book_id, chapter_index):
    """Retrieve a specific chapter of a book."""
    try:
        # Log request details
        app.logger.info(f"Fetching chapter {chapter_index} for book {book_id}")
        
        if not book_id:
            return jsonify({
                "error": "Book ID is required",
                "details": "No book ID provided in the request"
            }), 400
        
        # Clean up book_id and construct the path
        clean_book_id = book_id.replace(".pdf", "").strip()
        histoire_path = os.path.join(SECTIONS_FOLDER, clean_book_id, "histoire")
        
        app.logger.info(f"Looking for chapters in: {histoire_path}")
        
        # Check if the book has been processed
        if not os.path.exists(os.path.join(SECTIONS_FOLDER, clean_book_id)):
            return jsonify({
                "error": "Book not processed",
                "details": "This book needs to be processed first"
            }), 404

        if not os.path.exists(histoire_path):
            app.logger.error(f"Book directory not found: {histoire_path}")
            return jsonify({
                "error": "Book not found",
                "details": "The requested book does not exist"
            }), 404

        chapter_files = sorted([
            file for file in os.listdir(histoire_path) 
            if file.endswith('.md')
        ], key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))

        if not chapter_files:
            app.logger.error(f"No chapters found in directory: {histoire_path}")
            return jsonify({
                "error": "No chapters available",
                "details": "The book has no readable chapters"
            }), 404

        if chapter_index < 0 or chapter_index >= len(chapter_files):
            app.logger.error(f"Chapter index out of range: {chapter_index}")
            return jsonify({
                "error": "Chapter not found",
                "details": "The requested chapter index is out of range"
            }), 404

        chapter_path = os.path.join(histoire_path, chapter_files[chapter_index])
        app.logger.info(f"Reading chapter from: {chapter_path}")

        if not os.path.exists(chapter_path):
            app.logger.error(f"Chapter file not found: {chapter_path}")
            return jsonify({
                "error": "Chapter file missing",
                "details": "The chapter file could not be found"
            }), 404

        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        if not content:
            app.logger.warning(f"Empty chapter content: {chapter_path}")
            return jsonify({
                "error": "Empty chapter",
                "details": "The chapter has no content"
            }), 404

        response = jsonify({
            "chapter": content,
            "index": chapter_index,
            "total": len(chapter_files)
        })

        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache'
        return response

    except Exception as e:
        app.logger.error(f"Error in get_book_chapter: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/api/books/<book_id>/chapters')
def get_book_chapters(book_id):
    """Retrieve all chapters of a book."""
    try:
        clean_book_id = book_id.replace(".pdf", "").strip()
        histoire_path = os.path.join(SECTIONS_FOLDER, clean_book_id, "histoire")

        if not os.path.exists(histoire_path):
            return jsonify({"error": "Book not found"}), 404

        chapter_files = sorted([
            file for file in os.listdir(histoire_path) 
            if file.endswith('.md')
        ], key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))

        chapters = []
        for file in chapter_files:
            with open(os.path.join(histoire_path, file), 'r', encoding='utf-8') as f:
                chapters.append(f.read())

        return jsonify({'chapters': chapters})
    except Exception as e:
        app.logger.error(f"Error in get_book_chapters: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<book_id>/cover')
def get_book_cover(book_id):
    try:
        clean_book_id = book_id.replace(".pdf", "").strip()
        images_dir = os.path.join(SECTIONS_FOLDER, clean_book_id, 'images')

        if not os.path.exists(images_dir):
            return jsonify({
                "status": "error",
                "message": "Images directory not found",
                "code": 404
            }), 404

        image_files = sorted([
            f for f in os.listdir(images_dir)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ], key=lambda x: x.lower())

        if not image_files:
            return jsonify({
                "status": "error",
                "message": "No cover image found",
                "code": 404
            }), 404

        first_image = image_files[0]
        content_type = mimetypes.guess_type(first_image)[0]

        return send_from_directory(
            images_dir,
            first_image,
            mimetype=content_type
        )

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)