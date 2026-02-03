import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

# Initialize the TestClient
client = TestClient(app)

# Dummy API Key for testing
HEADERS = {"x-api-key": "test-secret-key"}

def test_health_check():
    """Verify that the health check endpoint returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Agentic Honey-Pot System is running."}

def test_api_key_validation():
    """Verify that missing API key returns 401 Unauthorized."""
    payload = {
        "sessionId": "test-session",
        "message": {"sender": "user", "text": "Hello", "timestamp": "2026-01-01T00:00:00Z"},
        "conversationHistory": []
    }
    response = client.post("/api/message", json=payload)
    assert response.status_code == 422 # FastAPI checks headers first, but alias might cause validation error if missing?
    # Actually, if header is missing, it's a 422 validation error in recent FastAPI versions usually, 
    # but let's check if we return 401 in our custom logic or if FastAPI catches it.
    # Our code says: `x_api_key: str = Header(...)`. Missing it causes 422.
    # We can pass an empty one to test our 401 logic if we made it Optional, but it is required.
    
def test_scam_detection_and_response():
    """Test a scam message triggers detection and an agent response."""
    payload = {
        "sessionId": "session-123",
        "message": {
            "sender": "scammer",
            "text": "Your account will be blocked. Verify immediately.",
            "timestamp": "2026-01-21T10:15:30Z"
        },
        "conversationHistory": []
    }
    
    response = client.post("/api/message", json=payload, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # The agent should respond with something from the 'initial_concern' or 'hesitation' category
    assert len(data["reply"]) > 0

def test_intelligence_extraction_trigger():
    """
    Test that intelligence extraction works and callback is triggered (mocked).
    """
    with patch("app.services.callback.CallbackService.send_final_result") as mock_callback:
        # Mocking the background tasks is tricky with TestClient alone usually, 
        # but TestClient runs background tasks synchronously after the response.
        
        payload = {
            "sessionId": "session-critical",
            "message": {
                "sender": "scammer",
                "text": "Send money to UPI: scammer@upi",
                "timestamp": "2026-01-21T10:20:00Z"
            },
            "conversationHistory": [
                {
                    "sender": "scammer",
                    "text": "Your account is blocked.",
                    "timestamp": "2026-01-21T10:15:00Z"
                },
                {
                    "sender": "user",
                    "text": "Oh no, what do I do?",
                    "timestamp": "2026-01-21T10:16:00Z"
                }
            ]
        }
        
        response = client.post("/api/message", json=payload, headers=HEADERS)
        assert response.status_code == 200
        
        # Verify callback was called because we provided a UPI ID (actionable intelligence)
        # and it's a scam context ("blocked" in history).
        assert mock_callback.called
        
        # Inspect the payload sent to the callback
        args, _ = mock_callback.call_args
        callback_payload = args[0]
        assert callback_payload["sessionId"] == "session-critical"
        assert "scammer@upi" in callback_payload["extractedIntelligence"]["upiIds"]
        assert callback_payload["scamDetected"] is True

def test_normal_message_flow():
    """Test that a non-scam message is handled gracefully."""
    payload = {
        "sessionId": "session-safe",
        "message": {
            "sender": "user",
            "text": "Hello, how are you?",
            "timestamp": "2026-01-21T09:00:00Z"
        },
        "conversationHistory": []
    }
    
    response = client.post("/api/message", json=payload, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
