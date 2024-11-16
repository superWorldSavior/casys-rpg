from flask import Flask, render_template, jsonify, send_from_directory
import os
import mimetypes

# Add proper MIME type for JavaScript modules
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = Flask(__name__, static_folder='frontend/dist')

@app.route('/api/text')
def get_text():
    # Sample text content - in production this could come from a database
    sample_text = [
        "Welcome to the interactive text reader.",
        "This is a progressive text display system.",
        "You can control the speed and navigation.",
        "Try using the spacebar to pause/resume.",
        "Type 'commencer' in the command box to begin."
    ]
    return jsonify(sample_text)

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
