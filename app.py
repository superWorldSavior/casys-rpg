from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import mimetypes
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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route('/api/upload-pdf', methods=['POST'])
async def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
            
        file = request.files['pdf']
        if not file or file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not file or not allowed_file(file.filename or ''):
            return jsonify({"error": "File type not allowed"}), 400
            
        filename = secure_filename(file.filename or '')
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file locally
        file.save(file_path)
        
        try:
            # Process the PDF using PDFService
            processed_pdf = await pdf_service.process_pdf(file_path)
            
            # Create metadata
            metadata = {
                "title": os.path.splitext(filename)[0],
                "author": "Unknown",
                "pages": len(processed_pdf.sections),
                "filename": filename,
                "id": filename,
                "uploadDate": datetime.now().isoformat(),
                "processing_status": "available",
                "available": True,
                "sections": len(processed_pdf.sections),
                "images": len(processed_pdf.images)
            }
            
            # Store metadata in database
            db[f"pdf_{filename}"] = json.dumps(metadata)
            
            return jsonify({
                "message": "PDF uploaded and processed successfully",
                "metadata": metadata
            })
            
        except Exception as processing_error:
            print(f"Error processing PDF: {processing_error}")
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
                "error": "Failed to process PDF",
                "metadata": metadata
            }), 500
            
    except Exception as e:
        print(f"Error uploading PDF: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/<filename>')
def get_book(filename):
    try:
        # Check if book exists and is available
        metadata_key = f"pdf_{filename}"
        if metadata_key not in db:
            return jsonify({"error": "Book not found"}), 404
            
        metadata = json.loads(db[metadata_key])
        if not metadata.get('available', False):
            return jsonify({"error": "Book is not available for reading"}), 403
            
        return send_from_directory(str(UPLOAD_FOLDER), filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/books/<filename>/content')
def get_book_content(filename):
    try:
        # Check if book exists and is available
        metadata_key = f"pdf_{filename}"
        if metadata_key not in db:
            return jsonify({"error": "Book not found"}), 404
            
        metadata = json.loads(db[metadata_key])
        if not metadata.get('available', False):
            return jsonify({"error": "Book is not available for reading"}), 403
        
        # Get the book's base folder name
        base_name = os.path.splitext(filename)[0]
        sections_folder = os.path.join(SECTIONS_FOLDER, base_name)
        
        if not os.path.exists(sections_folder):
            return jsonify({"error": "Book content not found"}), 404
            
        # Read all sections
        sections = []
        section_files = sorted([f for f in os.listdir(sections_folder) if f.endswith('.md')])
        for section_file in section_files:
            with open(os.path.join(sections_folder, section_file), 'r', encoding='utf-8') as f:
                sections.append(f.read())
                
        return jsonify(sections)
    except Exception as e:
        print(f"Error getting book content: {e}")
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
