from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import mimetypes
from pathlib import Path
from replit import db
import json
from werkzeug.utils import secure_filename
from datetime import datetime

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

# Removed unused code related to object storage

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
        
        # Create basic metadata
        metadata = {
            "title": os.path.splitext(filename)[0],
            "author": "Unknown",
            "pages": 0,  # We'll update this later if needed
            "filename": filename,
            "id": filename,  # Using filename as ID for now
            "uploadDate": datetime.now().isoformat()
        }
        
        # Save file locally
        file.save(file_path)
        
        # Store metadata in database
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

@app.route('/')
def serve_index():
    try:
        return send_from_directory('frontend/dist', 'index.html')
    except Exception as e:
        print(f"Error serving index: {e}")
        return str(e), 500

@app.route('/<path:path>')
def serve_static(path):
    try:
        if os.path.exists(os.path.join('frontend/dist', path)):
            return send_from_directory('frontend/dist', path)
        return send_from_directory('frontend/dist', 'index.html')
    except Exception as e:
        print(f"Error serving static file: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)