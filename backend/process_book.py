import ebooklib
from ebooklib import epub
from pymongo import MongoClient
import pymongo
import logging
import json
from pymongo.errors import ConnectionFailure
from readai import summarize_book_chapter, summarize_summaries, call_standalone_embedding_script
from bs4 import BeautifulSoup
import numpy as np
import faiss
from transformers import AutoTokenizer, AutoModel
import psutil
import os

logger = logging.getLogger(__name__)
logger.propagate = True
logging.basicConfig(level=logging.INFO)


# Function to connect to MongoDB
def connect_to_mongodb():
    client = MongoClient('mongodb://localhost:27017/')
    # client = MongoClient('mongodb://172.18.0.2:27017/')
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        # print("MongoDB is connected")
        # logging.info("MongoDB is connected")
    except ConnectionFailure:
        print("Server not available")
        logging.info("Server not available")
    db = client['epub_reader_db']
    collection = db['insights']
    return collection

def lookup_summary(chapter_id):
    # Query the database for the summary
    collection = connect_to_mongodb()
    logging.info("Inside lookup_summary, the requested chapter_id is %s", chapter_id)
    summary_document = collection.find_one({"chapter_identifier": chapter_id})

    if summary_document:
        # Return the summary if found
        return summary_document['chapter_summary']
    else:
        # Handle case where no summary is found
        return None
    
def lookup_book_summary(book_title):
    # Query the database for the summary
    collection = connect_to_mongodb()
    summary_document = collection.find_one({"book": book_title, "is_book_summary": True})
    if summary_document:
        # Return the summary if found
        return summary_document['book_summary']
    else:
        # Handle case where no summary is found
        return None
    

def extract_text_to_json(epub_path, json_path, chunk_size):
    book = epub.read_epub(epub_path)
    content = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')
            paragraphs = soup.get_text().split('\n')
            chunk = ''
            for paragraph in paragraphs:
                if len(chunk.split()) + len(paragraph.split()) <= chunk_size:
                    chunk += ' ' + paragraph
                else:
                    content.append(chunk.strip())
                    chunk = paragraph
            if chunk:  # Add the last chunk
                content.append(chunk.strip())

    # Save to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    
def check_summaries(file_path, collection, rewrite=False, socketio=None):
    logging.info("Inside check_summaries, the file_path is %s", file_path)
    book = epub.read_epub(file_path)
    book_title = book.get_metadata('DC', 'title')[0][0]
    logging.info("book_title is %s", book_title)

    # Check if book summary exists
    book_summary = collection.find_one({"book": book_title, "is_book_summary": True})

    # Check if all chapter summaries exist
    total_chapters = len(list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT)))
    chapter_summaries = collection.find({"book": book_title, "is_book_summary": {"$ne": True}})
    chapter_summaries_count = chapter_summaries.count()

    if book_summary and chapter_summaries_count == total_chapters:
        logging.info("All summaries are completed for the book: %s", book_title)
        return True
    else:
        logging.info("Summaries are still pending for the book: %s", book_title)
        return False


def process_epub(file_path, collection, socketio, rewrite=False):
    logging.info("wth Inside process_epub, the file_path is %s", file_path)
    book = epub.read_epub(file_path)
    chapter_count = 0  # Initialize a counter for chapters
    book_title = book.get_metadata('DC', 'title')[0][0]
    logging.info("book_title is %s", book_title)
    chapter_summaries = []

    total_chapters = len(list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT)))

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        chapter_count += 1  # Increment the chapter count
        chapter_content = item.get_body_content().decode()

        # Create a unique identifier for each chapter, for example, using book title and chapter number
        chapter_uri = item.file_name
        chapter_identifier = f"{book_title}_Chapter_{chapter_uri}"

        # Check if the summary for this chapter already exists in the database
        existing_summary = collection.find_one({"chapter_identifier": chapter_identifier})
        if existing_summary is None or rewrite is True or existing_summary.get('chapter_summary') is None:
            # Summary not found in database, generate it
            chapter_summary = summarize_book_chapter(chapter_content)
            chapter_summaries.append({'chapter_summary': chapter_summary})

            # Store the chapter summary, count, and identifier in the database
            document = {
                'book': book_title,
                'chapter_count': chapter_count,
                'chapter_summary': chapter_summary,
                'chapter_identifier': chapter_identifier
            }
            collection.insert_one(document)
        else:
            # Summary already exists, skip processing
            chapter_summaries.append(existing_summary)

        # Emit progress update
        if socketio:
            progress = int((chapter_count / (total_chapters + 1)) * 100)
            socketio.emit('progress_update', {'progress': progress})

    # Now summarizing all the chapters to get a unified summary of the book as a whole
    existing_book_summary = lookup_book_summary(book_title)
    if existing_book_summary:
        logging.info("Book summary already exists, skipping processing for book")
    else:
        consolidated_summary = summarize_summaries(" ".join(chapter['chapter_summary']['summary'] for chapter in chapter_summaries if 'chapter_summary' in chapter and chapter['chapter_summary']['is_main_content']))
        document = {
            'book': book_title,
            'is_book_summary': True,  # Flag to indicate that this is a book summary
            'book_summary': consolidated_summary
        }
        logging.info("wtf is going on")
        collection.insert_one(document)
    if socketio:
        progress = int(((chapter_count + 1) / (total_chapters + 1)) * 100)
        socketio.emit('progress_update', {'progress': progress})

    socketio.emit('disconnect', {'book_title': book_title})



# Function to create indexes in MongoDB
def create_indexes(collection):
    # Define the index specifications
    index_specs = [
        {"key": [("book", pymongo.ASCENDING)], "name": "book_index"},
        {"key": [("chapter_count", pymongo.ASCENDING)], "name": "chapter_count_index"},
        {"key": [("chapter_summary", pymongo.TEXT)], "name": "chapter_summary_text_index"}
    ]

    # Retrieve current indexes on the collection
    existing_indexes = collection.list_indexes()
    # Create a set of existing index names
    existing_index_names = {index['name'] for index in existing_indexes}

    # Create each index if it does not already exist
    for index_spec in index_specs:
        if index_spec["name"] not in existing_index_names:
            collection.create_index(index_spec["key"], name=index_spec["name"])
            logging.info(f"Created index: {index_spec['name']}")
        else:
            logging.info(f"Index already exists: {index_spec['name']}")

def log_memory_usage(stage=""):
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"{stage} - Memory usage: {memory_info.rss / 1024 ** 2:.2f} MB")




def book_main(file_path, socketio, json_path, embeddings_path):
    logging.info('Processing book: %s', file_path)
    collection = connect_to_mongodb()
    create_indexes(collection)
    process_epub(file_path, collection, socketio, False)
    embeddings = None

    if os.path.exists(embeddings_path):
        logging.info(f"Embeddings file already exists at {embeddings_path}.")
        try:
            embeddings = np.load(embeddings_path)
            logging.info(f"Embeddings file already exists at {embeddings_path}.")

        except Exception as e:
            logging.error(f"Error loading embeddings from {embeddings_path}: {e}")
        

    if embeddings is None:
        extract_text_to_json(file_path, json_path, chunk_size=200)
        log_memory_usage()  # Log memory usage

        with open(json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        embeddings = call_standalone_embedding_script(content, model_name, batch_size=1)
        np.save(embeddings_path, embeddings)

    logging.info(f"Embeddings shape: {embeddings.shape}")
    # dimension = embeddings.shape[1]
    # index = faiss.IndexFlatL2(dimension)
    # index.add(embeddings)
    # logging.info(f"FAISS index created with {len(embeddings)} embeddings")