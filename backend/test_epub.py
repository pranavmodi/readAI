import random
from ebooklib import epub

# Function to create Carl Jung style content about Gandhi
def carl_jung_content():
    chapter1_content = """
    <h1>Introduction</h1>
    <p>Mahatma Gandhi, a figure revered and often misunderstood, represents an archetype that transcends mere historical significance. In the realm of the collective unconscious, Gandhi symbolizes the Self, a unifying principle striving towards individuation. His life, marked by nonviolent resistance and profound spiritual insights, calls us to reflect on the deeper aspects of human nature and our societal structures.</p>
    <p>Gandhi’s principle of Ahimsa, or nonviolence, is not merely a political strategy but a profound psychological stance. It challenges the very fabric of human aggression and the innate tendencies towards conflict. Gandhi’s commitment to truth, or Satyagraha, is another dimension that invites introspection. The pursuit of truth, in the Jungian sense, is a journey towards self-realization, uncovering the layers of the psyche to reveal the core essence of the individual.</p>
    <p>In this exploration, we delve into the psychological underpinnings of Gandhi's philosophies and actions. By examining Gandhi through the lens of analytical psychology, we gain insights into the collective unconscious, the archetypes that shape our behaviors, and the individuation process that leads to a more harmonious existence.</p>
    """

    chapter2_content = """
    <h1>Gandhi and the Shadow</h1>
    <p>Gandhi's philosophy of nonviolence, or Ahimsa, stands in stark contrast to the Shadow aspect of the psyche. The Shadow, as an integral part of the unconscious, encompasses the darker elements of the self that are often repressed. Gandhi's life work can be seen as a continuous struggle to integrate the Shadow within the social and personal spheres, advocating for a moral and spiritual revolution.</p>
    <p>The concept of the Shadow is crucial in understanding the human condition. It represents the unacknowledged and often feared aspects of ourselves that we project onto others. Gandhi’s approach to conflict was revolutionary because it sought to address these projections. By advocating for nonviolence, he was, in essence, calling for a confrontation with the Shadow—not through aggression, but through understanding and integration.</p>
    <p>Gandhi’s personal struggles, including his experiments with celibacy and self-discipline, can be viewed as efforts to confront and integrate his own Shadow. His transparent acknowledgment of his imperfections made him a relatable and compelling figure, demonstrating that the path to individuation is fraught with challenges but is ultimately transformative. His life serves as a testament to the power of integrating the Shadow to achieve a higher state of consciousness and societal harmony.</p>
    """

    return chapter1_content, chapter2_content

# Create an EPUB book
book = epub.EpubBook()

# Set the title and author
book.set_title('Carl Jung on Gandhi')
book.set_language('en')
book.add_author('Carl Jung (inspired)')

# Get content for the chapters
chapter1_content, chapter2_content = carl_jung_content()

# Create chapters
chapter1 = epub.EpubHtml(title='Introduction', file_name='chap_01.xhtml', lang='en')
chapter1.content = chapter1_content

chapter2 = epub.EpubHtml(title='Gandhi and the Shadow', file_name='chap_02.xhtml', lang='en')
chapter2.content = chapter2_content

# Add chapters to the book
book.add_item(chapter1)
book.add_item(chapter2)

# Create table of contents
book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
            epub.Link('chap_02.xhtml', 'Gandhi and the Shadow', 'shadow'))

# Add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# Define CSS style
style = 'BODY {color: black; font-family: Arial, sans-serif;}'  # Basic style for readability

nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
book.add_item(nav_css)

# Create spine
book.spine = ['nav', chapter1, chapter2]

# Write the EPUB file
epub.write_epub('carl_jung_on_gandhi.epub', book, {})

print("EPUB file 'carl_jung_on_gandhi.epub' created successfully!")
