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

def create_client():
    load_dotenv()  # Load environment variables from .env file
    openai_api_key = os.getenv('OPENAI_API_KEY1')  # Retrieve the OpenAI API key
    client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client
    return client

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def split_into_chunks(text, max_token_length=3000):
    """
    Splits a text into chunks, each having a maximum of max_token_length tokens.
    This uses a rough approximation of 4 characters per token.
    """
    avg_chars_per_token = 4
    max_chunk_length = max_token_length * avg_chars_per_token
    chunks = []

    while text:
        # Take the next chunk of text up to the max_chunk_length
        chunk = text[:max_chunk_length]
        chunks.append(chunk)
        # Remove the processed chunk from the text
        text = text[max_chunk_length:]

    return chunks


# def split_into_chunks(text, max_token_length=4000, encoding='gpt-3.5-turbo'):
#     """
#     Splits a text into chunks, each having a maximum of max_token_length tokens.
#     """
#     # encoding = tiktoken.get_encoding(encoding)
#     tokens = encoding.encode(text)
#     chunks = []

#     current_chunk = []
#     current_length = 0

#     for token in tokens:
#         if current_length + len(token) > max_token_length:
#             # Join the tokens in the current chunk and add it to the chunks list
#             chunks.append(encoding.decode(current_chunk))
#             current_chunk = [token]
#             current_length = len(token)
#         else:
#             current_chunk.append(token)
#             current_length += len(token)

#     # Add the last chunk if it's not empty
#     if current_chunk:
#         chunks.append(encoding.decode(current_chunk))

#     return chunks



def summarize_chunk(chunk, client):
    system_prompt = ("You are a book reader, skilled in reading chapters and summarizing them. Summarize this text chunk. "
                     "Please provide a concise, unified summary that captures the key points from these summaries.")

    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": chunk}
      ]
    )

    return completion.choices[0].message.content


def consolidate_summaries(summaries, client):
    system_prompt = ("You are a book reader, skilled in reading chapters and summarizing them. "
                     "You have read several summaries of different parts of a chapter. "
                     "Please provide a concise, unified summary that captures the key points from these summaries.")

    # Combine summaries into a single text
    combined_summaries = " ".join(summaries)
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": combined_summaries}
      ]
    )

    return completion.choices[0].message.content


def summarize_book_chapter(chapter_text):
    # Check if the chapter needs to be split into chunks
    client = create_client()
    if num_tokens_from_string(chapter_text, 'r50k_base') > 3000:
        chunks = split_into_chunks(chapter_text)
        chunk_summaries = [summarize_chunk(chunk, client) for chunk in chunks]
        consolidated_summary = consolidate_summaries(chunk_summaries, client)
    else:
        consolidated_summary = summarize_chunk(chapter_text, client)

    return consolidated_summary


# Function to summarize a book chapter
# def summarize_book_chapter(chapter_text):
#     def create_client():
#       load_dotenv()  # Load environment variables from .env file
#       openai_api_key = os.getenv('OPENAI_API_KEY1')  # Retrieve the OpenAI API key
#       client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client
#       return client

#     client = create_client()
#     system_prompt = ("You are a book reader, skilled in reading chapters and summarizing them. "
#              "Create a response with 2 sections: 1. Summary of the chapter. 2. Key Takeaways from the Chapter "
#              "If the chapter text is empty, return empty, just wait for the first chapter text.")

#     # Generate the summary for the current chapter
#     completion = client.chat.completions.create(
#       model="gpt-3.5-turbo",
#       messages=[
#         {"role": "system", "content": system_prompt},
#         {"role": "user", "content": chapter_text}
#       ]
#     )

#     # Extract the generated summary from the response
#     cc_message = completion.choices[0].message
#     cumulative_book_summary = cc_message.content

#     return cumulative_book_summary


