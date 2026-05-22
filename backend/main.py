from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import asyncio

from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.genai import types
from agent import github_card_agent

# Initialize FastAPI app
app = FastAPI(title="GitHub Dev Card Generator")

# Add CORS middleware
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
            print(f"Event {event_count}: type={type(event).__name__}, is_final={event.is_final_response()}")
            
            # Check if this is a final response part
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            safe_text = part.text[:100].encode('ascii', errors='replace').decode('ascii')
                            print(f"Final response text: {safe_text}")
                            final_text += part.text
            
            # If there's an error in the event
            if event.error_message:
                safe_error = event.error_message.encode('ascii', errors='replace').decode('ascii')
                print(f"Agent Event Error: {safe_error}")
                raise Exception(event.error_message)

        print(f"Total events processed: {event_count}")

        # The agent is instructed to save the card.
        # Check if it was actually saved
        file_path = os.path.join(cards_dir, f"{username}.html")
        if not os.path.exists(file_path):
            # If not saved yet, maybe give it a moment or check the response
            print(f"Warning: Card file not found at {file_path}")
            # We could trigger the tool call directly if the agent failed to do it, 
            # but the agent is instructed to do it.
        else:
            print(f"Card file successfully saved at {file_path}")
        
        card_path = f"/static/cards/{username}.html"
        
        return {
            "status": "success",
            "username": username,
            "card_url": card_path,
            "agent_response": final_text
        }
    except Exception as e:
        print(f"Error in generate_card: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}")
async def get_card(username: str):
    file_path = os.path.join(cards_dir, f"{username}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Card not found")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
