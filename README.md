# 🐙 GitHub Dev Card Generator

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-8E75C2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud_Run-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/run)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)

An AI-powered developer profile analyzer and custom developer card generator. Built with **Google's Agent Development Kit (ADK)**, **Gemini 1.5 Flash**, **FastMCP**, and **FastAPI**, this application fetches public GitHub information, analyzes developer metrics, generates a customized persona card, and serves it through a sleek, modern UI.

---

## 🌐 Live Demo

You can access the live application here:
- **Frontend UI**: [https://github-card-frontend-1009339555607.us-central1.run.app](https://github-card-frontend-1009339555607.us-central1.run.app)
- **Backend API**: [https://github-card-backend-1009339555607.us-central1.run.app](https://github-card-backend-1009339555607.us-central1.run.app)

---

## ✨ Features

- **⚡ Instant Profile Scraping**: Leverages the GitHub REST API to securely fetch developer profiles and top-starred repositories.
- **🧠 Gemini-Powered Analysis**: Utilizes **Gemini 1.5 Flash** (via `gemini-flash-latest`) to extract developer insights, define custom skills, and generate a personalized persona.
- **🎨 Dynamic Persona Themes**: Automatically categorizes developers into visual themes like Hacker, Builder, Researcher, and more.
- **🖥️ Premium Frontend UI**: immersive dark mode dashboard with skeleton loading animations and responsive previewing.
- **🐳 Cloud-Ready**: Fully containerized with Docker and optimized for deployment on **Google Cloud Run**.

---

## 🏗️ Architecture Flow

```mermaid
graph TD
    User([User entering Username]) -->|HTTP POST /generate| API[FastAPI Backend]
    API -->|Google ADK Runner| Agent[github_card_agent]
    Agent -->|1. scrape_github| MCP[FastMCP Server]
    MCP -->|GitHub API| GitHub[(GitHub API)]
    GitHub -.->|Profile & Repos| MCP
    MCP -.->|Scraped JSON| Agent
    Agent -->|2. analyze_profile| MCP
    MCP -->|Gemini 1.5 Flash| Gemini[Google Gemini API]
    Gemini -.->|Insights & Theme JSON| MCP
    MCP -.->|Analysis Results| Agent
    Agent -->|3. generate_card_html| MCP
    MCP -.->|Styled HTML Card| Agent
    Agent -->|4. save_card| MCP
    MCP -->|Write File| Disk[(Static Disk /cards/)]
    API -->|Return JSON & Card URL| User
```

---

## 🚀 Getting Started

### 💻 Local Development

1. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and add your keys:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   GITHUB_TOKEN=your_github_token_here
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   - Frontend: `http://localhost:3000`
   - Backend: `http://localhost:8080`

### ☁️ Deployment

The project is pre-configured for Google Cloud Run. Use the provided Dockerfiles for automated builds and deployments.
