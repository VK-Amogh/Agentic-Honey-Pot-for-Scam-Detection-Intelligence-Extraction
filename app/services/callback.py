import requests
import logging
import json
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Reusable session for connection pooling (faster)
_session = requests.Session()

class CallbackService:
    """
    Manages communication with the external evaluation platform.
    """

    @staticmethod
    def send_final_result(payload: Dict[str, Any]) -> bool:
        """
        Sends the final extracted intelligence to the evaluation endpoint.
        """
        endpoint = settings.EVALUATION_ENDPOINT
        
        try:
            logger.info(f"Sending final result for session {payload.get('sessionId')}")
            
            response = _session.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5  # Faster timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info("Successfully reported final results.")
                return True
            else:
                logger.error(f"Callback failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Network error: {str(e)[:50]}")
            return False
