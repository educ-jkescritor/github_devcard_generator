from fastmcp import FastMCP
import requests
import json
import os
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("GitHubDevCard")

# Configure Gemini
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@mcp.tool()
def scrape_github(username: str) -> dict:
    """
    Calls the GitHub REST API to fetch public profile data and repos.
    """
    print(f"[scrape_github] Starting for username: {username}")
    
    headers = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        # User Profile
        user_url = f"https://api.github.com/users/{username}"
        print(f"[scrape_github] Fetching user profile from {user_url}")
        user_resp = requests.get(user_url, headers=headers)
        if user_resp.status_code != 200:
            error_msg = f"User not found or API error: {user_resp.status_code}"
            print(f"[scrape_github] ERROR: {error_msg}")
            return {"error": error_msg}
        
        user_data = user_resp.json()
        print(f"[scrape_github] User data retrieved: {user_data.get('name', 'N/A')}")
        
        # Repositories
        repos_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
        print(f"[scrape_github] Fetching repos from {repos_url}")
        repos_resp = requests.get(repos_url, headers=headers)
        repos_list = repos_resp.json() if repos_resp.status_code == 200 else []
        print(f"[scrape_github] Retrieved {len(repos_list)} repositories")
        
        # Process Repos
        top_repos = sorted(repos_list, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:6]
        processed_repos = [
            {
                "name": r["name"],
                "stars": r["stargazers_count"],
                "language": r["language"],
                "description": r["description"]
            } for r in top_repos
        ]
        print(f"[scrape_github] Top repos: {[r['name'] for r in processed_repos]}")
        
        # Languages Aggregation
        languages = {}
        for r in repos_list:
            lang = r.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        print(f"[scrape_github] Languages: {sorted_languages[:5]}")
        
        result = {
            "username": username,
            "name": user_data.get("name"),
            "bio": user_data.get("bio"),
            "avatar_url": user_data.get("avatar_url"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "top_repos": processed_repos,
            "most_used_languages": [l[0] for l in sorted_languages[:5]]
        }
        print(f"[scrape_github] SUCCESS: Returning data for {username}")
        return result
    except Exception as e:
        error_msg = f"Exception in scrape_github: {str(e)}"
        print(f"[scrape_github] ERROR: {error_msg}")
        return {"error": error_msg}

@mcp.tool()
def analyze_profile(github_data: dict) -> dict:
    """
    Calls Gemini 1.5 Flash to analyze GitHub data and return insights.
    """
    print(f"[analyze_profile] Starting analysis for {github_data.get('username', 'unknown')}")
    
    prompt = f"""
    Analyze this GitHub profile data and return a JSON object.
    
    Data: {json.dumps(github_data)}
    
    Return exactly this JSON structure (NO MARKDOWN, just pure JSON):
    {{
        "developer_vibe": "1 sentence personality description",
        "top_skills": ["skill1", "skill2", "skill3"],
        "fun_fact": "something clever inferred from their repos",
        "card_theme": "one of: hacker, builder, researcher, designer, open-source-hero"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print(f"[analyze_profile] Got response from Gemini")
        
        # Clean response text in case of markdown blocks
        content = response.text.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        result = json.loads(content)
        print(f"[analyze_profile] SUCCESS: Parsed JSON with skills {result.get('top_skills', [])}")
        return result
    except Exception as e:
        print(f"[analyze_profile] ERROR: {str(e)}")
        return {
            "developer_vibe": "A mysterious code weaver.",
            "top_skills": github_data.get("most_used_languages", ["Coding"])[:3],
            "fun_fact": "This developer keeps their secrets in the code.",
            "card_theme": "hacker"
        }

@mcp.tool()
def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """
    Generates a self-contained HTML string for a beautiful dev card.
    """
    print(f"[generate_card_html] Starting for {username}")
    
    theme = analysis.get("card_theme", "builder")
    themes = {
        "hacker": {"bg": "#0d1117", "text": "#58a6ff", "accent": "#238636"},
        "builder": {"bg": "#ffffff", "text": "#24292e", "accent": "#0366d6"},
        "researcher": {"bg": "#f6f8fa", "text": "#1b1f23", "accent": "#6f42c1"},
        "designer": {"bg": "#fff5f5", "text": "#d73a49", "accent": "#ea4aaa"},
        "open-source-hero": {"bg": "#f0fff4", "text": "#22863a", "accent": "#28a745"}
    }
    t = themes.get(theme, themes["builder"])
    
    skills_html = "".join([f'<span class="badge" style="background:{t["accent"]}; color:white; padding:4px 8px; border-radius:12px; margin-right:5px; font-size:12px;">{s}</span>' for s in analysis.get("top_skills", [])])
    
    repos_html = "".join([
        f'<div style="margin-top:10px; border-bottom:1px solid #eee; padding-bottom:5px;">'
        f'<strong>{r["name"]}</strong> ⭐{r["stars"]} <br/>'
        f'<small>{r["description"] or "No description"}</small>'
        f'</div>'
        for r in github_data.get("top_repos", [])[:3]
    ])
    
    print(f"[generate_card_html] Theme: {theme}, Skills: {analysis.get('top_skills', [])}, Repos: {len(repos_html)}")

    html = f"""
    <div class="dev-card" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; width: 400px; padding: 20px; border-radius: 12px; background: {t["bg"]}; color: {t["text"]}; border: 1px solid #ddd; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <img src="{github_data.get("avatar_url")}" style="width: 60px; height: 60px; border-radius: 50%; margin-right: 15px; border: 2px solid {t["accent"]};">
            <div>
                <h2 style="margin: 0; font-size: 20px;">{github_data.get("name") or username}</h2>
                <p style="margin: 0; opacity: 0.8; font-size: 14px;">@{username}</p>
            </div>
        </div>
        <p style="font-style: italic; margin-bottom: 15px;">"{analysis.get("developer_vibe")}"</p>
        <div style="margin-bottom: 15px;">
            {skills_html}
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 15px; border-top: 1px solid #eee; padding-top: 10px;">
            <span><strong>{github_data.get("public_repos")}</strong> Repos</span>
            <span><strong>{github_data.get("followers")}</strong> Followers</span>
            <span><strong>{theme.title()}</strong></span>
        </div>
        <div style="font-size: 13px;">
            <h4 style="margin: 0 0 10px 0; color: {t["accent"]};">Top Repositories</h4>
            {repos_html}
        </div>
        <p style="margin-top: 15px; font-size: 11px; opacity: 0.6; text-align: center;">Fun Fact: {analysis.get("fun_fact")}</p>
    </div>
    """
    print(f"[generate_card_html] SUCCESS: Generated HTML card")
    return html


@mcp.tool()
def save_card(username: str, html: str) -> str:
    """
    Saves the HTML to static/cards/{username}.html
    """
    print(f"[save_card] Starting save for {username}")
    
    static_dir = os.path.join(os.path.dirname(__file__), "static", "cards")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"[save_card] Created directory: {static_dir}")
        
    filename = f"{username}.html"
    file_path = os.path.join(static_dir, filename)
    
    # Wrap in a full HTML document for browser viewing
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>{username}'s Dev Card</title></head>
    <body style="display:flex; justify-content:center; align-items:center; height:100vh; background:#f0f2f5;">
        {html}
    </body>
    </html>
    """
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"[save_card] SUCCESS: Card saved to {file_path}")
        return f"/static/cards/{filename}"
    except Exception as e:
        print(f"[save_card] ERROR: {str(e)}")
        raise

if __name__ == "__main__":
    mcp.run()
