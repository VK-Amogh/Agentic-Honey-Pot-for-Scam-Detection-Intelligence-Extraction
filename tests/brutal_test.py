"""
Brutal Stress Test for Agentic Honey-Pot API
Tests concurrent requests and error handling.
"""
import asyncio
import aiohttp
import time
import json

API_URL = "http://localhost:8000/api/message"
API_KEY = "change-me-in-cloud-console"

SCAM_MESSAGES = [
    "Your bank account will be blocked today. Verify immediately.",
    "You have won a lottery of 50 Lakhs. Send UPI ID to claim.",
    "This is CBI. Your Aadhaar is linked to drugs case. Pay fine to avoid arrest.",
    "KYC expired. Update now or SIM will be blocked.",
    "You have a courier from customs. Pay duty of Rs 5000 to release.",
]

async def send_message(session, scammer_id: int, message: str):
    payload = {
        "sessionId": f"brutal-test-session-{scammer_id}",
        "message": {
            "sender": "scammer",
            "text": message,
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    start = time.time()
    try:
        async with session.post(API_URL, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            latency = time.time() - start
            status = resp.status
            body = await resp.text()
            return {"scammer_id": scammer_id, "status": status, "latency": latency, "response": body[:200]}
    except asyncio.TimeoutError:
        return {"scammer_id": scammer_id, "status": "TIMEOUT", "latency": 30.0, "response": "Request timed out"}
    except Exception as e:
        return {"scammer_id": scammer_id, "status": "ERROR", "latency": 0, "response": str(e)}

async def run_brutal_test(num_scammers: int = 10):
    print(f"--- BRUTAL TEST: {num_scammers} Concurrent Scammers ---")
    print(f"Targeting: {API_URL}")
    
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_scammers):
            msg = SCAM_MESSAGES[i % len(SCAM_MESSAGES)]
            tasks.append(send_message(session, i, msg))
        
        results = await asyncio.gather(*tasks)
    
    # Analyze Results
    success_count = sum(1 for r in results if r["status"] == 200)
    fail_count = len(results) - success_count
    avg_latency = sum(r["latency"] for r in results) / len(results)
    max_latency = max(r["latency"] for r in results)
    
    print(f"\n--- RESULTS ---")
    print(f"Success: {success_count}/{num_scammers}")
    print(f"Failed/Timeout: {fail_count}")
    print(f"Avg Latency: {avg_latency:.2f}s")
    print(f"Max Latency: {max_latency:.2f}s")
    
    # Show failures
    for r in results:
        if r["status"] != 200:
            print(f"  [FAIL] Scammer {r['scammer_id']}: {r['status']} - {r['response'][:100]}")
    
    return {"success": success_count, "failed": fail_count, "avg_latency": avg_latency, "max_latency": max_latency}

if __name__ == "__main__":
    asyncio.run(run_brutal_test(10))
