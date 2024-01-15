from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from process_book import book_main
import os
import threading


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
        thread = threading.Thread(target=book_main, args=(file_path,))
        thread.start()

        # Return response immediately
        return jsonify({"message": "File upload initiated", "filename": filename})        


    



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
