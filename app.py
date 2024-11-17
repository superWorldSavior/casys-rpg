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

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def allowed_file(filename: str) -> bool:
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    
    # Process the PDF
    await pdf_service.process_pdf(file_path)
    
    metadata = {
        "title": os.path.splitext(filename)[0],
        "author": "Unknown",
        "filename": filename,
        "id": filename,
        "uploadDate": datetime.now().isoformat(),
        "status": "processing",
        "current_page": 0,
        "total_pages": 0,
        "processed_sections": 0,
        "processed_images": 0,
        "error_message": None
    }
    
    db[f"pdf_{filename}"] = json.dumps(metadata)
    return metadata

@app.route('/api/books/upload', methods=['POST'])
async def upload_pdfs():
    try:
        if 'pdf_files' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No PDF files provided",
                "code": 400
            }), 400

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
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
            except Exception as e:
                errors.append({
                    "filename": file.filename,
                    "error": f"Processing failed: {str(e)}"
                })

        if not processed_files and errors:
            return jsonify({
                "status": "error",
                "message": "All files failed to process",
                "errors": errors,
                "code": 400
            }), 400

        response_data = {
            "status": "success",
            "message": f"{len(processed_files)} files uploaded and processing started",
            "books": processed_files
        }
        
        if errors:
            response_data["errors"] = errors
            
        return jsonify(response_data)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500

@app.route('/api/books')
def get_books():
    try:
        books = []
        for key in db.prefix("pdf_"):
            try:
                metadata = json.loads(db[key])
                base_name = os.path.splitext(metadata.get('filename', ''))[0]
                progress_file = os.path.join(SECTIONS_FOLDER, base_name, 'metadata', 'progress.json')
                
                # Include all books with progress.json and add their progress data
                if os.path.exists(progress_file):
                    with open(progress_file, 'r') as f:
                        progress_data = json.load(f)
                        # Update metadata with all progress fields
                        metadata.update({
                            'status': progress_data.get('status', 'processing'),
                            'current_page': progress_data.get('current_page', 0),
                            'total_pages': progress_data.get('total_pages', 0),
                            'processed_sections': progress_data.get('processed_sections', 0),
                            'processed_images': progress_data.get('processed_images', 0),
                            'error_message': progress_data.get('error_message')
                        })
                        books.append(metadata)
            except Exception as e:
                continue
        
        return jsonify({
            "status": "success",
            "books": books
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500

@app.route('/api/books/<filename>')
def get_book(filename):
    try:
        metadata_key = f"pdf_{filename}"
        if metadata_key not in db:
            return jsonify({
                "status": "error",
                "message": "Book not found",
                "code": 404
            }), 404
            
        metadata = json.loads(db[metadata_key])
        base_name = os.path.splitext(filename)[0]
        progress_file = os.path.join(SECTIONS_FOLDER, base_name, 'metadata', 'progress.json')
        
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
                if progress_data.get('status') != 'completed':
                    return jsonify({
                        "status": "error",
                        "message": "Book is not ready for reading",
                        "code": 403
                    }), 403
                    
        return send_from_directory(str(UPLOAD_FOLDER), filename)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 404
        }), 404

@app.route('/api/books/<filename>/content')
def get_book_content(filename):
    try:
        metadata_key = f"pdf_{filename}"
        if metadata_key not in db:
            return jsonify({
                "status": "error",
                "message": "Book not found",
                "code": 404
            }), 404
        
        base_name = os.path.splitext(filename)[0]
        sections_folder = os.path.join(SECTIONS_FOLDER, base_name)
        
        if not os.path.exists(sections_folder):
            return jsonify({
                "status": "error",
                "message": "Book content not found",
                "code": 404
            }), 404
            
        sections = []
        section_files = sorted([f for f in os.listdir(sections_folder) if f.endswith('.md')])
        for section_file in section_files:
            with open(os.path.join(sections_folder, section_file), 'r', encoding='utf-8') as f:
                sections.append(f.read())
                
        return jsonify({
            "status": "success",
            "sections": sections
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "code": 500
        }), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'):
        return jsonify({
            "status": "error",
            "message": "Not found",
            "code": 404
        }), 404
    static_folder = str(app.static_folder) if app.static_folder else ''
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
