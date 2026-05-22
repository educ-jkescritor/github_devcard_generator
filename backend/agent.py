import os
import sys
from dotenv import load_dotenv

# Load environment variables at the VERY top
if os.path.exists(".env"):
    load_dotenv(".env")
elif os.path.exists("../.env"):
    load_dotenv("../.env")
else:
    load_dotenv()

# Ensure both key names are set for maximum compatibility
if os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset, 
    StdioConnectionParams, 
    StdioServerParameters
)

# Define the MCP toolset connecting to our mcp_server.py
mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[os.path.join(os.path.dirname(__file__), "mcp_server.py")],
            env=os.environ.copy() # Pass the full environment
        ),
        timeout=60.0
    )
)

# Define the GitHub Dev Card Agent
github_card_agent = LlmAgent(
    name="github_card_agent",
    model="gemini-flash-latest",
    instruction="""
    You are a GitHub profile analyst and dev card generator. 
    When a user gives you a GitHub username, you MUST follow this exact sequence: 
    
    1. First, ALWAYS call the 'scrape_github' tool with the username to fetch their GitHub data
    2. Once you have the scraped data, call 'analyze_profile' with that data to get insights
    3. Then, call 'generate_card_html' with the username, the scraped data, and the analysis results
    4. Finally, ALWAYS call 'save_card' with the username and the generated HTML to save it to disk
    
    IMPORTANT: You MUST complete all 4 steps. Do not skip any step.
    IMPORTANT: Always include all the HTML generated from step 3 when calling save_card in step 4.
    
    Be enthusiastic about developers' work. 
    If the profile is private or doesn't exist, report the error clearly and ask the user to check the username.
    """,
    tools=[mcp_toolset]
)
