from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import mimetypes
from pathlib import Path
from replit import db
from replit.object_storage import Client
import json
from werkzeug.utils import secure_filename
from datetime import datetime

# Add proper MIME type for JavaScript modules
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# Add supported file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf'}

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)

# Initialize Object Storage
client = Client()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_chapters_from_storage():
    try:
        chapters = []
        # List all markdown files
        files = [f for f in client.list_objects() if isinstance(f, str) and f.endswith('.md') and not f.endswith('_v.md')]
        if not files:
            return []
            
        # Sort files by chapter number
        files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        
        for file in files:
            content = client.get_object(file).decode('utf-8')  # Assuming the method is actually available in the client's interface
            chapters.append(content)
        return chapters
    except Exception as e:
        print(f"Error reading from object storage: {e}")
        return get_chapters_from_db()

def get_chapters_from_db():
    try:
        chapter_keys = [k for k in db.prefix("") if k.startswith('chapter_')]
        chapter_keys.sort()
        chapters = [db[key] for key in chapter_keys]
        return chapters
    except Exception as e:
        print(f"Error reading from database: {e}")
        return []

def get_chapter_versions(chapter_id):
    try:
        base_name = f"{chapter_id}.md"
        versions = []
        
        # Get all versions for this chapter
        all_files = client.list_objects()
        version_files = [f for f in all_files if isinstance(f, str) and f.startswith(f"{chapter_id}_v") and f.endswith('.md')]
        
        # Get base version
        if base_name in all_files:
            versions.append({
                'version': '1',
                'timestamp': datetime.now().isoformat(),
                'key': base_name
            })
        
        # Add all other versions
        for vfile in sorted(version_files, key=lambda x: int(x.split('_v')[1].split('.')[0]) if isinstance(x, str) else 0):
            version_num = vfile.split('_v')[1].split('.')[0] if isinstance(vfile, str) else '0'
            versions.append({
                'version': version_num,
                'timestamp': datetime.now().isoformat(),
                'key': vfile
            })
            
        return versions
    except Exception as e:
        print(f"Error getting chapter versions: {e}")
        return []

@app.route('/api/text')
def get_text():
    try:
        chapter_sections = get_chapters_from_storage()
        if not chapter_sections:
            return jsonify([
                "# Welcome\n\nWelcome to the interactive text reader.",
                "## Getting Started\n\nThis is a progressive text display system.",
                "## Navigation\n\nYou can control the speed and navigation.",
                "## Controls\n\nTry using the spacebar to pause/resume.",
                "## Start\n\nType 'commencer' in the command box to begin."
            ])
        return jsonify(chapter_sections)
    except Exception as e:
        print(f"Error retrieving text: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/versions/<chapter_id>')
def get_versions(chapter_id):
    try:
        versions = get_chapter_versions(chapter_id)
        return jsonify(versions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/<chapter_id>/version/<version>')
def get_specific_version(chapter_id, version):
    try:
        if version == '1':
            key = f"{chapter_id}.md"
        else:
            key = f"{chapter_id}_v{version}.md"
        content = client.get_object(key).decode('utf-8')  # Assuming the method is actually available in the client's interface
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/content', methods=['POST'])
def update_content():
    try:
        content = request.json
        if not content or 'sections' not in content:
            return jsonify({"error": "Invalid content format"}), 400
        
        # Store content with versioning
        for idx, section in enumerate(content['sections']):
            chapter_id = f'chapter_{idx:03d}'
            base_name = f"{chapter_id}.md"
            
            # Get existing versions
            versions = get_chapter_versions(chapter_id)
            new_version = str(len(versions) + 1)
            
            # Store new version
            version_key = f"{chapter_id}_v{new_version}.md"
            client.upload_from_text(
                version_key,
                section
            )
            
            # Update current version
            client.upload_from_text(
                base_name,
                section
            )
        
        return jsonify({"message": "Content updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/<path:filename>')
def get_image(filename):
    try:
        image_data = client.get_object(f"images/{filename}")  # Assuming the method is actually available in the client's interface
        
        temp_dir = Path('temp_images')
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / filename
        
        with open(temp_path, 'wb') as f:
            f.write(image_data)
        
        return send_from_directory('temp_images', filename)
    except Exception as e:
        print(f"Error retrieving image: {e}")
        return jsonify({"error": str(e)}), 404

@app.route('/api/images', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
            
        filename = secure_filename(file.filename)
        
        client.upload_bytes(
            f"images/{filename}",
            file.read()
        )
        
        return jsonify({
            "message": "Image uploaded successfully",
            "url": f"/api/images/{filename}"
        })
    except Exception as e:
        print(f"Error uploading image: {e}")
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
        
        # Create basic metadata without PyMuPDF
        metadata = {
            "title": os.path.splitext(filename)[0],
            "author": "Unknown",
            "pages": 0,  # We'll update this later if needed
            "filename": filename,
            "id": filename,  # Using filename as ID for now
            "uploadDate": datetime.now().isoformat()
        }
        
        # Upload PDF to object storage
        file_content = file.read()
        client.upload_bytes(
            f"pdfs/{filename}",
            file_content
        )
        
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
        pdf_data = client.get_bytes(f"pdfs/{filename}")
        return pdf_data, 200, {'Content-Type': 'application/pdf'}
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