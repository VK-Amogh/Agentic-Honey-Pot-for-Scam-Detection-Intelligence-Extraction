from fastapi import APIRouter, Header, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from app.models.schemas import IncomingMessageRequest, AgentResponse
from app.core.detector import ScamDetector
from app.core.agent import AgentPersona
from app.core.intelligence import IntelligenceExtractor
from app.services.callback import CallbackService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

detector = ScamDetector()
agent = AgentPersona()
extractor = IntelligenceExtractor()

import time

def process_background_tasks(request_data: IncomingMessageRequest, detection_result: dict, start_time: float, agent_reply: str):
    try:
        full_text = request_data.message.text
        for msg in request_data.conversationHistory:
            full_text += " " + msg.text
            
        intelligence_data = extractor.extract(full_text)
        
        has_critical_info = (
            len(intelligence_data["bankAccounts"]) > 0 or 
            len(intelligence_data["upiIds"]) > 0 or
            len(intelligence_data["phishingLinks"]) > 0
        )
        
        total_messages = len(request_data.conversationHistory) + 2
        
        # Build complete chat transcript
        chat_transcript = [m.model_dump() for m in request_data.conversationHistory]
        chat_transcript.append(request_data.message.model_dump())
        chat_transcript.append({
            "sender": "agent",
            "text": agent_reply,
            "timestamp": int(time.time() * 1000)
        })
        
        is_scam = detection_result.get("is_scam", False)
        confidence = detection_result.get("confidence", 0.0)
        scam_type = detection_result.get("scam_type", "UNKNOWN")
        
        # Report only if Scammed Detected AND (Critical Info found OR Long Conversation)
        if is_scam and (has_critical_info or total_messages >= 5):
            payload = {
                "sessionId": request_data.sessionId,
                "scamDetected": is_scam,
                "scamConfidenceScore": round(confidence, 2),
                "scamType": scam_type,
                "totalMessagesExchanged": total_messages,
                "extractedIntelligence": {
                    "bankAccounts": intelligence_data["bankAccounts"],
                    "upiIds": intelligence_data["upiIds"],
                    "phishingLinks": intelligence_data["phishingLinks"],
                    "phoneNumbers": intelligence_data["phoneNumbers"],
                    "ifscCodes": intelligence_data.get("ifscCodes", []),
                    "panNumbers": intelligence_data.get("panNumbers", []),
                    "cryptoWallets": intelligence_data.get("cryptoWallets", []),
                    "aadhaarNumbers": intelligence_data.get("aadhaarNumbers", []),
                    "emails": intelligence_data.get("emails", []),
                    "suspiciousKeywords": intelligence_data.get("suspiciousKeywords", [])
                },
                "conversationTranscript": chat_transcript,
                "agentNotes": agent.get_agent_notes(request_data.sessionId, request_data.conversationHistory),
                "performanceMetrics": {
                    "processingTime": f"{time.time() - start_time:.4f}s",
                    "detectionMethod": detection_result.get("method", "unknown")
                }
            }
            CallbackService.send_final_result(payload)
            
    except Exception as e:
        logger.error(f"Error in background processing: {str(e)}")

@router.post("/message", response_model=AgentResponse)
async def handle_message(
    payload: IncomingMessageRequest, 
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., alias="x-api-key")
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    start_time = time.time()

    try:
        # Get detection result with confidence score
        detection_result = detector.analyze_with_confidence(payload.message.text, payload.conversationHistory)
        is_scam = detection_result["is_scam"]
        
        metadata_dict = payload.metadata.model_dump() if payload.metadata else {}
        reply_text = agent.generate_reply(payload.message.text, payload.conversationHistory, metadata_dict, is_scam=is_scam)
        
        background_tasks.add_task(process_background_tasks, payload, detection_result, start_time, reply_text)
        
        return AgentResponse(
            status="success",
            reply=reply_text
        )

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Support for GUVI endpoint tester - accepts GET/OPTIONS/HEAD
@router.get("/message")
@router.head("/message")
async def message_get():
    """GET endpoint for health check / endpoint verification."""
    return {"status": "ready", "endpoint": "/api/message", "method": "POST required for messages"}

@router.options("/message")
async def message_options():
    """OPTIONS endpoint for CORS preflight."""
    return JSONResponse(
        content={"methods": ["POST", "GET", "OPTIONS", "HEAD"]},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "x-api-key, content-type"
        }
    )

