from fastapi import FastAPI
from pydantic import BaseModel
import trafilatura
from trafilatura.settings import use_config
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

# run with: python3 -m uvicorn main:app --reload

app = FastAPI(title="Article Scraper + Summarizer")

origins = [
  "http://localhost:5173", # Vite dev server
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Load summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

class URLInput(BaseModel):
  url: str
  mode: str = "default"

@app.post("/scrape-and-summarize")
async def scrape_and_summarize(input: URLInput):
  # Trafilatura config with User-Agent
  config = use_config()
  config['EXTRA_HEADERS'] = {
    "User-Agent": (
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )
  }

  # Run blocking fetch_url in threadpool
  downloaded = await run_in_threadpool(
    lambda: trafilatura.fetch_url(input.url, config=config)
  )
  if not downloaded:
    return {"error": "Could not fetch the URL. It may be invalid or blocked."}

  # Run blocking extract in threadpool
  text = await run_in_threadpool(lambda: trafilatura.extract(downloaded))
  if not text:
    return {"error": "Could not extract article text."}

  # Run summarization in threadpool based on the selected mode
  try:
    max_chars = 4000
    summary_input = text[:max_chars]

    if input.mode == "default":
      result = await run_in_threadpool(
        lambda: summarizer(summary_input, max_length=150, min_length=50, do_sample=False)
      )
      summary_text = result[0]["summary_text"]

    elif input.mode == "bullets":
      result = await run_in_threadpool(
        lambda: summarizer(summary_input, max_length=180, min_length=60, do_sample=False)
      )
      sentences = result[0]["summary_text"].split(". ")
      summary_text = "\n".join([f"• {s.strip()}" for s in sentences if s.strip()])

    elif input.mode == "simple":
      result = await run_in_threadpool(
        lambda: summarizer(summary_input, max_length=100, min_length=40, do_sample=False)
      )
      summary_text = result[0]["summary_text"]

    else:
      return {"error": f"Invalid summary mode '{input.mode}'"}

  except Exception as e:
    return {"error": f"Summarization failed: {str(e)}"}

  return {"article_text": text, "summary": summary_text}
  