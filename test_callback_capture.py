"""
Test script to capture and display the callback payload sent to GUVI.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from unittest.mock import patch
import json

client = TestClient(app)

# Mock the callback to capture the payload
def mock_callback(payload):
    print("=== CALLBACK PAYLOAD (sent to GUVI) ===")
    print(json.dumps(payload, indent=2, default=str))
    with open("callback_payload.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    return True

with patch("app.services.callback.CallbackService.send_final_result", side_effect=mock_callback):
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Send money to UPI: fraud@upi immediately or your account will be blocked!",
            "timestamp": 1770005528731
        },
        "conversationHistory": [
            {"sender": "scammer", "text": "Your bank account will be suspended. Verify now.", "timestamp": 1770005528000},
            {"sender": "user", "text": "Oh no! What do I do sir?", "timestamp": 1770005528100},
            {"sender": "scammer", "text": "Transfer Rs 5000 to avoid suspension.", "timestamp": 1770005528200},
            {"sender": "user", "text": "But I dont have money...", "timestamp": 1770005528300},
            {"sender": "scammer", "text": "Then give your bank details for verification.", "timestamp": 1770005528400}
        ],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    response = client.post("/api/message", json=payload, headers={"x-api-key": settings.API_SECRET_KEY})

print("\n=== API RESPONSE ===")
print(json.dumps(response.json(), indent=2))
print("\nCallback payload saved to: callback_payload.json")
