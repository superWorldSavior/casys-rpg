from flask import Flask, render_template, jsonify, send_from_directory
import os
import mimetypes
from pathlib import Path

# Add proper MIME type for JavaScript modules
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = Flask(__name__, static_folder='frontend/dist')

def read_markdown_files():
    content_dir = Path('content')
    chapters = []
    
    # Read each markdown file
    for chapter_file in sorted(content_dir.glob('*.md')):
        with open(chapter_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
            # Split content by headers using markdown syntax
            sections = md_content.split('\n## ')
            
            # Process first section (if it exists)
            if sections[0].startswith('# '):
                first_content = sections[0].split('\n', 1)[1] if '\n' in sections[0] else ''
                if first_content.strip():
                    chapters.append(first_content.strip())
            
            # Process remaining sections
            for section in sections[1:]:
                if section.strip():
                    # Reconstruct the section with its header
                    clean_section = f'## {section.strip()}'
                    chapters.append(clean_section)
    
    return chapters

@app.route('/api/text')
def get_text():
    try:
        chapter_sections = read_markdown_files()
        return jsonify(chapter_sections)
    except Exception as e:
        print(f"Error reading markdown files: {e}")
        # Fallback content in case of error
        return jsonify([
            "# Welcome\n\nWelcome to the interactive text reader.",
            "## Getting Started\n\nThis is a progressive text display system.",
            "## Navigation\n\nYou can control the speed and navigation.",
            "## Controls\n\nTry using the spacebar to pause/resume.",
            "## Start\n\nType 'commencer' in the command box to begin."
        ])

@app.route('/')
def serve_index():
    if app.static_folder:
        return send_from_directory(app.static_folder, 'index.html')
    return "Error: Static folder not configured", 500

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    if app.static_folder:
        assets_dir = os.path.join(app.static_folder, 'assets')
        if isinstance(assets_dir, str):
            return send_from_directory(assets_dir, filename)
    return "Error: Static folder not configured", 500

@app.route('/<path:path>')
def serve_static(path):
    if app.static_folder:
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    return "Error: Static folder not configured", 500
