from openai import OpenAI
from dotenv import load_dotenv
import os
from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken


# def create_client1():
#     load_dotenv()  # Load environment variables from .env file
#     openai_api_key = os.getenv('OPENAI_API_KEY1')  # Retrieve the OpenAI API key
#     client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client
#     return client

# Function to summarize a book chapter
def summarize_book_chapter(chapter_text):
    def create_client():
      load_dotenv()  # Load environment variables from .env file
      openai_api_key = os.getenv('OPENAI_API_KEY1')  # Retrieve the OpenAI API key
      client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client
      return client

    client = create_client()
    system_prompt = ("You are a book reader, skilled in reading chapters and summarizing them. "
             "Create a response with 2 sections: 1. Summary of the chapter. 2. Key Takeaways from the Chapter "
             "If the chapter text is empty, return empty, just wait for the first chapter text.")

    # Generate the summary for the current chapter
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": chapter_text}
      ]
    )

    # Extract the generated summary from the response
    cc_message = completion.choices[0].message
    cumulative_book_summary = cc_message.content

    return cumulative_book_summary


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


