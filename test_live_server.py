"""
Test Live Server - 3 Scenarios
"""
import requests
import json
import time

BASE_URL = "https://agentic-honey-pot-for-scam-detection-5voj.onrender.com"
API_KEY = "scam-chat-secure-v1-8x92m-hackathon"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

print("=" * 60)
print("TESTING LIVE SERVER")
print(f"URL: {BASE_URL}")
print("=" * 60)

# Test health first
print("\n[1] HEALTH CHECK...")
try:
    r = requests.get(f"{BASE_URL}/", timeout=30)
    print(f"Status: {r.status_code} - {r.json()}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("[2] SCENARIO 1: REAL BANK MESSAGE (Legitimate)")
print("=" * 60)

real_bank = {
    "sessionId": "live-test-real-001",
    "message": {
        "sender": "scammer",
        "text": "Dear Customer, your SBI account statement for January 2026 is ready. View on netbanking.sbi.co.in",
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
}

try:
    r = requests.post(f"{BASE_URL}/api/message", json=real_bank, headers=HEADERS, timeout=60)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("[3] SCENARIO 2: FAKE BANK SCAM")
print("=" * 60)

fake_bank = {
    "sessionId": "live-test-scam-002",
    "message": {
        "sender": "scammer",
        "text": "URGENT: Your SBI account will be BLOCKED. Send Rs 5000 to UPI: rbi-verify@paytm immediately!",
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [
        {"sender": "scammer", "text": "This is RBI. Your account has illegal transactions.", "timestamp": int(time.time() * 1000) - 60000},
        {"sender": "user", "text": "what?? my account?", "timestamp": int(time.time() * 1000) - 30000}
    ],
    "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
}

try:
    r = requests.post(f"{BASE_URL}/api/message", json=fake_bank, headers=HEADERS, timeout=60)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("[4] SCENARIO 3: GRADUAL SCAM (Friendly -> Scam)")
print("=" * 60)

gradual = {
    "sessionId": "live-test-gradual-003",
    "message": {
        "sender": "scammer",
        "text": "Aunty ji send money to UPI: double-money@paytm. Govt scheme, 100% guarantee!",
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [
        {"sender": "scammer", "text": "Hello ji! I am Ravi from your village.", "timestamp": int(time.time() * 1000) - 180000},
        {"sender": "user", "text": "hellooo who is this??", "timestamp": int(time.time() * 1000) - 150000},
        {"sender": "scammer", "text": "I am Sharma uncle's son. How are you?", "timestamp": int(time.time() * 1000) - 120000},
        {"sender": "user", "text": "accha accha beta.. im fine", "timestamp": int(time.time() * 1000) - 90000},
        {"sender": "scammer", "text": "Aunty I have a great investment opportunity for you.", "timestamp": int(time.time() * 1000) - 60000},
        {"sender": "user", "text": "wat opportunity beta??", "timestamp": int(time.time() * 1000) - 30000}
    ],
    "metadata": {"channel": "WhatsApp", "language": "Hinglish", "locale": "IN"}
}

try:
    r = requests.post(f"{BASE_URL}/api/message", json=gradual, headers=HEADERS, timeout=60)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
