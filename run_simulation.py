"""
Full Scam Simulation Test
"""
import requests
import json
import time

URL = "https://agentic-honey-pot-for-scam-detection-5voj.onrender.com"
KEY = "scam-chat-secure-v1-8x92m-hackathon"
HEADERS = {"x-api-key": KEY, "Content-Type": "application/json"}

print("=" * 60)
print("FULL SCAM SIMULATION TEST")
print("=" * 60)

# Multi-turn scam conversation
turns = [
    {
        "msg": "This is CBI officer. Your Aadhaar linked to money laundering case.",
        "history": []
    },
    {
        "msg": "FIR registered. Arrest warrant issued. You must cooperate now.",
        "history": [
            {"sender": "scammer", "text": "This is CBI officer. Your Aadhaar linked to money laundering.", "timestamp": int(time.time()*1000)-120000},
            {"sender": "user", "text": "sirr plsss what happened??", "timestamp": int(time.time()*1000)-90000}
        ]
    },
    {
        "msg": "To clear your name, transfer Rs 50000 to UPI: cbi-clearance@paytm immediately.",
        "history": [
            {"sender": "scammer", "text": "This is CBI officer. Your Aadhaar linked to money laundering.", "timestamp": int(time.time()*1000)-180000},
            {"sender": "user", "text": "sirr plsss what happened??", "timestamp": int(time.time()*1000)-150000},
            {"sender": "scammer", "text": "FIR registered. Arrest warrant issued.", "timestamp": int(time.time()*1000)-120000},
            {"sender": "user", "text": "ARREST?? but i didnt do anything sirr", "timestamp": int(time.time()*1000)-90000}
        ]
    }
]

results = []

for i, turn in enumerate(turns):
    print(f"\n--- TURN {i+1} ---")
    print(f"Scammer: {turn['msg'][:60]}...")
    
    payload = {
        "sessionId": "full-test-session",
        "message": {"sender": "scammer", "text": turn["msg"], "timestamp": int(time.time()*1000)},
        "conversationHistory": turn["history"],
        "metadata": {"channel": "WhatsApp", "language": "English", "locale": "IN"}
    }
    
    start = time.time()
    r = requests.post(f"{URL}/api/message", json=payload, headers=HEADERS, timeout=120)
    latency = time.time() - start
    
    if r.status_code == 200:
        data = r.json()
        reply = data.get("reply", "ERROR")
        print(f"Agent: {reply}")
        print(f"Latency: {latency:.2f}s")
        results.append({"turn": i+1, "reply": reply, "latency": latency})
    else:
        print(f"ERROR: {r.status_code} - {r.text}")
        results.append({"turn": i+1, "error": r.text})

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)

# Save results
with open("simulation_results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\nResults saved to simulation_results.json")
