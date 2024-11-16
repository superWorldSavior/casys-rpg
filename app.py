from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import mimetypes
from pathlib import Path
from replit import db
import json
from werkzeug.utils import secure_filename
from datetime import datetime
import fitz  # PyMuPDF
from pdf_processing.application.pdf_service import PDFService
from pdf_processing.infrastructure.pdf_processor import MuPDFProcessor
from pdf_processing.infrastructure.pdf_repository import FileSystemPDFRepository

# Add proper MIME type for JavaScript modules
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# Add supported file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf'}

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)

# Initialize PDF processing services
pdf_processor = MuPDFProcessor()
pdf_repository = FileSystemPDFRepository()
pdf_service = PDFService(pdf_processor, pdf_repository)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload-pdf', methods=['POST'])
async def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
            
        file = request.files['pdf']
        if not file or not file.filename:
            return jsonify({"error": "No selected file"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file locally
        file.save(file_path)
        
        # Process PDF using our enhanced service
        processed_pdf = await pdf_service.process_pdf(file_path, "sections")
        
        if processed_pdf.metadata:
            # Create enhanced metadata
            metadata = {
                "title": processed_pdf.metadata.title or os.path.splitext(filename)[0],
                "author": processed_pdf.metadata.author or "Unknown",
                "subject": processed_pdf.metadata.subject,
                "keywords": processed_pdf.metadata.keywords,
                "creator": processed_pdf.metadata.creator,
                "producer": processed_pdf.metadata.producer,
                "creation_date": processed_pdf.metadata.creation_date.isoformat() if processed_pdf.metadata.creation_date else None,
                "modification_date": processed_pdf.metadata.modification_date.isoformat() if processed_pdf.metadata.modification_date else None,
                "pages": processed_pdf.metadata.page_count,
                "file_size": processed_pdf.metadata.file_size,
                "pdf_version": processed_pdf.metadata.pdf_version,
                "is_encrypted": processed_pdf.metadata.is_encrypted,
                "page_dimensions": processed_pdf.metadata.page_dimensions,
                "filename": filename,
                "id": filename,
                "uploadDate": datetime.now().isoformat(),
                "sections_count": len(processed_pdf.sections),
                "images_count": len(processed_pdf.images)
            }
        else:
            metadata = {
                "title": os.path.splitext(filename)[0],
                "author": "Unknown",
                "pages": 0,
                "filename": filename,
                "id": filename,
                "uploadDate": datetime.now().isoformat()
            }
        
        # Store metadata and content in database
        db[f"pdf_{filename}"] = json.dumps(metadata)
        
        return jsonify({
            "message": "PDF uploaded successfully",
            "metadata": metadata
        })
    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/<filename>')
def get_book(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/books/<filename>/content')
def get_book_content(filename):
    try:
        pdf_folder_name = os.path.splitext(filename)[0]
        metadata_path = os.path.join('sections', pdf_folder_name, 'section_metadata.json')
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            return jsonify(content)
        return jsonify({"error": "Book content not found"}), 404
    except Exception as e:
        print(f"Error getting book content: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/books')
def get_books():
    try:
        books = []
        for key in db.prefix("pdf_"):
            metadata = json.loads(db[key])
            books.append(metadata)
        return jsonify(books)
    except Exception as e:
        print(f"Error getting books: {e}")
        return jsonify({"error": str(e)}), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder = str(app.static_folder) if app.static_folder else ''
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
