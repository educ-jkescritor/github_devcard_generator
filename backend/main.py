import os
from dotenv import load_dotenv

# Load environment variables at the VERY top
if os.path.exists(".env"):
    load_dotenv(".env")
elif os.path.exists("../.env"):
    load_dotenv("../.env")
else:
    load_dotenv()

# Ensure both key names are set for maximum compatibility
key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if key:
    os.environ["GOOGLE_API_KEY"] = key
    os.environ["GEMINI_API_KEY"] = key
    print(f"API Key detected in environment: {key[:4]}...{key[-4:]}")
else:
    print("CRITICAL: No API Key found in environment variables!")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio

from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.genai import types
from agent import github_card_agent

# Initialize FastAPI app
app = FastAPI(title="GitHub Dev Card Generator")

# Add CORS middleware with more specific configuration if needed, 
# but "*" is generally fine for local dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup ADK Services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# Initialize ADK Runner
runner = Runner(
    app_name="GitHubDevCardGen",
    agent=github_card_agent,
    session_service=session_service,
    memory_service=memory_service,
    auto_create_session=True
)

# Ensure static directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
cards_dir = os.path.join(static_dir, "cards")
os.makedirs(cards_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class GenerateRequest(BaseModel):
    username: str

@app.post("/generate")
async def generate_card(request: GenerateRequest):
    username = request.username
    session_id = f"session_{username}"
    user_id = "default_user"
    
    print(f"\n--- New Request: {username} ---")
    
    try:
        # Prepare content
        content = types.Content(
            role="user",
            parts=[types.Part(text=f"Generate a dev card for {username}")]
        )

        # Run the agent async
        print(f"Starting agent run for user: {username}")
        events = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        )
        
        final_text = ""
        event_count = 0
        async for event in events:
            event_count += 1
            # print(f"Event {event_count}: type={type(event).__name__}")
            
            # Check if this is a final response part
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            final_text += part.text
            
            # If there's an error in the event
            if event.error_message:
                print(f"AGENT ERROR EVENT: {event.error_message}")
                raise Exception(event.error_message)

        print(f"Agent finished. Total events: {event_count}")

        # The agent is instructed to save the card.
        # Check if it was actually saved
        file_path = os.path.join(cards_dir, f"{username}.html")
        if not os.path.exists(file_path):
            print(f"CRITICAL: Card file NOT found at {file_path}")
            # Try to see if the agent returned the HTML in final_text but didn't save?
            # For now, just report the error.
            raise HTTPException(status_code=500, detail="Agent failed to save the card file.")
        
        print(f"Card successfully verified at {file_path}")
        card_path = f"/static/cards/{username}.html"
        
        return {
            "status": "success",
            "username": username,
            "card_url": card_path,
            "agent_response": final_text
        }
    except Exception as e:
        print(f"EXCEPTION in generate_card: {str(e)}")
        # import traceback
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}")
async def get_card(username: str):
    file_path = os.path.join(cards_dir, f"{username}.html")
    print(f"Fetching card for {username}: {file_path}")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    print(f"Card not found: {file_path}")
    raise HTTPException(status_code=404, detail="Card not found")

@app.get("/health")
async def health():
    return {"status": "ok", "google_api_key": "present" if os.getenv("GOOGLE_API_KEY") else "missing"}

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on http://0.0.0.0:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
