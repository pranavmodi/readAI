from pymongo import MongoClient
from pymongo import MongoClient



def init_db(book_name):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["books_db"]
    print('the collection names', db.list_collection_names())
    collection = db[book_name]
    return collection



def get_summary(index_num, collection):
    document = collection.find_one({"index_num": index_num})
    if document is None:
        return None
    return document['summary']

# Define a function to store summaries
def store_summary(index_num, summary, collection):
  # Create a document
  document = {
    "index_num": index_num,
    "summary": summary
  }

  # Insert the document into the collection
  collection.insert_one(document)

# # Example usage
# book_title = "The Lord of the Rings"

# # Store summaries for individual chapters
# store_summary(1, "The Fellowship of the Ring is formed.")
# store_summary(2, "The Fellowship departs from Rivendell.")
# store_summary(3, "The Fellowship is broken.")
# store_summary(4, "Frodo and Sam continue their journey to Mordor.")
# store_summary(5, "The Battle of Helm's Deep takes place.")
# store_summary(6, "Frodo and Sam reach Mount Doom and destroy the One Ring.")

# # Print confirmation message
# print(f"Chapterwise summaries for '{book_title}' stored successfully!")