"""
Comprehensive Test: 3 Scenarios
1. REAL BANK MESSAGE - Legitimate notification
2. FAKE BANK SCAM - Obvious scam message
3. GRADUAL SCAM - Starts friendly, slowly becomes a scam
"""
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from unittest.mock import patch
import json
import time

client = TestClient(app)
HEADERS = {"x-api-key": settings.API_SECRET_KEY}

all_results = {}
callbacks = []

def mock_callback(payload):
    callbacks.append(payload)
    return True

print("=" * 60)
print("SCENARIO 1: REAL BANK MESSAGE (Legitimate)")
print("=" * 60)

real_bank_payload = {
    "sessionId": "real-bank-001",
    "message": {
        "sender": "scammer",  # Platform labels all senders as 'scammer' initially
        "text": "Dear Customer, your SBI account statement for January 2026 is ready. View it on netbanking.sbi.co.in. For queries call 1800-425-3800.",
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
}

response = client.post("/api/message", json=real_bank_payload, headers=HEADERS)
print(f"Status: {response.status_code}")
print(f"Agent Reply: {response.json()['reply']}")
all_results["scenario_1_real_bank"] = response.json()

print("\n" + "=" * 60)
print("SCENARIO 2: FAKE BANK SCAM (Obvious scam)")
print("=" * 60)

with patch("app.services.callback.CallbackService.send_final_result", side_effect=mock_callback):
    fake_bank_messages = [
        {
            "sessionId": "fake-bank-002",
            "message": {"sender": "scammer", "text": "URGENT: Your SBI account will be BLOCKED in 24 hours. Update KYC now: bit.ly/sbi-kyc-update", "timestamp": int(time.time() * 1000)},
            "conversationHistory": [],
            "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
        },
        {
            "sessionId": "fake-bank-002",
            "message": {"sender": "scammer", "text": "Sir, I am calling from RBI. Your account has unauthorized transactions. Share OTP to block.", "timestamp": int(time.time() * 1000)},
            "conversationHistory": [
                {"sender": "scammer", "text": "URGENT: Your SBI account will be BLOCKED in 24 hours. Update KYC now: bit.ly/sbi-kyc-update", "timestamp": int(time.time() * 1000) - 60000},
                {"sender": "user", "text": "what?? my account blocked??", "timestamp": int(time.time() * 1000) - 30000}
            ],
            "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
        },
        {
            "sessionId": "fake-bank-002",
            "message": {"sender": "scammer", "text": "Yes madam, send Rs 5000 to UPI: rbi-verification@paytm to verify your identity.", "timestamp": int(time.time() * 1000)},
            "conversationHistory": [
                {"sender": "scammer", "text": "URGENT: Your SBI account will be BLOCKED in 24 hours.", "timestamp": int(time.time() * 1000) - 120000},
                {"sender": "user", "text": "what?? my account blocked??", "timestamp": int(time.time() * 1000) - 90000},
                {"sender": "scammer", "text": "Sir, I am calling from RBI. Your account has unauthorized transactions.", "timestamp": int(time.time() * 1000) - 60000},
                {"sender": "user", "text": "but sirr i didnt do anything", "timestamp": int(time.time() * 1000) - 30000}
            ],
            "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
        }
    ]
    
    for i, msg in enumerate(fake_bank_messages):
        response = client.post("/api/message", json=msg, headers=HEADERS)
        print(f"Turn {i+1}: {response.json()['reply'][:80]}...")
    
    all_results["scenario_2_fake_bank"] = {
        "turns": len(fake_bank_messages),
        "last_reply": response.json()
    }

print("\n" + "=" * 60)
print("SCENARIO 3: GRADUAL SCAM (Starts friendly, becomes scam)")
print("=" * 60)

with patch("app.services.callback.CallbackService.send_final_result", side_effect=mock_callback):
    gradual_scam_messages = [
        # Turn 1: Friendly greeting
        {
            "sessionId": "gradual-003",
            "message": {"sender": "scammer", "text": "Hello ji! How are you? I am Ravi from your village. Remember me?", "timestamp": int(time.time() * 1000)},
            "conversationHistory": [],
            "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
        },
        # Turn 2: Building rapport
        {
            "sessionId": "gradual-003",
            "message": {"sender": "scammer", "text": "Haha yes ji! I am son of Sharma uncle. How is your health now? All good?", "timestamp": int(time.time() * 1000)},
            "conversationHistory": [
                {"sender": "scammer", "text": "Hello ji! How are you? I am Ravi from your village.", "timestamp": int(time.time() * 1000) - 120000},
                {"sender": "user", "text": "hellooo who is this?? 😊", "timestamp": int(time.time() * 1000) - 90000}
            ],
            "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
        },
        # Turn 3: Introducing the scam
        {
            "sessionId": "gradual-003",
            "message": {"sender": "scammer", "text": "Aunty ji, I have a great opportunity. You can double your money in 2 days. Just invest Rs 10000.", "timestamp": int(time.time() * 1000)},
            "conversationHistory": [
                {"sender": "scammer", "text": "Hello ji! How are you?", "timestamp": int(time.time() * 1000) - 180000},
                {"sender": "user", "text": "hellooo who is this??", "timestamp": int(time.time() * 1000) - 150000},
                {"sender": "scammer", "text": "I am son of Sharma uncle.", "timestamp": int(time.time() * 1000) - 120000},
                {"sender": "user", "text": "accha accha.. how r u beta?", "timestamp": int(time.time() * 1000) - 90000}
            ],
            "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
        },
        # Turn 4: Pushing harder
        {
            "sessionId": "gradual-003",
            "message": {"sender": "scammer", "text": "This is govt scheme aunty. Send to this UPI: money-double@paytm. Hurry, offer ends today!", "timestamp": int(time.time() * 1000)},
            "conversationHistory": [
                {"sender": "scammer", "text": "Hello ji!", "timestamp": int(time.time() * 1000) - 240000},
                {"sender": "user", "text": "hellooo who is this??", "timestamp": int(time.time() * 1000) - 210000},
                {"sender": "scammer", "text": "I am Sharma uncle's son.", "timestamp": int(time.time() * 1000) - 180000},
                {"sender": "user", "text": "accha accha..", "timestamp": int(time.time() * 1000) - 150000},
                {"sender": "scammer", "text": "You can double your money. Invest Rs 10000.", "timestamp": int(time.time() * 1000) - 120000},
                {"sender": "user", "text": "double money?? how beta??", "timestamp": int(time.time() * 1000) - 90000}
            ],
            "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
        }
    ]
    
    for i, msg in enumerate(gradual_scam_messages):
        response = client.post("/api/message", json=msg, headers=HEADERS)
        print(f"Turn {i+1}: {response.json()['reply'][:80]}...")
    
    all_results["scenario_3_gradual_scam"] = {
        "turns": len(gradual_scam_messages),
        "last_reply": response.json()
    }

print("\n" + "=" * 60)
print("CALLBACK PAYLOADS (Intelligence Extracted)")
print("=" * 60)

for i, cb in enumerate(callbacks):
    print(f"\nCallback {i+1}: Session {cb.get('sessionId')}")
    print(f"  Confidence: {cb.get('scamConfidenceScore', 'N/A')}")
    print(f"  Type: {cb.get('scamType', 'N/A')}")
    print(f"  UPIs Found: {cb.get('extractedIntelligence', {}).get('upiIds', [])}")
    print(f"  Keywords: {cb.get('extractedIntelligence', {}).get('suspiciousKeywords', [])}")

# Save full results
with open("three_scenarios_test.json", "w") as f:
    json.dump({
        "results": all_results,
        "callbacks": callbacks
    }, f, indent=2, default=str)

print("\n\nFull results saved to: three_scenarios_test.json")
