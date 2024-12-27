import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(dotenv_path="api/.env")

def ask(query):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API Key not found. Ensure GOOGLE_API_KEY is set in the environment.")

    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(query)

    return response.text