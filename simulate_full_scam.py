
import requests
import json
import time
import sys
import re
import os

# Add the current directory to sys.path so we can import app modules if needed
sys.path.append(os.getcwd())

# FORCE UTF-8 for Windows output
sys.stdout.reconfigure(encoding='utf-8')

# Configuration
BASE_URL = "https://agentic-honey-pot-for-scam-detection-5voj.onrender.com"
API_KEY = "scam-chat-secure-v1-8x92m-hackathon"
SESSION_ID = "simulation-session-full-001"

# Import local intelligence extractor for client-side verification
try:
    from app.core.intelligence import IntelligenceExtractor
    extractor = IntelligenceExtractor()
except ImportError:
    print("Warning: Could not import IntelligenceExtractor. Make sure you are running this from the project root.")
    extractor = None

def print_separator():
    print("-" * 60)

def simulate_message(text, history):
    print(f"\nðŸš« SCAMMER: {text}")
    
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "sessionId": SESSION_ID,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": history
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/message", headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply")
            print(f"ðŸ¤– AGENT:   {reply}")
            
            # Update History
            history.append(payload["message"])
            history.append({
                "sender": "agent",
                "text": reply,
                "timestamp": int(time.time() * 1000)
            })
            return history
        else:
            print(f"â Œ Error: {response.status_code} - {response.text}")
            return history
            
    except Exception as e:
        print(f"â Œ Connection Error: {e}")
        return history

def run_simulation():
    print_separator()
    print("ðŸ”„ STARTING FULL SCAM SIMULATION")
    print_separator()
    
    history = []
    
    # SCENARIO: Lottery Scam
    scenarios = [
        "Hello, I am calling from SBI bank. You have won a lottery of 50 lakhs.",
        "To claim this amount, you need to pay a small processing fee.",
        "The fee is just Rs. 5000. Please pay immediately to secure your prize.",
        "You can send the money to my UPI ID: scammer-raj@okaxis",
        "Or you can transfer to Account Number: 987654321012, IFSC: SBIN0001234",
        "Please do it fast, valid only for 10 minutes."
    ]
    
    full_text_for_verification = ""
    
    for msg in scenarios:
        history = simulate_message(msg, history)
        full_text_for_verification += msg + " "
        time.sleep(1) # Small delay for realism
        
    print_separator()
    print("âœ… SIMULATION COMPLETE")
    print_separator()
    
    # Client-side Verification of Rules
    if extractor:
        print("\nðŸ”  VERIFYING EXTRACTION LOGIC (Client-Side Simulation)")
        print("Based on the conversation, the server should have extracted:")
        
        intelligence_data = extractor.extract(full_text_for_verification)
        
        # Construct the JSON payload that would be sent to the callback
        expected_payload = {
            "sessionId": SESSION_ID,
            "scamDetected": True,
            "totalMessagesExchanged": len(history),
            "extractedIntelligence": {
                "bankAccounts": intelligence_data["bankAccounts"],
                "upiIds": intelligence_data["upiIds"],
                "phishingLinks": intelligence_data["phishingLinks"],
                "phoneNumbers": intelligence_data["phoneNumbers"],
                "suspiciousKeywords": intelligence_data["suspicious_keywords"]
            },
            "agentNotes": "Simulation notes not available client-side"
        }
        
        print(json.dumps(expected_payload, indent=2))
        
        if len(intelligence_data["upiIds"]) > 0:
            print("\nâœ… SUCCESS: UPI ID detected locally.")
        if len(intelligence_data["bankAccounts"]) > 0:
            print("âœ… SUCCESS: Bank Account detected locally.")
        if "lottery" in intelligence_data["suspicious_keywords"]:
             print("âœ… SUCCESS: Suspicious keywords detected locally.")

        # Save to file
        with open("scam_result.json", "w", encoding="utf-8") as f:
            json.dump(expected_payload, f, indent=2)
        print("\nðŸ“‚ JSON Report saved to 'scam_result.json'")

if __name__ == "__main__":
    import os
    run_simulation()
