from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler

from config import CORS_ORIGINS
from db import connect_db, disconnect_db, create_tables_if_not_exists
from routes import summarize, summaries

app = FastAPI(title="AI Article Summarizer")

# Rate limiter
app.state.limiter = Limiter(key_func=lambda request: request.client.host)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
  CORSMiddleware,
  allow_origins=CORS_ORIGINS,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Routes
app.include_router(summarize.router)
app.include_router(summaries.router)


@app.on_event("startup")
async def on_startup():
  await connect_db()
  try:
    await create_tables_if_not_exists()
  except Exception:
    pass


@app.on_event("shutdown")
async def on_shutdown():
  await disconnect_db()

@app.get("/health")
def health_check():
  return {"status": "ok"}
