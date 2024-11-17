from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import mimetypes
import traceback
from pathlib import Path
from replit import db
import json
from werkzeug.utils import secure_filename
from datetime import datetime
from pdf_processing.infrastructure.pdf_processor import MuPDFProcessor
from pdf_processing.infrastructure.pdf_repository import FileSystemPDFRepository
from pdf_processing.application.pdf_service import PDFService

# Add proper MIME type for JavaScript modules
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# Add supported file types
ALLOWED_EXTENSIONS = {'pdf'}

# Configure folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
SECTIONS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sections')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SECTIONS_FOLDER, exist_ok=True)

# Initialize PDF processing components
pdf_processor = MuPDFProcessor()
pdf_repository = FileSystemPDFRepository()
pdf_service = PDFService(pdf_processor, pdf_repository)

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)

def allowed_file(filename: str) -> bool:
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.route('/api/books')
def get_books():
    try:
        print("Request received at /api/books")
        books = []
        for key in db.prefix("pdf_"):
            try:
                metadata = json.loads(db[key])
                base_name = os.path.splitext(metadata.get('filename', ''))[0]
                progress_file = os.path.join(SECTIONS_FOLDER, base_name, 'metadata', 'progress.json')
                
                if os.path.exists(progress_file):
                    with open(progress_file, 'r') as f:
                        progress_data = json.load(f)
                        if progress_data.get('status') == 'completed':
                            metadata['available'] = True
                            books.append(metadata)
            except Exception as e:
                print(f"Error processing book {key}: {str(e)}")
                continue
        return jsonify(books)
    except Exception as e:
        print(f"Error getting books: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-pdf', methods=['POST'])
async def upload_pdf():
    try:
        print("Request received at /api/upload-pdf")
        print(f"Request method: {request.method}")
        print(f"Request files: {request.files}")
        
        if 'pdf' not in request.files:
            print("No 'pdf' in request.files")
            return jsonify({"error": "No PDF file provided"}), 400

        file = request.files['pdf']
        if not file or not file.filename:
            print("No selected file or empty filename")
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            print(f"Invalid file type: {file.filename}")
            return jsonify({"error": "Invalid file type. Only PDF files are allowed"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        print(f"Saving file to: {file_path}")
        file.save(file_path)
        
        try:
            print(f"Processing file: {filename}")
            await pdf_service.process_pdf(file_path)
            
            metadata = {
                "title": os.path.splitext(filename)[0],
                "author": "Unknown",
                "filename": filename,
                "id": filename,
                "uploadDate": datetime.now().isoformat(),
                "processing_status": "processing",
                "available": False
            }
            
            db[f"pdf_{filename}"] = json.dumps(metadata)
            print(f"Successfully processed {filename}")
            
            return jsonify({
                "message": "PDF uploaded and processing started",
                "file": metadata
            })
            
        except Exception as processing_error:
            print(f"Error processing {filename}: {str(processing_error)}")
            print(f"Error type: {type(processing_error)}")
            print(f"Error traceback: {traceback.format_exc()}")
            metadata = {
                "title": os.path.splitext(filename)[0],
                "author": "Unknown",
                "filename": filename,
                "id": filename,
                "uploadDate": datetime.now().isoformat(),
                "processing_status": "failed",
                "available": False,
                "error": str(processing_error)
            }
            db[f"pdf_{filename}"] = json.dumps(metadata)
            return jsonify({
                "error": f"Error processing file: {str(processing_error)}",
                "file": metadata
            }), 500
            
    except Exception as e:
        print(f"Error in upload_pdf: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/<filename>')
def get_book(filename):
    try:
        print(f"Request received for book: {filename}")
        metadata_key = f"pdf_{filename}"
        if metadata_key not in db:
            print(f"Book not found: {filename}")
            return jsonify({"error": "Book not found"}), 404
            
        metadata = json.loads(db[metadata_key])
        if not metadata.get('available', False):
            print(f"Book not available: {filename}")
            return jsonify({"error": "Book is not available for reading"}), 403
            
        return send_from_directory(str(UPLOAD_FOLDER), filename)
    except Exception as e:
        print(f"Error getting book: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 404

@app.route('/api/books/<filename>/content')
def get_book_content(filename):
    try:
        print(f"Request received for book content: {filename}")
        metadata_key = f"pdf_{filename}"
        if metadata_key not in db:
            print(f"Book content not found: {filename}")
            return jsonify({"error": "Book not found"}), 404
            
        metadata = json.loads(db[metadata_key])
        if not metadata.get('available', False):
            print(f"Book content not available: {filename}")
            return jsonify({"error": "Book is not available for reading"}), 403
        
        base_name = os.path.splitext(filename)[0]
        sections_folder = os.path.join(SECTIONS_FOLDER, base_name)
        
        if not os.path.exists(sections_folder):
            print(f"Sections folder not found: {sections_folder}")
            return jsonify({"error": "Book content not found"}), 404
            
        sections = []
        section_files = sorted([f for f in os.listdir(sections_folder) if f.endswith('.md')])
        print(f"Found {len(section_files)} sections")
        for section_file in section_files:
            with open(os.path.join(sections_folder, section_file), 'r', encoding='utf-8') as f:
                sections.append(f.read())
                
        return jsonify(sections)
    except Exception as e:
        print(f"Error getting book content: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
    static_folder = str(app.static_folder) if app.static_folder else ''
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
