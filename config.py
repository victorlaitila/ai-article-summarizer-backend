import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN")
HF_MODEL = os.environ.get("HF_MODEL")

if not HF_TOKEN:
  raise RuntimeError("Set HUGGINGFACE_API_TOKEN environment variable")
if not HF_MODEL:
  raise RuntimeError("Set HF_MODEL environment variable")

HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

CORS_ORIGINS = [
  "http://localhost:5173",
  "https://victorlaitila.github.io"
]

# Summarization mode parameters
SUMMARY_MODES = {
  "default": {"max_length": 150, "min_length": 50},
  "bullets": {"max_length": 180, "min_length": 60},
  "simple": {"max_length": 100, "min_length": 40},
}

MAX_CHARS = 4000
