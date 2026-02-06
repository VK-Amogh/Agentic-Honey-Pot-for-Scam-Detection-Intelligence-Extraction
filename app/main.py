import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import routes

# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic Honey-Pot API for detecting scams and extracting intelligence."
)

class ProcessTimeHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response

app.add_middleware(ProcessTimeHeaderMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for the hackathon context
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(routes.router, prefix="/api")

from fastapi import Header, HTTPException

@app.get("/")
@app.head("/")
async def root(x_api_key: str = Header(None, alias="x-api-key")):
    """
    Health check endpoint with optional API key validation.
    GUVI validator uses this to test endpoint reachability and auth.
    """
    # If API key is provided, validate it
    if x_api_key:
        if x_api_key != settings.API_SECRET_KEY:
            raise HTTPException(status_code=403, detail="Invalid API key")
        return {
            "status": "active",
            "service": "agentic-honeypot",
            "mode": "validation",
            "message": "API key valid. Ready for messages."
        }
    # No API key = simple health check
    return {"message": "Agentic Honey-Pot System is running."}

@app.get("/health")
@app.head("/health")
async def health():
    """Alternative health check endpoint for uptime monitors."""
    return {"status": "healthy"}


