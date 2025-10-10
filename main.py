from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler

from config import CORS_ORIGINS
from routes import summarize

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

@app.get("/health")
def health_check():
  return {"status": "ok"}
