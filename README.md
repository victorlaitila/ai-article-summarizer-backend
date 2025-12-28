# AI Article Summarizer Backend

This is the FastAPI **backend** service for the AI Article Summarizer project.  
It provides endpoints to scrape articles from the web and/or generate AI-based summaries by calling the Hugging Face Inference API.

Frontend repository can be found [here](https://github.com/victorlaitila/ai-article-summarizer/)

## Live Demo
The app is live here: [AI Article Summarizer](https://victorlaitila.github.io/ai-article-summarizer/)


NOTE: the demo uses a mock server with static data and does not call the actual backend API in order to avoid deployment costs.

## Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/victorlaitila/ai-article-summarizer-backend.git
cd ai-article-summarizer-backend
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
# with Docker Compose v2+ (recommended)
docker compose up --build

# or with the docker-compose CLI
docker-compose up --build
```

The API will now be available at `http://127.0.0.1:8000`

(If you prefer to run the app locally without Docker for development, you can still start uvicorn directly: uvicorn main:app --reload --port 8080.)

## API Endpoints

### `POST /summarize/text`

Scrapes an article from a given URL and returns the article + summary (or summarizes directly using free text).

**Request Body:**
```json
{
  "type": "url", // or "text"
  "value": "https://example.com/article",
  "mode": "default" // Options: "default", "bullets", "simple"
}
```

**Response:**
```json
{
  "article_text": "...",
  "summary": "..."
}
```

### `POST /summarize/file`

Returns the article + summary based on the file content.

**Request Body:**
```json
{
  "file": "example.pdf",
  "mode": "bullets"
}
```

**Response:**
```json
{
  "article_text": "...",
  "summary": "..."
}
```

## Environment Variables

Create a `.env` file in the project root with:

```
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
```