from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
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

def process_background_tasks(request_data: IncomingMessageRequest, is_scam: bool):
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
        
        total_messages = len(request_data.conversationHistory) + 1
        
        # Report only if Scammed Detected AND (Critical Info found OR Long Conversation)
        if is_scam and (has_critical_info or total_messages >= 5):
            payload = {
                "sessionId": request_data.sessionId,
                "scamDetected": is_scam,
                "totalMessagesExchanged": total_messages,
                "extractedIntelligence": {
                    "bankAccounts": intelligence_data["bankAccounts"],
                    "upiIds": intelligence_data["upiIds"],
                    "phishingLinks": intelligence_data["phishingLinks"],
                    "phoneNumbers": intelligence_data["phoneNumbers"],
                    "ifscCodes": intelligence_data.get("ifscCodes", []),
                    "panNumbers": intelligence_data.get("panNumbers", []),
                    "cryptoWallets": intelligence_data.get("cryptoWallets", []),
                    "suspiciousKeywords": intelligence_data["suspicious_keywords"]
                },
                "agentNotes": agent.get_agent_notes(request_data.sessionId)
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

    try:
        is_scam = detector.analyze(payload.message.text, payload.conversationHistory)
        
        metadata_dict = payload.metadata.model_dump() if payload.metadata else {}
        reply_text = agent.generate_reply(payload.message.text, payload.conversationHistory, metadata_dict, is_scam=is_scam)
        
        background_tasks.add_task(process_background_tasks, payload, is_scam)
        
        return AgentResponse(
            status="success",
            reply=reply_text
        )

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
