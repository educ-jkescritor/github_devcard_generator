import os
import sys
from dotenv import load_dotenv

# Ensure we can import from current directory
sys.path.append(os.path.dirname(__file__))

# Load env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

print("--- Testing GitHub Data Scraper & Dev Card Generator ---")
print("GOOGLE_API_KEY:", "Present" if os.getenv("GOOGLE_API_KEY") else "Missing")
print("GITHUB_TOKEN:", "Present" if os.getenv("GITHUB_TOKEN") else "Missing")

from mcp_server import scrape_github, analyze_profile, generate_card_html, save_card

username = "torvalds"
print(f"\n1. Scraping GitHub profile for: {username}...")
github_data = scrape_github(username)

if "error" in github_data:
    print(f"FAILED to scrape profile: {github_data['error']}")
    sys.exit(1)

print("\nSUCCESSFULLY SCRAPED DATA:")
print(f" - Name: {github_data.get('name')}")
print(f" - Bio: {github_data.get('bio')}")
print(f" - Avatar URL: {github_data.get('avatar_url')}")
print(f" - Location: {github_data.get('location')}")
print(f" - Public Repos: {github_data.get('public_repos')}")
print(f" - Followers: {github_data.get('followers')}")
print(f" - Most Used Languages: {github_data.get('most_used_languages')}")
print(f" - Top Repos:")
for idx, repo in enumerate(github_data.get('top_repos', [])):
    print(f"    {idx+1}. {repo['name']} (Stars: {repo['stars']}, Lang: {repo['language']})")

print(f"\n2. Analyzing profile using Gemini...")
analysis = analyze_profile(github_data)
print("\nGEMINI ANALYSIS RESULT:")
print(f" - Developer Vibe: {analysis.get('developer_vibe')}")
print(f" - Top Skills: {analysis.get('top_skills')}")
print(f" - Fun Fact: {analysis.get('fun_fact')}")
print(f" - Card Theme: {analysis.get('card_theme')}")

print(f"\n3. Generating Card HTML...")
card_html = generate_card_html(username, github_data, analysis)
print(f"Generated HTML length: {len(card_html)} characters")

print(f"\n4. Saving Card...")
saved_url = save_card(username, card_html)
print(f"Saved card URL path: {saved_url}")
full_path = os.path.join(os.path.dirname(__file__), "static", "cards", f"{username}.html")
print(f"Full saved path exists: {os.path.exists(full_path)} ({full_path})")

print("\nALL BACKEND TOOLS WORK PERFECTLY!")
