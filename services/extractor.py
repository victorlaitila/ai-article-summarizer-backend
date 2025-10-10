from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
import trafilatura
from trafilatura.settings import use_config
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from utils.text import clean_text

async def extract_text_from_url(url: str) -> str:
  config = use_config()
  config["EXTRA_HEADERS"] = {
    "User-Agent": (
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )
  }

  downloaded = await run_in_threadpool(lambda: trafilatura.fetch_url(url, config=config))
  if not downloaded:
    raise ValueError("Could not fetch the URL. It may be invalid or blocked.")

  html_text = await run_in_threadpool(lambda: trafilatura.extract(downloaded, output_format="html"))
  if not html_text:
    raise ValueError("Could not extract article text.")

  soup = BeautifulSoup(html_text, "html.parser")
  parts = []

  # Formatting
  for el in soup.find_all(["h1", "h2", "h3", "p", "li"]):
    txt = el.get_text(strip=True)
    if el.name.startswith("h"):
      txt = f"\n{txt}\n"
    parts.append(txt)

  return clean_text("\n\n".join(parts))

async def extract_text_from_file(file: UploadFile) -> str:
  text = ""
  filename = file.filename.lower()
  content_type = file.content_type

  if content_type == "application/pdf" or filename.endswith(".pdf"):
    pdf_reader = PdfReader(file.file)
    for page in pdf_reader.pages:
      text += (page.extract_text() or "") + "\n"
  elif content_type == "text/plain" or filename.endswith(".txt"):
    text = (await file.read()).decode("utf-8")
  else:
    raise ValueError(f"Unsupported file type.")

  text = clean_text(text)
  if not text:
    raise ValueError("File appears to be empty or unreadable.")

  return text
