import requests
import json
import os

# Configuration
BASE_URL = "https://agentic-honey-pot-for-scam-detection-5voj.onrender.com"
API_KEY = "scam-chat-secure-v1-8x92m-hackathon"

def test_health():
    print(f"Testing Health Check at {BASE_URL}/ ...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("âœ… Health Check Passed!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"âŒ Health Check Failed: Status {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"âŒ Connection Error: {e}")
        return False

def test_api():
    print(f"\nTesting API Endpoint at {BASE_URL}/api/message ...")
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "sessionId": "verify-script-session-001",
        "message": {
            "sender": "scammer",
            "text": "Hello, I am calling from your bank. We need your password to secure your account immediately.",
            "timestamp": 1716200000000
        },
        "conversationHistory": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/message", headers=headers, json=payload)
        
        if response.status_code == 200:
            print("âœ… API Test Passed!")
            data = response.json()
            print(f"Reply: {data.get('reply')}")
            print(f"Status: {data.get('status')}")
            return True
        else:
            print(f"âŒ API Test Failed: Status {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"âŒ Connection Error: {e}")
        return False

if __name__ == "__main__":
    health_ok = test_health()
    if health_ok:
        test_api()
