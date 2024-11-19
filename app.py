from flask import Flask, render_template, jsonify, send_from_directory, request, g
from flask_cors import CORS
import os
import mimetypes
import traceback
from pathlib import Path
from replit import db
import json
import logging
from werkzeug.utils import secure_filename
from datetime import datetime
from pdf_processing.infrastructure.container import Container
from pdf_processing.application.services.pdf_service import PDFService, PDFProcessingError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def create_app():
    """Application factory function."""
    app = Flask(__name__, static_folder='frontend/dist')
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Initialize container and store PDFService
    try:
        container = Container.get_instance()
        app.pdf_service = container.resolve(PDFService)
        logger.info("Successfully initialized container and resolved PDFService")
    except Exception as e:
        logger.error(f"Failed to initialize container: {str(e)}", exc_info=True)
        raise
    
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        if not filename:
            return False
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def find_cover_image(book_folder: str) -> str:
        """Find the first image in the book's images folder to use as cover."""
        images_folder = os.path.join(book_folder, 'images')
        if os.path.exists(images_folder):
            image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if image_files:
                return f'/sections/{os.path.basename(book_folder)}/images/{image_files[0]}'
        return None

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "status": "error",
            "message": "Method not allowed",
            "code": 405
        }), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error("Internal server error occurred", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "code": 500
        }), 500

    async def process_pdf_file(file):
        if not file or not file.filename:
            raise ValueError("No file selected")
            
        if not allowed_file(file.filename):
            raise ValueError("Invalid file type. Only PDF files are allowed")
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        try:
            # Process the PDF using the injected service
            processed_pdf = await app.pdf_service.process_pdf(file_path)
            
            metadata = {
                "title": os.path.splitext(filename)[0],
                "author": "Unknown",
                "filename": filename,
                "id": filename,
                "uploadDate": datetime.now().isoformat(),
                "status": processed_pdf.progress.status.value,
                "current_page": processed_pdf.progress.current_page,
                "total_pages": processed_pdf.progress.total_pages,
                "processed_sections": len(processed_pdf.sections),
                "processed_images": len(processed_pdf.images),
                "error_message": processed_pdf.progress.error_message,
                "cover_image": None
            }
            
            db[f"pdf_{filename}"] = json.dumps(metadata)
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing PDF file {filename}: {str(e)}", exc_info=True)
            raise

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
            logger.error(f"Error in upload_pdfs: {str(e)}", exc_info=True)
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
                    book_folder = os.path.join(SECTIONS_FOLDER, base_name)
                    metadata_dir = os.path.join(book_folder, 'metadata')
                    progress_file = os.path.join(metadata_dir, 'processing.json')
                    
                    if os.path.exists(progress_file):
                        with open(progress_file, 'r') as f:
                            progress_data = json.load(f)
                            metadata.update(progress_data)
                            metadata['cover_image'] = find_cover_image(book_folder)
                            books.append(metadata)
                except Exception as e:
                    logger.error(f"Error processing book metadata: {str(e)}", exc_info=True)
                    continue
            
            return jsonify({
                "status": "success",
                "books": books
            })
        except Exception as e:
            logger.error(f"Error in get_books: {str(e)}", exc_info=True)
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
            progress_file = os.path.join(SECTIONS_FOLDER, base_name, 'metadata', 'processing.json')
            
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
            logger.error(f"Error in get_book: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": str(e),
                "code": 404
            }), 404

    @app.route('/sections/<path:filename>')
    def serve_section_file(filename):
        """Serve files from the sections folder (including images)."""
        try:
            directory = os.path.dirname(filename)
            file = os.path.basename(filename)
            full_dir = os.path.join(SECTIONS_FOLDER, directory)
            return send_from_directory(full_dir, file)
        except Exception as e:
            logger.error(f"Error serving section file: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": str(e),
                "code": 404
            }), 404

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

    return app
