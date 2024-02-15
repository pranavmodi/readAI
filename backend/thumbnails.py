import os
import ebooklib
from ebooklib import epub

def extract_and_save_thumbnails(epubs_dir='static/epubs', thumbnails_dir='static/thumbnails'):
    # Ensure the thumbnail directory exists
    if not os.path.exists(thumbnails_dir):
        os.makedirs(thumbnails_dir)

    # Iterate over all .epub files in the epubs directory
    for filename in os.listdir(epubs_dir):
        if filename.endswith('.epub'):
            epub_path = os.path.join(epubs_dir, filename)
            epub_book = epub.read_epub(epub_path)

            # Try to find cover in metadata
            cover_item = None
            cover_id = epub_book.get_metadata('http://www.idpf.org/2007/opf', 'cover')
            if cover_id:
                cover_id = cover_id[0][0]  # Extracting the cover ID
                cover_item = epub_book.get_item_with_id(cover_id)

            # If not found in metadata, try the first image
            if not cover_item:
                cover_item = next((item for item in epub_book.get_items() if item.media_type == 'image/jpeg'), None)

            if cover_item:
                # Save the cover image
                cover_name = os.path.splitext(filename)[0] + '.jpg'
                cover_path = os.path.join(thumbnails_dir, cover_name)

                with open(cover_path, 'wb') as img_file:
                    img_file.write(cover_item.content)
                print(f"Saved thumbnail for {filename} as {cover_name}")
            else:
                print(f"No cover found for {filename}")

# Call the function
extract_and_save_thumbnails()
