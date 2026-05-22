# 🐙 GitHub Dev Card Generator

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-8E75C2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)
[![FastMCP](https://img.shields.io/badge/FastMCP-orange?style=for-the-badge)](https://github.com/jlowin/fastmcp)

An AI-powered developer profile analyzer and custom developer card generator. Built with **Google's Agent Development Kit (ADK)**, **Gemini 2.5 Flash**, **FastMCP**, and **FastAPI**, this application fetches public GitHub information, analyzes developer metrics, generates a customized persona card, and serves it through a sleek, modern UI.

---

## ✨ Features

- **⚡ Instant Profile Scraping**: Leverages the GitHub REST API to securely fetch developer profiles and top-starred repositories.
- **🧠 Gemini-Powered Analysis**: Utilizes **Gemini 2.5 Flash** to extract developer insights, define custom skills, write a personalized "developer vibe," and generate a clever "fun fact."
- **🎨 Dynamic Persona Themes**: Automatically categorizes developers into one of five custom-tailored visual themes:
  - 💻 `Hacker` (Sleek dark green neon theme)
  - 🛠️ `Builder` (Professional clean blue theme)
  - 🔬 `Researcher` (Intellectual purple academic theme)
  - 🎨 `Designer` (Vibrant creative pink theme)
  - 🛡️ `Open-Source Hero` (Empathetic green community theme)
- **🖥️ Premium Frontend UI**: Features an immersive dark mode dashboard with skeleton loading animations, smooth micro-interactions, responsive previewing, and a one-click **Share URL** utility.
- **🐳 Dockerized Architecture**: Containerized setup utilizing `docker-compose` for rapid local spin-up.

---

## 🏗️ Architecture Flow

The system orchestrates a beautiful multi-step agent flow:

```mermaid
graph TD
    User([User entering Username]) -->|HTTP POST /generate| API[FastAPI Backend]
    API -->|Google ADK Runner| Agent[github_card_agent]
    Agent -->|1. scrape_github| MCP[FastMCP Server]
    MCP -->|GitHub API| GitHub[(GitHub API)]
    GitHub -.->|Profile & Repos| MCP
    MCP -.->|Scraped JSON| Agent
    Agent -->|2. analyze_profile| MCP
    MCP -->|Gemini 2.5 Flash| Gemini[Google Gemini API]
    Gemini -.->|Insights & Theme JSON| MCP
    MCP -.->|Analysis Results| Agent
    Agent -->|3. generate_card_html| MCP
    MCP -.->|Styled HTML Card| Agent
    Agent -->|4. save_card| MCP
    MCP -->|Write File| Disk[(Static Disk /cards/)]
    API -->|Return JSON & Card URL| User
```

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **AI/Agent Orchestration**: Google Agent Development Kit (ADK) & FastMCP (Model Context Protocol)
- **Model**: Gemini 2.5 Flash
- **Frontend**: Vanilla HTML5, CSS3 (Modern HSL variables & CSS transitions), Vanilla JS
- **Containerization**: Docker & Docker Compose

---

## 🚀 Getting Started

### 📋 Prerequisites

- **Python 3.11+** installed locally
- A **Google Gemini API Key** (Get one from [Google AI Studio](https://aistudio.google.com/))
- *(Optional)* A **GitHub Personal Access Token** (To prevent API rate limits for profile scraping)

---

### 💻 Local Run (Manual)

#### 1. Configure Environment Variables
In the root directory, copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_here
```

#### 2. Run the Backend
Navigate to the `backend` directory, create a virtual environment, install requirements, and run the FastAPI server:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
The backend will boot up at `http://localhost:8080`.

#### 3. Run the Frontend
You can open `frontend/index.html` directly in your browser or run a simple local web server:
```bash
cd frontend
python -m http.server 3000
```
Visit `http://localhost:3000` in your web browser.

---

### 🐳 Running with Docker Compose (Recommended)

Make sure you have Docker and Docker Compose installed.

1. **Spin up the stack**:
   ```bash
   docker-compose up --build
   ```
2. **Access the application**:
   - Frontend: `http://localhost:3000`
   - Backend: `http://localhost:8080`

---

## 📂 Project Structure

```text
github-card-generator/
├── backend/
│   ├── .venv/                 # Local python virtual environment (ignored)
│   ├── static/                # Serves static assets & generated HTML cards
│   │   └── cards/             # Generated cards saved here
│   ├── agent.py               # Google ADK agent definition & prompt
│   ├── main.py                # FastAPI endpoints & entrypoint
│   ├── mcp_server.py          # FastMCP server tools (scraping, Gemini analysis, saving)
│   ├── Dockerfile             # Container configuration for backend
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── index.html             # Sleek frontend SPA
│   └── Dockerfile             # Simple static server configuration for frontend
├── docker-compose.yml         # Easy multi-container management
├── .gitignore                 # Safe workspace tracking exclusion
└── README.md                  # This documentation
```

---

## 📜 License

This project is licensed under the MIT License.
