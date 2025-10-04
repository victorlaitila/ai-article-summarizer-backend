import os
import re
import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from pydantic import BaseModel
import trafilatura
from trafilatura.settings import use_config
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Article Scraper + Summarizer")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [
  "http://localhost:5173",
  "https://victorlaitila.github.io"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

load_dotenv()
HF_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")
if not HF_TOKEN:
  raise RuntimeError("Please set HUGGINGFACE_API_TOKEN environment variable")

HF_MODEL = "facebook/bart-large-cnn"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# Input schema
class URLInput(BaseModel):
  url: str
  mode: str = "default"

def call_hf_api(text, max_length=150, min_length=50):
  payload = {
    "inputs": text,
    "parameters": {"max_length": max_length, "min_length": min_length}
  }
  response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=90)
  response.raise_for_status()
  result = response.json()
  if isinstance(result, list) and "summary_text" in result[0]:
    return result[0]["summary_text"]
  raise RuntimeError(f"Hugging Face API error: {result}")

@app.post("/scrape-and-summarize")
@limiter.limit("5/minute")
async def scrape_and_summarize(request: Request, input: URLInput):
  # Trafilatura config
  config = use_config()
  config['EXTRA_HEADERS'] = {
    "User-Agent": (
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )
  }

  # Fetch and extract article
  downloaded = await run_in_threadpool(lambda: trafilatura.fetch_url(input.url, config=config))
  if not downloaded:
    return {"error": "Could not fetch the URL. It may be invalid or blocked."}

  html_text = await run_in_threadpool(lambda: trafilatura.extract(downloaded, output_format="html"))
  if not html_text:
    return {"error": "Could not extract article text."}

  soup = BeautifulSoup(html_text, "html.parser")

  # Extract text with spacing between paragraphs/headings
  readable_text_parts = []
  for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "p", "li"]):
    text_piece = element.get_text(strip=True)
    if element.name.startswith("h"):
      text_piece = f"\n{text_piece}\n"
    readable_text_parts.append(text_piece)

  text = "\n\n".join(readable_text_parts)

  # Sanitize text
  text = text.strip()
  text = re.sub(r'\n{2,}', '\n\n', text)  

  # Summarization
  try:
    max_chars = 4000
    summary_input = text[:max_chars]

    if input.mode == "default":
      summary_text = await asyncio.to_thread(call_hf_api, summary_input, 150, 50)
    elif input.mode == "bullets":
      summary_raw = await asyncio.to_thread(call_hf_api, summary_input, 180, 60)
      sentences = summary_raw.split(". ")
      summary_text = "\n".join([f"• {s.strip()}" for s in sentences if s.strip()])
    elif input.mode == "simple":
      summary_text = await asyncio.to_thread(call_hf_api, summary_input, 100, 40)
    else:
      return {"error": f"Invalid summary mode '{input.mode}'"}

  except Exception as e:
    return {"error": f"Summarization failed: {str(e)}"}

  return {"article_text": text, "summary": summary_text}

@app.get("/health")
def health_check():
  return {"status": "ok"}
  