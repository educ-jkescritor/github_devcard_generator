import os
import sys
from dotenv import load_dotenv

# Load env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
print("GITHUB_TOKEN:", os.getenv("GITHUB_TOKEN"))

# Try using the google-genai SDK
try:
    from google import genai
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    print("Successfully imported google-genai and initialized Client")
    
    # List models to see what is available and if key is valid
    print("Listing models...")
    for m in client.models.list():
        if "flash" in m.name or "pro" in m.name:
            print(f" - {m.name}")
            
except Exception as e:
    print("Error with google-genai Client:", e)

# Try using legacy google-generativeai SDK (used by mcp_server.py)
try:
    import google.generativeai as legacy_genai
    legacy_genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    print("Successfully configured legacy google.generativeai")
    
    # Try gemini-2.5-flash
    try:
        model = legacy_genai.GenerativeModel("gemini-2.5-flash")
        resp = model.generate_content("Hello")
        print("legacy gemini-2.5-flash response:", resp.text)
    except Exception as e:
        print("legacy gemini-2.5-flash error:", e)
        
    # Try gemini-2.0-flash
    try:
        model = legacy_genai.GenerativeModel("gemini-2.0-flash")
        resp = model.generate_content("Hello")
        print("legacy gemini-2.0-flash response:", resp.text)
    except Exception as e:
        print("legacy gemini-2.0-flash error:", e)

    # Try gemini-1.5-flash
    try:
        model = legacy_genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content("Hello")
        print("legacy gemini-1.5-flash response:", resp.text)
    except Exception as e:
        print("legacy gemini-1.5-flash error:", e)

except Exception as e:
    print("Error with legacy google.generativeai:", e)
