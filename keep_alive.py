"""
Keep-Alive Script - Sends actual API requests to keep server warm
Prevents cold starts by keeping the honeypot API loaded
"""
import requests
import time
import logging
import json

# Configuration
SERVER_URL = "https://agentic-honey-pot-for-scam-detection-5voj.onrender.com"
API_KEY = "scam-chat-secure-v1-8x92m-hackathon"
PING_INTERVAL = 60  # 1 minute

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# Warmup payload - lightweight, won't trigger callback
WARMUP_PAYLOAD = {
    "sessionId": "warmup-ping",
    "message": {
        "sender": "scammer",
        "text": "Hello",  # Simple benign message
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [],
    "metadata": {"channel": "warmup", "language": "English", "locale": "IN"}
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def warm_server():
    """Send actual API request to keep server warm."""
    try:
        # Update timestamp for each request
        WARMUP_PAYLOAD["message"]["timestamp"] = int(time.time() * 1000)
        
        response = requests.post(
            f"{SERVER_URL}/api/message",
            json=WARMUP_PAYLOAD,
            headers=HEADERS,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")[:40]  # First 40 chars
            logger.info(f"✓ Server WARM - Reply: {reply}...")
        else:
            logger.warning(f"⚠ Status: {response.status_code}")
        return True
        
    except requests.exceptions.Timeout:
        logger.error("✗ Timeout - server waking up, next ping will be fast")
        return False
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False

def health_ping():
    """Simple health check - no GROQ usage."""
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=30)
        if response.status_code == 200:
            logger.info(f"✓ Health OK")
        return True
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        return False

def main():
    print("=" * 50)
    print("KEEP-WARM SERVICE (Smart Mode)")
    print(f"Server: {SERVER_URL}")
    print("Health ping every 1 min, Full API warmup every 5 min")
    print("=" * 50)
    
    ping_count = 0
    
    try:
        while True:
            ping_count += 1
            
            # Every 5th ping = full API warmup (uses GROQ)
            # Otherwise = simple health ping (no GROQ)
            if ping_count % 5 == 1:
                logger.info(f"#{ping_count} - Full API warmup")
                warm_server()
            else:
                logger.info(f"#{ping_count} - Health ping")
                health_ping()
            
            time.sleep(PING_INTERVAL)
    except KeyboardInterrupt:
        print(f"\n\nStopped. Total pings: {ping_count}")

if __name__ == "__main__":
    main()
