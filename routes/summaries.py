from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db import insert_summary, delete_summary, fetch_summaries

router = APIRouter(prefix="/summaries", tags=["summaries"])

class SaveSummaryInput(BaseModel):
  summary: str
  keywords: Optional[List[str]] = None

@router.post("", status_code=201)
async def save_summary(payload: SaveSummaryInput):
  if not payload.summary:
    raise HTTPException(status_code=400, detail="summary is required")
  try:
    inserted_id = await insert_summary(summary=payload.summary, keywords=payload.keywords)
    return {"id": inserted_id}
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
