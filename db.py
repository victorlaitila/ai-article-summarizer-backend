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
    content TEXT,
    keywords JSONB DEFAULT '[]'::jsonb,
    url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
  );
  """)

async def insert_summary(content: str, keywords: list | None = None, url: str | None = None):
  query = (
    "INSERT INTO summaries(content, keywords, url) "
    "VALUES (:content, CAST(:keywords AS jsonb), :url) "
    "RETURNING id, content, keywords, url, created_at"
  )
  values = {"content": content, "keywords": json.dumps(keywords or []), "url": url}
  try:
    row = await database.fetch_one(query, values=values)
    return dict(row) if row else None
  except Exception:
    raise

async def delete_summary(summary_id: int):
  query = "DELETE FROM summaries WHERE id = :id"
  await database.execute(query, values={"id": summary_id})

async def fetch_summaries(limit: int = 20):
  query = "SELECT id, content, keywords, url, created_at FROM summaries ORDER BY created_at DESC LIMIT :limit"
  rows = await database.fetch_all(query, values={"limit": limit})
  return [dict(r) for r in rows]
  