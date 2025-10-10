from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from slowapi.util import get_remote_address
from slowapi import Limiter

from pydantic import BaseModel
from services.hf_client import summarize_text
from services.extractor import extract_text_from_url, extract_text_from_file

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

class SummarizeInput(BaseModel):
  type: str
  value: str
  mode: str = "default"

@router.post("/summarize-text")
@limiter.limit("5/minute")
async def summarize(request: Request, input: SummarizeInput):
  try:
    if input.type == "url":
      text = await extract_text_from_url(input.value)
    elif input.type == "text":
      text = input.value.strip()
      if not text:
        raise HTTPException(status_code=400, detail="Empty text input.")
    else:
      raise HTTPException(status_code=400, detail=f"Unsupported type '{input.type}'")

    summary = await summarize_text(text, input.mode)
    return {"article_text": text, "summary": summary}
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

@router.post("/summarize-file")
@limiter.limit("5/minute")
async def summarize_file(
  request: Request,
  file: UploadFile = File(...),
  mode: str = Form("default")
):
  try:
    text = await extract_text_from_file(file)
    summary = await summarize_text(text, mode)
    return {"article_text": text, "summary": summary}
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
