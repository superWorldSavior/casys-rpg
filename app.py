from typing import Optional
from flask import Flask, jsonify, send_from_directory, request, session, redirect
from flask_cors import CORS
from flask_sock import Sock
import json
import io
import fitz
import os
import mimetypes
import traceback
from pathlib import Path
import json
from werkzeug.utils import secure_filename
from datetime import datetime

from pdf_processing.infrastructure.pdf_processor import MuPDFProcessor
from pdf_processing.infrastructure.pdf_repository import FileSystemPDFRepository
from pdf_processing.application.pdf_service import PDFService

# Add MIME types for JavaScript and CSS
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

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
pdf_repository = FileSystemPDFRepository()  # Initialisation du dépôt
pdf_processor = MuPDFProcessor(
    repository=pdf_repository)  # Passer le dépôt à MuPDFProcessor
pdf_service = PDFService(processor=pdf_processor,
                         repository=pdf_repository)  # Tout connecter

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
sock = Sock(app)

# Enable CORS with credentials support
CORS(app,
     resources={
         r"/api/*": {
             "origins": ["http://localhost:5174", "http://172.31.196.48:5174"],
             "supports_credentials": True
         }
     })

# Register auth blueprint
# from auth_routes import auth_bp

# app.register_blueprint(auth_bp)


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_metadata(filename: str, metadata: dict):
    """Save metadata to a JSON file."""
    filepath = os.path.join(METADATA_FOLDER, f"{filename}.json")
    try:
        with open(filepath, 'w') as f:
            json.dump(metadata, f)
        return True
    except Exception as e:
        app.logger.error(f"Failed to save metadata for {filename}: {e}")
        return False


def load_metadata(filename: str) -> Optional[dict]:
    """Load metadata from a JSON file."""
    filepath = os.path.join(METADATA_FOLDER, f"{filename}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            app.logger.error(f"Failed to load metadata for {filename}: {e}")
    return None


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "status": "error",
        "message": "Method not allowed",
        "code": 405
    }), 405


async def process_pdf_file(file):
    if not file or not file.filename:
        raise ValueError("No file selected")

    if not allowed_file(file.filename):
        raise ValueError("Invalid file type. Only PDF files are allowed")

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        # Process the PDF
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


@app.route('/api/books/upload', methods=['POST'])
async def upload_pdfs():
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
            except ValueError as e:
                errors.append({"filename": file.filename, "error": str(e)})
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": f"Processing failed: {str(e)}"
                })

        if not processed_files:
            return jsonify({
                "status": "error",
                "message": "All files failed to process",
                "errors": errors,
                "code": 400
            }), 400

        response_data = {
            "status": "success",
            "message": f"{len(processed_files)} files uploaded",
            "books": processed_files
        }
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
    try:
        books = []
        for metadata_file in os.listdir(METADATA_FOLDER):
            if metadata_file.endswith('.json'):
                metadata = load_metadata(os.path.splitext(metadata_file)[0])
                if metadata:
                    books.append(metadata)
        return jsonify({"status": "success", "books": books})
    except Exception as e:
        app.logger.error(f"Error retrieving books: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@app.route('/api/books/<filename>')
def get_book(filename):
    try:
        metadata = load_metadata(filename)
        if not metadata:
            return jsonify({
                "status": "error",
                "message": "Book not found",
                "code": 404
            }), 404
        return jsonify(metadata)
    except Exception as e:
        app.logger.error(f"Error retrieving book metadata for {filename}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@app.route('/api/books/<filename>/sections/<section_id>')
def get_book_section(filename, section_id):
    try:
        section_path = os.path.join(SECTIONS_FOLDER, filename,
                                    f"{section_id}.txt")
        if not os.path.exists(section_path):
            return jsonify({
                "status": "error",
                "message": "Section not found",
                "code": 404
            }), 404

        with open(section_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            "status": "success",
            "section": {
                "id": section_id,
                "content": content
            }
        })
    except Exception as e:
        app.logger.error(
            f"Error getting book section {section_id} for {filename}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@app.route('/api/books/<filename>/cover')
def get_book_cover(filename):
    try:
        # Récupérer la première page du PDF comme couverture
        pdf_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(pdf_path):
            return jsonify({
                "status": "error",
                "message": "PDF not found",
                "code": 404
            }), 404

        # Utiliser MuPDF pour extraire la première page
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        # Convertir en PNG
        img_data = pix.tobytes("png")

        from flask import send_file
        return send_file(io.BytesIO(img_data),
                         mimetype='image/png',
                         download_name=f"{filename}_cover.png")
    except Exception as e:
        app.logger.error(f"Error getting book cover for {filename}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500


@sock.route('/api/ws/books')
def books_websocket(ws):
    try:
        while True:
            data = ws.receive()
            # Handle incoming messages if needed
    except Exception as e:
        app.logger.error(f"WebSocket error: {e}")


# Handle 404 errors for API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue_app(path):
    if path.startswith('api/'):
        return jsonify({"error": "Not found", "code": 404}), 404

    try:
        # Serve static files from the dist directory
        if path and os.path.exists(os.path.join('vue-frontend/dist', path)):
            return send_from_directory('vue-frontend/dist', path)
        # Default to index.html for client-side routing
        return send_from_directory('vue-frontend/dist', 'index.html')
    except Exception as e:
        app.logger.error(f"Error serving Vue app: {e}")
        return jsonify({"error": "Internal server error", "code": 500}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
