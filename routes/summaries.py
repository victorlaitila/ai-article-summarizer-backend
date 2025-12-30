from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db import insert_summary, delete_summary, fetch_summaries

router = APIRouter(prefix="/summaries", tags=["summaries"])

class SaveSummaryInput(BaseModel):
  content: str
  keywords: Optional[List[str]] = None
  url: Optional[str] = None

@router.post("", status_code=201)
async def save_summary(payload: SaveSummaryInput):
  if not payload.content:
    raise HTTPException(status_code=400, detail="content is required")
  try:
    created = await insert_summary(content=payload.content, keywords=payload.keywords, url=payload.url)
    if not created:
      raise HTTPException(status_code=500, detail="Failed to create summary")
    return created
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{summary_id}")
async def remove_summary(summary_id: int):
  try:
    await delete_summary(summary_id)
    return {"status": "deleted"}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

@router.get("", name="List summaries")
async def list_summaries(limit: int = Query(50, gt=0, le=500)):
  try:
    rows = await fetch_summaries(limit=limit)
    return {"items": rows}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
