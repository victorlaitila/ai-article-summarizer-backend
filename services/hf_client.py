import requests
import asyncio
from config import HF_API_URL, HEADERS
from utils.text import get_summary_params

def call_hf_api(text: str, max_length: int, min_length: int) -> str:
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

async def summarize_text(text: str, mode: str) -> str:
  from utils.text import clean_text
  text = clean_text(text)
  if not text:
    raise ValueError("No text provided for summarization.")

  max_length, min_length = get_summary_params(mode)

  if mode == "bullets":
    summary_raw = await asyncio.to_thread(call_hf_api, text[:4000], max_length, min_length)
    sentences = summary_raw.split(". ")
    return "\n".join([f"• {s.strip()}" for s in sentences if s.strip()])

  return await asyncio.to_thread(call_hf_api, text[:4000], max_length, min_length)
