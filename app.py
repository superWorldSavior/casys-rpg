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

# Add proper MIME type for JavaScript modules
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# Add supported file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf'}

# Configure folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
SECTIONS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sections')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SECTIONS_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_file_exists(filename):
    # Only check if sections exist in the SECTIONS_FOLDER
    base_name = os.path.splitext(filename)[0]
    section_path = os.path.join(SECTIONS_FOLDER, f"{base_name}_section_1.txt")
    sections_exist = os.path.exists(section_path)
    
    # Return tuple of existence status and status message
    return sections_exist, "available" if sections_exist else "sections_missing"

def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        text_content = []
        for page in doc:
            text = page.get_text()
            if text.strip():  # Only add non-empty pages
                text_content.append(text)
        doc.close()
        
        # Create sections for the extracted content
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        section_path = os.path.join(SECTIONS_FOLDER, f"{base_name}_section_1.txt")
        
        # Save first section (we can implement more sophisticated sectioning later)
        with open(section_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_content))
            
        return text_content, True
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return [], False

@app.route('/api/books')
def get_books():
    try:
        # First get list of available sections
        available_sections = set()
        for file in os.listdir(SECTIONS_FOLDER):
            if file.endswith('_section_1.txt'):
                book_name = file.replace('_section_1.txt', '.pdf')
                available_sections.add(book_name)
        
        books = []
        # Only process books that have sections
        for key in db.prefix("pdf_"):
            metadata = json.loads(db[key])
            filename = metadata.get('filename')
            if filename and filename in available_sections:
                metadata['available'] = True
                metadata['processing_status'] = 'available'
                db[key] = json.dumps(metadata)
                books.append(metadata)
            
        return jsonify(books)
    except Exception as e:
        print(f"Error getting books: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({"error": "No PDF file provided"}), 400
            
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file locally
        file.save(file_path)
        
        # Extract text content from PDF and create sections
        text_content, processing_success = extract_text_from_pdf(file_path)
        
        # Verify sections exist
        is_available, status = verify_file_exists(filename)
        
        # Create metadata
        metadata = {
            "title": os.path.splitext(filename)[0],
            "author": "Unknown",
            "pages": len(text_content),
            "filename": filename,
            "id": filename,
            "uploadDate": datetime.now().isoformat(),
            "processing_status": status,
            "available": is_available
        }
        
        # Store metadata and content in database
        db[f"pdf_{filename}"] = json.dumps(metadata)
        if processing_success:
            db[f"content_{filename}"] = json.dumps(text_content)
        
        return jsonify({
            "message": "PDF uploaded and processed successfully" if is_available else f"PDF processing incomplete: {status}",
            "metadata": metadata
        })
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
        
        # Verify sections exist
        is_available, status = verify_file_exists(filename)
        
        # Update metadata if availability has changed
        if metadata.get('available', False) != is_available or metadata.get('processing_status') != status:
            metadata['available'] = is_available
            metadata['processing_status'] = status
            db[metadata_key] = json.dumps(metadata)
        
        if not is_available:
            return jsonify({"error": f"Book is not available: {status}"}), 403
            
        return send_from_directory(UPLOAD_FOLDER, filename)
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
        
        # Verify sections exist
        is_available, status = verify_file_exists(filename)
        
        # Update metadata if availability has changed
        if metadata.get('available', False) != is_available or metadata.get('processing_status') != status:
            metadata['available'] = is_available
            metadata['processing_status'] = status
            db[metadata_key] = json.dumps(metadata)
            
        if not is_available:
            return jsonify({"error": f"Book is not available: {status}"}), 403
            
        content_key = f"content_{filename}"
        if content_key in db:
            content = json.loads(db[content_key])
            return jsonify(content)
        return jsonify({"error": "Book content not found"}), 404
    except Exception as e:
        print(f"Error getting book content: {e}")
        return jsonify({"error": str(e)}), 500

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'):
        return jsonify({"error": "Not found"}), 404
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
