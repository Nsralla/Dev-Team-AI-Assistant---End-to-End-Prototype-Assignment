import os
import requests
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_llama3(system_prompt:str, user_prompt: str):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role":"system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    response = requests.post(GROQ_URL, headers=headers, json=payload)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()["choices"][0]["message"]["content"]