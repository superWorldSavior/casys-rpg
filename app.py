from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import mimetypes
from pathlib import Path
from replit import db

# Add proper MIME type for JavaScript modules
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)

def get_chapters_from_db():
    try:
        # Get all keys that start with 'chapter_'
        chapter_keys = [k for k in db.prefix("") if k.startswith('chapter_')]
        # Sort keys to maintain order
        chapter_keys.sort()
        # Get content for each chapter
        chapters = [db[key] for key in chapter_keys]
        return chapters
    except Exception as e:
        print(f"Error reading from database: {e}")
        return []

@app.route('/api/text')
def get_text():
    try:
        chapter_sections = get_chapters_from_db()
        if not chapter_sections:
            # Fallback content in case of empty database
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

@app.route('/api/content', methods=['POST'])
def update_content():
    try:
        content = request.json
        if not content or 'sections' not in content:
            return jsonify({"error": "Invalid content format"}), 400
        
        # Clear existing content
        keys = db.prefix("")
        for key in keys:
            if key.startswith('chapter_'):
                del db[key]
        
        # Store new content
        for idx, section in enumerate(content['sections']):
            key = f'chapter_{idx:03d}'
            db[key] = section
        
        return jsonify({"message": "Content updated successfully"})
    except Exception as e:
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
