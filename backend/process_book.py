import traceback
import ebooklib
from ebooklib import epub
from pymongo import MongoClient
import pymongo
import logging
from pymongo.errors import ConnectionFailure
from readai import summarize_book_chapter, summarize_book


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
        print("MongoDB is connected")
        logging.info("MongoDB is connected")
    except ConnectionFailure:
        print("Server not available")
        logging.info("Server not available")
    db = client['epub_reader_db']
    collection = db['insights']
    return collection

def lookup_summary(chapter_id):
    # Query the database for the summary
    collection = connect_to_mongodb()
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

# Function to process the ePub file
def process_epub(file_path, collection, rewrite=False):
    logging.info("Inside process_epub, the file_path is %s", file_path)
    book = epub.read_epub(file_path)
    chapter_count = 0  # Initialize a counter for chapters
    book_title = book.get_metadata('DC', 'title')[0][0]
    logging.info("book_title is %s", book_title)
    chapter_summaries = []

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        chapter_count += 1  # Increment the chapter count
        chapter_content = item.get_body_content().decode()

        # Create a unique identifier for each chapter, for example, using book title and chapter number

        chapter_uri = item.file_name
        chapter_identifier = f"{book_title}_Chapter_{chapter_uri}"

        # Check if the summary for this chapter already exists in the database
        existing_summary = collection.find_one({"chapter_identifier": chapter_identifier})
        # logging.info("existing_summary is %s", existing_summary)
        if existing_summary is None or rewrite is True or existing_summary['chapter_summary'] is None:
            # logging.info("Going to process again for chapter number %s", chapter_count)
            # logging.info("checking if null, the existing_summary is %s", existing_summary['chapter_summary'])
            # Summary not found in database, generate it
            chapter_summary = summarize_book_chapter(chapter_content)
            chapter_summaries.append(chapter_summary)

            # Store the chapter summary, count, and identifier in the database
            document = {
                'book': book_title,
                'chapter_count': chapter_count,
                'chapter_summary': chapter_summary,
                'chapter_identifier': chapter_identifier
            }

            # will pretty print log the created document variable in a readable manner
            # logging.info("going to insert, the document is %s", document)
            collection.insert_one(document)
            # check if the insertion was successful
            # logging.info("inserted document is %s", collection.find_one({"chapter_identifier": chapter_identifier}))
        else:
            # Summary already exists, skip processing
            chapter_summaries.append(existing_summary)

    # Now summarizing all the chapters to get a unified summary of the book as a whole

    # First check if the summary already exists
    existing_book_summary = lookup_book_summary(book_title)
    if existing_book_summary:
        logging.info("Book summary already exists, skipping processing for book: %s", existing_book_summary)
        return
    else:
        # join together all chapter summaries which have is_main_content as True
        consolidated_summary = summarize_book(" ".join(cs['summary'] for cs in chapter_summaries if cs['is_main_content']))
        document = {
            'book': book_title,
            'is_book_summary': True,  # Flag to indicate that this is a book summary
            'book_summary': consolidated_summary
        }
        collection.insert_one(document)




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
    logging.info("Existing indexes: %s", existing_indexes)

    # Create a set of existing index names
    existing_index_names = {index['name'] for index in existing_indexes}

    # Create each index if it does not already exist
    for index_spec in index_specs:
        if index_spec["name"] not in existing_index_names:
            collection.create_index(index_spec["key"], name=index_spec["name"])
            logging.info(f"Created index: {index_spec['name']}")
        else:
            logging.info(f"Index already exists: {index_spec['name']}")

def book_main(file_path):
    logging.info('Processing book: %s', file_path)
    try:
        collection = connect_to_mongodb()
        create_indexes(collection)

        process_epub(file_path, collection, False)
        logging.info("Successfully processed and inserted into MongoDB")

        # Optionally, create indexes after processing if they are specific to the processed data
        # create_indexes(collection)

    except pymongo.errors.PyMongoError as e:
        logging.error("MongoDB error: %s", e)
        traceback.print_exc()  # Print the stacktrace
    except Exception as e:
        logging.error("An error occurred: %s", e)
        traceback.print_exc()  # Print the stacktrace
    finally:
        # Close the MongoDB connection if open, or handle accordingly
        pass
