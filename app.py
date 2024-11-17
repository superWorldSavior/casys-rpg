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
    print(f"Method not allowed error:")
    print(f"Path: {request.path}")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    return jsonify({"error": "Method not allowed"}), 405

async def process_pdf_file(file):
    print(f"Processing file: {file.filename}")
    if not file or not file.filename:
        print("No file or filename")
        raise ValueError("No file selected")
        
    if not allowed_file(file.filename):
        print(f"Invalid file type for file: {file.filename}")
        raise ValueError("Invalid file type")
        
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    print(f"Saving file to: {file_path}")
    file.save(file_path)
    
    # Process the PDF
    print(f"Starting PDF processing for: {filename}")
    await pdf_service.process_pdf(file_path)
    print(f"PDF processing completed for: {filename}")
    
    metadata = {
        "title": os.path.splitext(filename)[0],
        "author": "Unknown",
        "filename": filename,
        "id": filename,
        "uploadDate": datetime.now().isoformat(),
        "processing_status": "processing",
        "available": False
    }
    
    print(f"Saving metadata for: {filename}")
    db[f"pdf_{filename}"] = json.dumps(metadata)
    return metadata

@app.route('/api/upload', methods=['POST'])
async def upload_pdfs():
    print(f"Received upload request:")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Files in request: {list(request.files.keys()) if request.files else 'No files'}")
    
    try:
        if 'files' not in request.files:
            print("No 'files' in request.files")
            return jsonify({"error": "No PDF files provided"}), 400

        uploaded_files = request.files.getlist('files')
        print(f"Number of files received: {len(uploaded_files)}")
        
        if not uploaded_files:
            print("No files selected")
            return jsonify({"error": "No files selected"}), 400

        processed_files = []
        errors = []
        
        for file in uploaded_files:
            try:
                print(f"Processing file: {file.filename}")
                metadata = await process_pdf_file(file)
                processed_files.append(metadata)
                print(f"Successfully processed: {file.filename}")
            except ValueError as e:
                print(f"Validation error for {file.filename}: {str(e)}")
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
            except Exception as e:
                print(f"Processing error for {file.filename}: {str(e)}")
                print(f"Error traceback: {traceback.format_exc()}")
                errors.append({
                    "filename": file.filename,
                    "error": f"Processing failed: {str(e)}"
                })

        if not processed_files and errors:
            print("All files failed to process")
            return jsonify({
                "error": "All files failed to process",
                "details": errors
            }), 400

        response_data = {
            "message": f"{len(processed_files)} files uploaded and processing started",
            "files": processed_files
        }
        
        if errors:
            response_data["errors"] = errors
            
        print(f"Upload completed. Processed: {len(processed_files)}, Errors: {len(errors)}")
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in upload_pdfs: {str(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/books')
def get_books():
    try:
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
                continue
        
        return jsonify(books)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/books/<filename>')
def get_book(filename):
    try:
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
        metadata_key = f"pdf_{filename}"
        if metadata_key not in db:
            return jsonify({"error": "Book not found"}), 404
            
        metadata = json.loads(db[metadata_key])
        if not metadata.get('available', False):
            return jsonify({"error": "Book is not available for reading"}), 403
        
        base_name = os.path.splitext(filename)[0]
        sections_folder = os.path.join(SECTIONS_FOLDER, base_name)
        
        if not os.path.exists(sections_folder):
            return jsonify({"error": "Book content not found"}), 404
            
        sections = []
        section_files = sorted([f for f in os.listdir(sections_folder) if f.endswith('.md')])
        for section_file in section_files:
            with open(os.path.join(sections_folder, section_file), 'r', encoding='utf-8') as f:
                sections.append(f.read())
                
        return jsonify(sections)
    except Exception as e:
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
