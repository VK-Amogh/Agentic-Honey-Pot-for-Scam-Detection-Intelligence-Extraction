import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "scam-chat-secure-v1-8x92m-hackathon"

def run_test():
    print(f"Testing Local API at {BASE_URL}...")
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"Health: {resp.status_code} {resp.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # 2. Message Test
    payload = {
        "sessionId": "local-test-01",
        "message": {
            "text": "Hello, I am calling from SBI bank. You won lottery.",
            "timestamp": int(time.time()*1000),
            "sender": "scammer"
        },
        "conversationHistory": []
    }
    
    headers = {"x-api-key": API_KEY}
    
    try:
        start = time.time()
        resp = requests.post(f"{BASE_URL}/api/message", json=payload, headers=headers)
        print(f"Message Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        print(f"Headers: {resp.headers}")
        
        if "X-Process-Time" in resp.headers:
            print("✅ Speed Header Present")
        else:
            print("❌ Speed Header MISSING")
            
    except Exception as e:
        print(f"Message Test Failed: {e}")

if __name__ == "__main__":
    run_test()
