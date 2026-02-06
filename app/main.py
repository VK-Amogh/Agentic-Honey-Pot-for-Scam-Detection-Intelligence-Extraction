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

# Include API Routes at both /api and root level for GUVI compatibility
app.include_router(routes.router, prefix="/api")
app.include_router(routes.router, prefix="")  # Also mount at root for GUVI validator

from fastapi import Header, HTTPException, BackgroundTasks
from app.models.schemas import IncomingMessageRequest, AgentResponse
from app.core.detector import ScamDetector
from app.core.agent import AgentPersona

# Initialize for root POST handler
root_detector = ScamDetector()
root_agent = AgentPersona()

@app.get("/")
@app.head("/")
async def root_get(x_api_key: str = Header(None, alias="x-api-key")):
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

@app.post("/", response_model=AgentResponse)
async def root_post(
    payload: IncomingMessageRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., alias="x-api-key")
):
    """
    POST / handler for GUVI validator - accepts message requests at root.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    try:
        detection_result = root_detector.analyze_with_confidence(payload.message.text, payload.conversationHistory)
        is_scam = detection_result["is_scam"]
        
        metadata_dict = payload.metadata.model_dump() if payload.metadata else {}
        reply_text = root_agent.generate_reply(payload.message.text, payload.conversationHistory, metadata_dict, is_scam=is_scam)
        
        # Add background task for callback
        background_tasks.add_task(routes.process_background_tasks, payload, detection_result, time.time(), reply_text)
        
        return AgentResponse(status="success", reply=reply_text)
    
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
@app.head("/health")
async def health():
    """Alternative health check endpoint for uptime monitors."""
    return {"status": "healthy"}




