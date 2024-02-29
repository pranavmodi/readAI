from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from process_book import book_main, lookup_summary, lookup_book_summary
import os
import threading
import logging


app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return '<p> Hello, new  World!</p> '

def clean_book_name(name):
    """Converts file-based names to more readable titles by replacing hyphens and underscores with spaces and capitalizing each word."""
    return ' '.join(word.capitalize() for word in name.replace('_', ' ').replace('-', ' ').split())



@app.route('/get-books')
def get_books():
    # Define directories for books and thumbnails
    books_dir = 'epubs'  # No need to include 'static/' here
    thumbnails_dir = 'thumbnails'  # No need to include 'static/' here

    # List .epub files in the books directory
    book_files = [f for f in os.listdir(os.path.join('static', books_dir)) if f.endswith('.epub')]

    # Prepare the list of books with their epub paths and thumbnail URLs
    books = []
    for book_file in book_files:
        book_name = os.path.splitext(book_file)[0]
        epub_path = os.path.join(books_dir, book_file)
        thumbnail_path = os.path.join(thumbnails_dir, book_name + '.jpg')

        # Check if the thumbnail file exists
        if os.path.exists(os.path.join('static', thumbnail_path)):
            thumbnail_url = url_for('static', filename=thumbnail_path)
        else:
            thumbnail_url = None  # or a URL to a default placeholder image

        books.append({
            "name": clean_book_name(book_name),
            "epub": url_for('static', filename=epub_path),
            "thumbnail": thumbnail_url
        })

    return jsonify(books)



@app.route('/upload-epub', methods=['POST'])
def upload_epub():
    logging.info("Inside upload_epub")
    if 'file' not in request.files:
        return 'No epub file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('.', filename)
        file.save(file_path)

        # Start a new thread for processing the ePub file
        logging.info("Starting a new thread for processing the ePub file")
        thread = threading.Thread(target=book_main, args=(file_path,))
        thread.start()

        # Return response immediately
        return jsonify({"message": "File upload initiated", "filename": filename})


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
    logging.info("Inside get_summary, the requested chapter_id is %s", chapter_id)
    summary_document = lookup_summary(chapter_id)
    logging.info("summary_document is %s", summary_document)

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


    


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
