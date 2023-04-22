from typing import Dict, List
import openai
import os
import requests
import storage

CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")
CHATGPT_API_URL = "https://api.openai.com/v1/engines/davinci-codex/completions"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CHATGPT_API_KEY}"
}


def _process_summary(relevant_files, query_request: str):
    chunks = _break_down_into_chunks(relevant_files)

    conversation_history = []

    system_message = f"{query_request}. You are a helpful assistant that will process documents, build an outline, and generate a summary of the current results."

    for chunk_id, chunk in chunks.items():
        user_message = f"Process the document '{chunk_id}'. {chunk}"
        assistant_response = ask_chatgpt_conversation(
            conversation_history, system_message, user_message)

        system_message = "Continue processing documents and updating the outline and summary of the current results."
        user_message = f"Based on the information from '{chunk_id}', update the outline and summary of the current results."
        assistant_response = ask_chatgpt_conversation(
            conversation_history, system_message, user_message)

    system_message = "You are now going to provide a brief and compressed summary of the processed documents."
    user_message = "Provide a brief and compressed summary of the processed documents."
    final_summary = ask_chatgpt_conversation(
        conversation_history, system_message, user_message)

    return final_summary


def _break_down_into_chunks(relevant_files: Dict[str, str], max_context_size=4096, prompt_space=200):
    chunks = {}
    remaining_space = max_context_size - prompt_space
    current_chunk = {}
    current_chunk_space = remaining_space

    for file_id, file_content in relevant_files.items():
        tokens = file_content.split()

        if len(tokens) <= current_chunk_space:
            current_chunk[file_id] = file_content
            current_chunk_space -= len(tokens)

        else:
            if current_chunk:
                chunk_id = f"chunk-{len(chunks)}"
                chunks[chunk_id] = current_chunk
                current_chunk = {}
                current_chunk_space = remaining_space

            while len(tokens) > 0:
                split_content = " ".join(tokens[:current_chunk_space])
                if len(tokens) > current_chunk_space:
                    split_content += " [Continued in the next part]"
                current_chunk[file_id] = split_content
                tokens = tokens[current_chunk_space:]

                chunk_id = f"chunk-{len(chunks)}"
                chunks[chunk_id] = current_chunk
                current_chunk = {}
                current_chunk_space = remaining_space

    if current_chunk:
        chunk_id = f"chunk-{len(chunks)}"
        chunks[chunk_id] = current_chunk

    return chunks


openai.api_key = os.getenv("OPENAI_API_KEY")


def ask_chatgpt_conversation(history, system_message, new_user_message):
    history.append({"role": "system", "content": system_message})
    history.append({"role": "user", "content": new_user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )

    assistant_response = response.choices[0].message['content'].strip()
    history.append({"role": "assistant", "content": assistant_response})

    return assistant_response
