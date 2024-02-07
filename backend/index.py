from flask import Flask, jsonify, request
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

@app.route('/get-books')
def get_books():
    books = ["1984", "Atlas Shrugged", "To Kill a Mockingbird", "The Great Gatsby", "One Hundred Years of Solitude", "Pride and Prejudice"]
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


@app.route('/get-summary/<path:chapter_id>', methods=['GET'])
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
        # Handle case where no summary is found
        return jsonify({
            "status": "error",
            "message": "Summary not found for chapter ID: " + chapter_id
        }), 404

    


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
