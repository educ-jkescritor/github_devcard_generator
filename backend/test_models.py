import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

models_to_test = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.0-flash-lite"
]

print("--- Testing newer & alternate models ---")
for model_name in models_to_test:
    print(f"Testing model: {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Hello World' in 2 words."
        )
        print(f"SUCCESS for {model_name}: {response.text.strip()}")
    except Exception as e:
        print(f"FAILED for {model_name}: {str(e)[:200]}")
