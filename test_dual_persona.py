"""
Test script to verify dual persona and confidence scoring.
"""
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from unittest.mock import patch
import json

client = TestClient(app)

captured_payloads = []

def mock_callback(payload):
    captured_payloads.append(payload)
    print("=== CALLBACK PAYLOAD ===")
    print(json.dumps(payload, indent=2, default=str))
    return True

print("=" * 50)
print("TEST 1: SCAM MESSAGE (Should activate scared persona)")
print("=" * 50)

with patch("app.services.callback.CallbackService.send_final_result", side_effect=mock_callback):
    scam_payload = {
        "sessionId": "test-scam-session",
        "message": {
            "sender": "scammer",
            "text": "This is CBI. Your Aadhaar is linked to money laundering. You will be arrested today. Pay 50000 to avoid jail.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [
            {"sender": "scammer", "text": "Your bank has reported suspicious activity.", "timestamp": 1770005528000},
            {"sender": "user", "text": "What happened sir?", "timestamp": 1770005528100},
            {"sender": "scammer", "text": "Police case registered. Warrant issued.", "timestamp": 1770005528200},
            {"sender": "user", "text": "But I didnt do anything!", "timestamp": 1770005528300},
            {"sender": "scammer", "text": "Transfer money to clear your name.", "timestamp": 1770005528400}
        ],
        "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
    }
    response = client.post("/api/message", json=scam_payload, headers={"x-api-key": settings.API_SECRET_KEY})
    print(f"\nAPI Response (Status {response.status_code}):")
    print(json.dumps(response.json(), indent=2))

print("\n" + "=" * 50)
print("TEST 2: BENIGN MESSAGE (Should activate happy persona)")
print("=" * 50)

benign_payload = {
    "sessionId": "test-benign-session",
    "message": {
        "sender": "scammer",
        "text": "Hello! How are you? I am your old friend from school. Remember me?",
        "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
}
response = client.post("/api/message", json=benign_payload, headers={"x-api-key": settings.API_SECRET_KEY})
print(f"\nAPI Response (Status {response.status_code}):")
print(json.dumps(response.json(), indent=2))

# Save results
with open("dual_persona_test.json", "w") as f:
    json.dump({
        "scam_test": captured_payloads[0] if captured_payloads else None,
        "benign_test": "No callback for benign (as expected)"
    }, f, indent=2, default=str)

print("\nResults saved to dual_persona_test.json")
