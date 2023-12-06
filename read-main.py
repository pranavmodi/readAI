import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os


def read_epub(file_path):
    # Open the EPUB file
    book = epub.read_epub(file_path)

    # Iterate through each item in the book
    for item in book.get_items():
        print(type(item))
        # Check if the item is an instance of the ebooklib.epub.EpubHtml class
        if isinstance(item, ebooklib.epub.EpubHtml):
            # Parse the item's content using BeautifulSoup
            soup = BeautifulSoup(item.content, 'html.parser')
            # Print the text from the parsed content
            print(soup.get_text())

# Replace 'your_book.epub' with the path to your EPUB file


os.chdir('/Users/pranav/personal/books')
read_epub('Be Useful.epub')
