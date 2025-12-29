import os
import json
from databases import Database
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
  raise RuntimeError("Set DATABASE_URL environment variable")

database = Database(DATABASE_URL)

async def connect_db():
  await database.connect()

async def disconnect_db():
  await database.disconnect()

async def create_tables_if_not_exists():
  await database.execute("""
  CREATE TABLE IF NOT EXISTS summaries (
    id SERIAL PRIMARY KEY,
    summary TEXT,
    keywords JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
  );
  """)

async def insert_summary(summary: str, keywords: list | None = None):
  query = (
    "INSERT INTO summaries(summary, keywords) "
    "VALUES (:summary, CAST(:keywords AS jsonb)) "
    "RETURNING id, summary, keywords, created_at"
  )
  values = {"summary": summary, "keywords": json.dumps(keywords or [])}
  try:
    row = await database.fetch_one(query, values=values)
    return dict(row) if row else None
  except Exception:
    raise

async def delete_summary(summary_id: int):
  query = "DELETE FROM summaries WHERE id = :id"
  await database.execute(query, values={"id": summary_id})

async def fetch_summaries(limit: int = 20):
  query = "SELECT id, summary, keywords, created_at FROM summaries ORDER BY created_at DESC LIMIT :limit"
  rows = await database.fetch_all(query, values={"limit": limit})
  return [dict(r) for r in rows]
