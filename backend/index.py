from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from process_book import book_main, lookup_summary, lookup_book_summary
from PIL import Image
from io import BytesIO
import zipfile
from lxml import etree
import os
import threading
import logging
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

BOOKS_DIR = 'static/epubs'
THUMBNAILS_DIR = 'static/thumbnails'
processing_status = {}


if not os.path.exists(BOOKS_DIR):
    os.makedirs(BOOKS_DIR)

if not os.path.exists(THUMBNAILS_DIR):
    os.makedirs(THUMBNAILS_DIR)

namespaces = {
    "calibre": "http://calibre.kovidgoyal.net/2009/metadata",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "opf": "http://www.idpf.org/2007/opf",
    "u": "urn:oasis:names:tc:opendocument:xmlns:container",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@app.route('/')
def hello():
    return '<p>Hello, new World!</p>'

def clean_book_name(name):
    """Converts file-based names to more readable titles by replacing hyphens and underscores with spaces and capitalizing each word."""
    return ' '.join(word.capitalize() for word in name.replace('_', ' ').replace('-', ' ').split())

def get_epub_cover(epub_path):
    with zipfile.ZipFile(epub_path) as z:
        t = etree.fromstring(z.read("META-INF/container.xml"))
        rootfile_path = t.xpath("/u:container/u:rootfiles/u:rootfile", namespaces=namespaces)[0].get("full-path")
        t = etree.fromstring(z.read(rootfile_path))
        cover_id = t.xpath("//opf:metadata/opf:meta[@name='cover']", namespaces=namespaces)[0].get("content")
        cover_href = t.xpath("//opf:manifest/opf:item[@id='" + cover_id + "']", namespaces=namespaces)[0].get("href")
        cover_path = os.path.join(os.path.dirname(rootfile_path), cover_href)
        return z.open(cover_path)

@app.route('/get-books')
def get_books():
    # List .epub files in the books directory
    book_files = [f for f in os.listdir(BOOKS_DIR) if f.endswith('.epub')]

    # Prepare the list of books with their epub paths and thumbnail URLs
    books = []
    for book_file in book_files:
        book_name = os.path.splitext(book_file)[0]
        epub_path = os.path.join(BOOKS_DIR, book_file)
        thumbnail_path = os.path.join(THUMBNAILS_DIR, book_name + '.jpg')

        # Check if the thumbnail file exists
        if os.path.exists(thumbnail_path):
            thumbnail_url = url_for('static', filename=os.path.join('thumbnails', book_name + '.jpg'))
        else:
            thumbnail_url = None  # or a URL to a default placeholder image

        books.append({
            "name": clean_book_name(book_name),
            "epub": url_for('static', filename=os.path.join('epubs', book_file)),
            "thumbnail": thumbnail_url
        })

    return jsonify(books)

# @app.route('/upload-epub', methods=['POST'])
# def upload_epub():
#     logging.info("Inside upload_epub")
#     if 'file' not in request.files:
#         return 'No epub file part', 400

#     file = request.files['file']

#     if file.filename == '':
#         return 'No selected file', 400

#     if file:
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(BOOKS_DIR, filename)
#         file.save(file_path)

#         try:
#             cover_image = get_epub_cover(file_path)
#             book_name = os.path.splitext(os.path.basename(file_path))[0]
#             cover_image_path = os.path.join(THUMBNAILS_DIR, book_name + '.jpg')
#             image = Image.open(cover_image)
#             image.save(cover_image_path, 'JPEG')
#         except Exception as e:
#             logging.warning("No cover image found for book: %s", book_name)

#         logging.info("Starting a new thread for processing the ePub file")
#         # thread = threading.Thread(target=book_main, args=(file_path,))
#         thread = threading.Thread(target=book_main, args=(file_path, socketio))
#         thread.start()

#         return jsonify({"message": "File upload initiated", "filename": filename})
    

@app.route('/upload-epub', methods=['POST'])
def upload_epub():
    logging.info("Inside new upload_epub")
    if 'file' not in request.files:
        return 'No epub file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(BOOKS_DIR, filename)
        file.save(file_path)

        return jsonify({"message": "File upload successful", "filename": filename})
    

@app.route('/process-epub', methods=['POST'])
def process_epub():
    logging.info("Inside process_epub")
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return 'No filename provided', 400

    file_path = os.path.join(BOOKS_DIR, filename)

    if not os.path.exists(file_path):
        return 'File not found', 404

    try:
        cover_image = get_epub_cover(file_path)
        book_name = os.path.splitext(os.path.basename(file_path))[0]
        cover_image_path = os.path.join(THUMBNAILS_DIR, book_name + '.jpg')
        image = Image.open(cover_image)
        image.save(cover_image_path, 'JPEG')
    except Exception as e:
        logging.warning("No cover image found for book: %s", book_name)

    logging.info("Starting a new thread for processing the ePub file")
    thread = threading.Thread(target=book_main, args=(file_path, socketio))
    thread.start()

    return jsonify({"message": "Book processing initiated", "filename": filename})



@app.route('/book-summary/<path:book_title>', methods=['GET'])
def book_summary(book_title):
    # Query the database for the summary
    logging.info("Inside book_summary, the requested book_title is %s", book_title)
    summary_document = lookup_book_summary(book_title)
    logging.info("summary_document is %s", summary_document)

    if summary_document:
        # Return the summary if found
        return jsonify({
            "status": "success",
            "book_summary": summary_document
        })
    else:
        # Handle case where no summary is found
        return jsonify({
            "status": "error",
            "message": "Summary not found for book: " + book_title
        }), 404

@app.route('/chapter-summary/<path:chapter_id>', methods=['GET'])
def get_summary(chapter_id):
    # Query the database for the summary
    summary_document = lookup_summary(chapter_id)

    if summary_document:
        # Return the summary if found
        return jsonify({
            "status": "success",
            "chapter_summary": summary_document
        })
    else:
        # Handle case where summary is pending
        return jsonify({
            "status": "pending",
            "message": "Summary is pending for chapter ID: " + chapter_id
        })
    

@app.route('/status-epub', methods=['GET'])
def status_epub():
    filename = request.args.get('filename')

    if not filename:
        return 'No filename provided', 400

    file_path = os.path.join(BOOKS_DIR, filename)

    if file_path not in processing_status:
        return 'File not found', 404

    return jsonify({"status": processing_status[file_path]})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
