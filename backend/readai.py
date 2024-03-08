import json
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

def split_into_chunks(chapter_text, max_token_length=3000, overlap_length=500):
    """
    Splits a text into chunks, each having a maximum of max_token_length tokens.
    Each chunk starts and ends at the end of a sentence and there is overlap between chunks.
    This uses a rough approximation of 4 characters per token.
    """
    avg_chars_per_token = 4
    max_chunk_length = max_token_length * avg_chars_per_token
    overlap_chars = overlap_length * avg_chars_per_token
    chunks = []

    while chapter_text:
        if len(chapter_text) <= max_chunk_length:
            chunks.append(chapter_text)
            break

        # Find the end of a sentence near max_chunk_length
        end = chapter_text.rfind('.', 0, max_chunk_length) + 1

        # If a sentence end wasn't found, take the whole chunk
        if end == 0:
            end = max_chunk_length

        chunk = chapter_text[:end]
        chunks.append(chunk)

        # Find the start of the next sentence for the next chunk
        next_sentence_start = chapter_text.find('. ', end - 1) + 2
        if next_sentence_start < 2:
            next_sentence_start = end

        # Start next chunk with some overlap, but from the start of a sentence
        overlap_start = max(end, next_sentence_start - overlap_chars)
        chapter_text = chapter_text[overlap_start:]

    return chunks


def summarize_chunk(chunk, client):
    system_prompt = ("You are an AI assistant skilled in summarizing book chapters. "
                     "Please provide a concise summary of this text chunk, focusing on key points and main ideas.")

    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": chunk}
      ]
    )

    return completion.choices[0].message.content


def consolidate_summaries(summaries, client):
    # system_prompt = ("You are an AI assistant. You have received summaries of a book chapter. "
    #                  "Combine these into a single coherent summary. Return the result as a JSON object with keys "
    #                  "Quotes Around Keys and String Values: In JSON, both keys and string values must be enclosed in double quotes ("). Single quotes (') are not valid in JSON.
    #                 "Boolean Values: Boolean values in JSON are represented as true or false (all lowercase), without quotes. If 'Yes' is intended to be a boolean, it should be replaced with true or false.
    #                  "'title', 'summary', and 'is_main_content'. Here's an example: "
    #                  "{'title': 'Chapter 1', 'summary': 'In this chapter, the main character...', 'is_main_content': 'Yes'}")

    system_prompt = ("You are an AI assistant. You have received summaries of a book chapter. "
                 "Combine these into a single coherent summary. Return the result as a JSON object. "
                 "When creating the JSON object, remember to: "
                 "0. 3 keys must be included - 'title', 'summary', and 'is_main_content'. create an approprite title for the chapter, a summary and a boolean value for is_main_content. By main content it means if the chapter is the main content of the book, and not things like preface, introduction, etc."
                 "1. Enclose keys and string values in double quotes. "
                 "2. Use true or false for boolean values, without quotes. true and fasle should be all lowercase."
                 "3. Ensure proper JSON structure with commas separating key-value pairs and curly braces enclosing the object. "
                 "Here are a couple of examples of a properly formatted JSON object. Note the lowercase true and false. "
                 "{\"title\": \"Chapter 1\", \"summary\": \"This is the copyrights page ....\", \"is_main_content\": false}"
                 "{\"title\": \"Chapter 1\", \"summary\": \"The main character does something silly...\", \"is_main_content\": true}"
                 "Before returning, validate the json object to ensure it has the correct keys and values. Especially that the boolean are all lowercase.")


    # Check if summaries is a list and combine, else use it directly
    combined_summaries = " ".join(summaries) if isinstance(summaries, list) else summaries

    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": combined_summaries}
      ]
    )

    try:
        # Attempt to parse the response as JSON
        print(completion.choices[0].message.content)
        unified_summary = json.loads(completion.choices[0].message.content)

        # Validate the keys in the JSON response
        if all(key in unified_summary for key in ["title", "summary", "is_main_content"]):
            return unified_summary
        else:
            raise ValueError("Response JSON does not contain the required keys.")

    except json.JSONDecodeError:
        # Handle case where response is not a valid JSON
        print("The response from the model is not valid JSON.")
        return None
    except ValueError as e:
        # Handle other validation errors
        print(e)
        return None




def summarize_book_chapter(chapter_text):
    client = create_client()
    chunks = split_into_chunks(chapter_text)
    chunk_summaries = [summarize_chunk(chunk, client) for chunk in chunks]
    consolidated_summary = consolidate_summaries(chunk_summaries, client)
    return consolidated_summary


def summarize_summaries(chapter_summaries, client=None):
    print("Inside summarize_summaries")
    if client is None:
        client = create_client()  # Initialize client

    # Check if the token count exceeds the limit
    if num_tokens_from_string(chapter_summaries, 'r50k_base') > 4096:
        chunks = split_into_chunks(chapter_summaries)
        chunk_summaries = [summarize_chunk(chunk, client) for chunk in chunks]

        combined_summaries = " ".join(chunk_summaries)
        if num_tokens_from_string(combined_summaries, 'r50k_base') > 4096:
            return summarize_summaries(combined_summaries, client)  # Recursive call with return
        else:
            return summarize_chunk(combined_summaries, client)  # Summarize the combined summaries
    else:
        system_prompt = ("You are a book reader, skilled in reading chapters and summarizing them. "
                         "You have read several summaries of different parts of a book. "
                         "Please provide a concise, unified summary that captures the overall summary of the entire book.")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chapter_summaries}
            ]
        )
        return completion.choices[0].message.content

# Example usage (assuming necessary functions and client are defined)
# summary = summarize_summaries(your_chapter_summaries)




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


