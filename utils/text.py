import re
from typing import Tuple
from config import SUMMARY_MODES

def clean_text(text: str) -> str:
  text = text.strip()
  return re.sub(r'\n{2,}', '\n\n', text)

def get_summary_params(mode: str) -> Tuple[int, int]:
  if mode not in SUMMARY_MODES:
    raise ValueError(f"Invalid summary mode '{mode}'")
  params = SUMMARY_MODES[mode]
  return params["max_length"], params["min_length"]
