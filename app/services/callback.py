import requests
import logging
from typing import Dict, Any
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class CallbackService:
    """
    Manages communication with the external evaluation platform.
    """

    @staticmethod
    def send_final_result(payload: Dict[str, Any]) -> bool:
        """
        Sends the final extracted intelligence to the evaluation endpoint.

        Args:
            payload: The dictionary containing the session results.

        Returns:
            True if the request was successful, False otherwise.
        """
        endpoint = settings.EVALUATION_ENDPOINT
        
        try:
            logger.info(f"Sending final result to {endpoint} for session {payload.get('sessionId')}")
            
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info("Successfully reported final results.")
                return True
            else:
                logger.error(f"Failed to report results. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Network error during callback: {str(e)}")
            return False
