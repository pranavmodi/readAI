from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    return '<p> Hello, new  World!</p> '

@app.route('/get-books')
def get_books():
    books = ["1984", "Atlas Fucking Shrugged", "To Kill a Mockingbird", "The Great Gatsby", "One Hundred Years of Solitude", "Pride and Prejudice"]
    return jsonify(books)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
