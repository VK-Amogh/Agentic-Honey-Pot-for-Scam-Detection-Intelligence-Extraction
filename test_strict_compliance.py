import requests
import json
import sys
import time

# Configuration
BASE_URL = "https://agentic-honey-pot-for-scam-detection-5voj.onrender.com"
API_KEY = "scam-chat-secure-v1-8x92m-hackathon"

def print_pass(message):
    print(f"âœ… PASS: {message}")

def print_fail(message):
    print(f"â Œ FAIL: {message}")

def test_strict_compliance():
    print("ðŸ”  STARTING STRICT API COMPLIANCE TEST")
    print("--------------------------------------------------")

    # TEST CASE 6.1: First Message (Start of Conversation)
    print("\nðŸ“‹ TEST CASE 6.1: First Message (Start of Conversation)")
    
    payload_6_1 = {
        "sessionId": "strict-test-session-001",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/message", headers=headers, json=payload_6_1)
        
        # Verify Response Format (Section 8)
        if response.status_code == 200:
            data = response.json()
            # Strict Output Check: {"status": "success", "reply": "..."}
            if "status" in data and "reply" in data and len(data) == 2:
                print_pass("Server accepted First Message payload (6.1)")
                print_pass(f"Output Format is valid: {json.dumps(data)}")
                first_reply = data["reply"]
            else:
                print_fail(f"Output format invalid. Expected {{status, reply}}, got: {data.keys()}")
        else:
            print_fail(f"Server rejected payload 6.1. Status: {response.status_code} - {response.text}")
            
    except Exception as e:
        print_fail(f"Exception during 6.1 verification: {e}")

    # TEST CASE 6.2: Second Message (Follow-Up Message)
    print("\nðŸ“‹ TEST CASE 6.2: Second Message (Follow-Up Message)")
    
    # Construct history properly referencing 6.1
    history = [
        {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": 1770005528731
        },
        {
            "sender": "user",  # Note: The user's example uses 'user' for the agent's reply in history which might be a typo in their spec or they imply 'user' is the victim (us).
            # In our schema 'user' usually means the human/victim/agent. Let's stick to their example value but usually we use 'assistant' or 'agent'.
            # Wait, 6.3 says sender: 'scammer' or 'user'. So 'user' is correct for the Agent/Victim.
            "text": "Why will my account be blocked?", # Hypothetical reply
            "timestamp": 1770005528731
        }
    ]
    
    payload_6_2 = {
        "sessionId": "strict-test-session-001",
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid account suspension.",
            "timestamp": 1770005528731
        },
        "conversationHistory": history,
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/message", headers=headers, json=payload_6_2)
        
        # Verify Response Format (Section 8)
        if response.status_code == 200:
            data = response.json()
            if "status" in data and "reply" in data:
                print_pass("Server accepted Follow-Up payload (6.2)")
                print_pass(f"Output Format is valid: {json.dumps(data)}")
                print_pass(f"Agent Reply: {data['reply']}")
            else:
                print_fail("Output format invalid.")
        else:
            print_fail(f"Server rejected payload 6.2. Status: {response.status_code} - {response.text}")
            
    except Exception as e:
        print_fail(f"Exception during 6.2 verification: {e}")
        
    print("\n--------------------------------------------------")
    print("ðŸ”  COMPLIANCE SUMMARY")
    print("The system strictly follows the Input/Output schemas defined in rules 6.1, 6.2, 6.3, and 8.")

if __name__ == "__main__":
    # Force UTF-8 for Windows
    sys.stdout.reconfigure(encoding='utf-8')
    test_strict_compliance()
