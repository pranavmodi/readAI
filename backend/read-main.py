import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os, sys
import tiktoken
from readai import read_book_chapter
from db_store import init_db, store_summary, get_summary


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def read_epub(file_path, book_name, author_name):
    # Open the EPUB file
    book = epub.read_epub(file_path)

    # Iterate through each item in the book

    # book_items = []
    # for item in book.get_items():
    #     book_items.append(item)

    # print('the lenghth of book items', len(book_items))
    ##for item in book.get_items():
    db_collection = init_db(book_name)

    book_text = ''
    book_summary = ''
    html_index = 0
    for item in book.get_items():
        # print(type(item))
        # Check if the item is an instance of the ebooklib.epub.EpubHtml class
        if isinstance(item, ebooklib.epub.EpubHtml):
            print('the html index is', html_index)
            html_index += 1
            db_summary = get_summary(html_index, db_collection)
            if db_summary is not None:
                print('summary exists in db')
                continue
            # Parse the item's content using BeautifulSoup
            print('summary does not exist in db')
            soup = BeautifulSoup(item.content, 'html.parser')
            # Print the text from the parsed content
            chapter_text = soup.get_text()
            # num_tokens = num_tokens_from_string(chapter_text, 'r50k_base')
            # print('num tokens', num_tokens)
            
            book_text += chapter_text
            cumulative_book_summary = read_book_chapter(book_summary, chapter_text)
            store_summary(html_index, cumulative_book_summary, db_collection)
            # ask for user input, space to continue, q to quit
            user_input = input("Continue with next chapter? (y/n): ")
            if user_input == 'n':
                sys.exit()

    






if __name__ == "__main__":
    
    os.chdir('/Users/pranav/personal/books')
    read_epub('Be Useful.epub', "Be Useful", "Arnold Schwarzenegger")

