from flask import Flask, render_template, jsonify, send_from_directory
import os
import mimetypes
import markdown
from pathlib import Path

# Add proper MIME type for JavaScript modules
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = Flask(__name__, static_folder='frontend/dist')

def read_markdown_files():
    content_dir = Path('content')
    chapters = []
    
    # Read and parse each markdown file
    for chapter_file in sorted(content_dir.glob('*.md')):
        with open(chapter_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
            # Convert markdown to HTML
            html_content = markdown.markdown(md_content)
            # Split content by headers to create sections
            sections = html_content.split('<h2>')
            # Process each section
            for section in sections[1:]:  # Skip the first split if it's empty
                # Reconstruct the h2 tag and clean up the section
                clean_section = f'<h2>{section}'.strip()
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
            "Welcome to the interactive text reader.",
            "This is a progressive text display system.",
            "You can control the speed and navigation.",
            "Try using the spacebar to pause/resume.",
            "Type 'commencer' in the command box to begin."
        ])

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')
