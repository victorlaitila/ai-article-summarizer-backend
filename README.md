# AI Article Summarizer Backend

This is the FastAPI **backend** service for the AI Article Summarizer project.  
It provides an endpoint to scrape articles from the web and generate AI-based summaries by calling the Hugging Face Inference API.

Frontend repository can be found [here](https://github.com/victorlaitila/ai-article-summarizer-frontend)

## Live Demo
The app is live here: [AI Article Summarizer](https://victorlaitila.github.io/ai-article-summarizer-frontend/)

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
uvicorn main:app --reload
```

The API will now be available at `http://127.0.0.1:8000`

## API Endpoints

### `POST /scrape-and-summarize`

Scrapes an article from a given URL and returns a summary.

**Request Body:**
```json
{
  "url": "https://example.com/article",
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

## Environment Variables

Create a `.env` file in the project root with:

```
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
```

## Deployment

The backend is deployed on **Fly.io** at: [Server](https://viclait-article-summarizer-backend.fly.dev/)