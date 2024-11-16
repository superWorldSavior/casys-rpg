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

# Add supported image types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)

# Initialize Object Storage
client = Client()
BUCKET_ID = os.environ.get('REPLIT_BUCKET_ID', 'replit-objstore-f05f56c7-9da7-4fbe-8b1f-ec80f5185697')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_chapters_from_storage():
    try:
        chapters = []
        # List all chapter files
        files = [f for f in client.list(BUCKET_ID) if f.key.startswith("chapter_")]
        if not files:
            return []
            
        # Sort files by chapter index
        files.sort(key=lambda x: int(x.metadata.get('index', 0)))
        
        for file in files:
            content = client.download_as_text(BUCKET_ID, file.key)
            chapters.append(json.loads(content))
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
        # List all versions for a specific chapter
        files = [f for f in client.list(BUCKET_ID) 
                if f.key.startswith(f"{chapter_id}_v")]
        
        if not files:
            return []
        
        versions = []
        for file in files:
            version_info = {
                'version': file.metadata.get('version', '1'),
                'timestamp': file.metadata.get('timestamp'),
                'key': file.key
            }
            versions.append(version_info)
        
        # Sort by version number
        versions.sort(key=lambda x: int(x['version']))
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
        key = f"{chapter_id}_v{version}"
        content = client.download_as_text(BUCKET_ID, key)
        return jsonify(json.loads(content))
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
            
            # Get existing versions
            versions = get_chapter_versions(chapter_id)
            new_version = str(len(versions) + 1)
            timestamp = datetime.utcnow().isoformat()
            
            # Store new version
            version_key = f"{chapter_id}_v{new_version}"
            client.upload_from_text(
                BUCKET_ID,
                version_key,
                json.dumps(section),
                metadata={
                    'index': str(idx),
                    'version': new_version,
                    'timestamp': timestamp
                }
            )
            
            # Update current version
            client.upload_from_text(
                BUCKET_ID,
                chapter_id,
                json.dumps(section),
                metadata={
                    'index': str(idx),
                    'current_version': new_version,
                    'timestamp': timestamp
                }
            )
        
        return jsonify({"message": "Content updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/images/<path:filename>')
def get_image(filename):
    try:
        image_data = client.download(BUCKET_ID, f"images/{filename}")
        
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
        
        client.upload(
            BUCKET_ID,
            f"images/{filename}",
            file.read(),
            metadata={'content-type': file.content_type}
        )
        
        return jsonify({
            "message": "Image uploaded successfully",
            "url": f"/api/images/{filename}"
        })
    except Exception as e:
        print(f"Error uploading image: {e}")
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
