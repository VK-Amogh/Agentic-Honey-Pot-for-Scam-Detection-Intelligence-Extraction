import requests
import time

URL = "https://agentic-honey-pot-for-scam-detection-5voj.onrender.com"
KEY = "scam-chat-secure-v1-8x92m-hackathon"
HEADERS = {"x-api-key": KEY, "Content-Type": "application/json"}

payload = {
    "sessionId": "quick-test",
    "message": {"sender": "scammer", "text": "Your bank is blocked. Send OTP now.", "timestamp": int(time.time()*1000)},
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
}

print("Testing API response time...")
start = time.time()
r = requests.post(URL + "/", json=payload, headers=HEADERS, timeout=120)
elapsed = time.time() - start

print(f"Time: {elapsed:.2f}s")
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Reply: {data.get('reply', 'ERROR')[:100]}")
else:
    print(f"Error: {r.text}")
