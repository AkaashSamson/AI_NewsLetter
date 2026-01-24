# AI Video Digest (WIP)

> 🚧 **Project Status:** Under Active Development (Alpha)

AI Video Digest is a personalized newsletter engine that transforms your favorite YouTube channels into a concise, readable feed. Instead of watching hours of video, get high-quality AI summaries of the latest uploads from your subscribed technical channels.

## 🎯 Goal
Create a personalized feed and email newsletter based on the youtube videos uploaded by your subscribed channels.

## ✨ Key Features
- **Smart Polling**: Automatically detects new videos from your monitored channels.
- **AI Summaries**: Uses LLMs (Groq/Gemini) to generate concise summaries from video transcripts.
- **Deduplication**: Intelligent tracking ensures you never see the same update twice.
- **Rate Limiting**: Built-in jitter and limits to respect YouTube's boundaries.
- **Dashboard**: A clean Streamlit interface to manage channels and view the latest feed.

## 🏗️ Architecture
The project follows a robust Service-Oriented Architecture (SOA):
- **Database**: PostgreSQL (Dockerized)
- **Backend**: Python Service Layer (`ChannelManager`, `FeedManager`)
- **Frontend**: Streamlit
- **ORM**: SQLAlchemy

## 🚀 Getting Started

### Prerequisites
- Docker Desktop
- Python 3.10+
- API Keys for Groq or Gemini

### Installation
1.  **Clone the repo**
2.  **Start the Database**:
    ```bash
    cd docker
    docker-compose up -d
    ```
3.  **Install Dependencies**:
    ```bash
    uv add sqlalchemy psycopg2-binary pydantic-settings streamlit youtube-transcript-api feedparser requests
    ```
4.  **Run the App**:
    ```bash
    streamlit run src/app/main.py
    ```

## 📝 Documentation
- [Architecture Reference](docs/architecture_reference.md)
- [Pipeline Analysis](docs/pipeline_code_analysis.md)