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


def get_isbn(file_path):
    # Get the EPUB's metadata
    import lxml.etree as etree

    book = epub.read_epub(file_path)
    metadata = book.get_metadata('DC', 'identifier')

    # Access the package (metadata, manifest, and spine are stored here)
    try:
        package = book.get_item_with_id('ncx').get_content()
        root = etree.fromstring(package)

        # Define the namespaces used in the package document
        ns = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'opf': 'http://www.idpf.org/2007/opf'
        }

        # Look for the <dc:identifier> element
        for identifier in root.findall('.//dc:identifier', ns):
            if identifier.text.startswith('urn:isbn:'):
                return identifier.text[9:]  # Remove the 'urn:isbn:' part

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        print(f"An error occurred: {e}")
        return None

def read_epub(file_path, book_name, author_name):
    # Open the EPUB file
    book = epub.read_epub(file_path)

    # Get the EPUB's metadata

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
    
    os.chdir('/Users/pranav/personal/books/selfhelp/')
    read_epub('Be Useful.epub', "Be Useful", "Arnold Schwarzenegger")

