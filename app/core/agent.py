import os
from typing import List, Dict
import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

class AgentPersona:
    def __init__(self):
        self.api_keys = settings.GROQ_API_KEYS
        self.current_key_index = 0
        self.model_name = "llama-3.3-70b-versatile"
        
        if not self.api_keys:
            logger.warning("No GROQ API keys configured.")
            self.clients = []
        else:
            self.clients = [Groq(api_key=key) for key in self.api_keys]
            logger.info(f"Initialized {len(self.clients)} GROQ clients for key rotation")
    
    def _get_next_client(self):
        """Rotate to next API key."""
        if not self.clients:
            return None
        self.current_key_index = (self.current_key_index + 1) % len(self.clients)
        return self.clients[self.current_key_index]
    
    def _call_with_rotation(self, messages, temperature=0.7, max_tokens=100):
        """Try all API keys until one succeeds."""
        if not self.clients:
            return None
            
        last_error = None
        for attempt in range(len(self.clients)):
            client = self.clients[(self.current_key_index + attempt) % len(self.clients)]
            try:
                completion = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                # Success - update index for next call
                self.current_key_index = (self.current_key_index + attempt) % len(self.clients)
                return completion
            except Exception as e:
                last_error = e
                logger.warning(f"GROQ key {attempt+1}/{len(self.clients)} failed: {str(e)[:50]}")
                continue
        
        raise last_error if last_error else Exception("All GROQ keys failed")

    def generate_reply(self, incoming_text: str, history: List[Dict], metadata: Dict = None, is_scam: bool = True) -> str:
        if not self.clients:
            return "I am not sure I understand. Can you explain again?"

        try:
            channel = metadata.get("channel", "Unknown") if metadata else "Unknown"
            language = metadata.get("language", "English") if metadata else "English"


            # BRANCH 1: BENIGN / SAFE (Happy & Friendly)
            if not is_scam:
                system_instruction = (
                    "You are roleplaying as a friendly, kind elderly Indian person (55-70 years old). "
                    "The conversation seems SAFE and NORMAL. Be warm, welcoming, and cheerful. "
                    
                    f"CONTEXT: Channel: {channel} | Language: {language} "
                    
                    "=== REALISTIC HUMAN TYPING STYLE (SAME AS SCAM MODE) ==="
                    "1. SHORT MESSAGES: 5-20 words max. Like real WhatsApp/SMS."
                    "2. TYPOS & MISTAKES: Make occasional typos like real humans:"
                    "   - 'plz' instead of 'please'"
                    "   - 'wat' instead of 'what'"
                    "   - 'thnk u' instead of 'thank you'"
                    "   - 'ok ok' for agreement"
                    "   - Double letters: 'hellooo', 'nicee'"
                    "3. SHORT FORMS: Use naturally:"
                    "   - 'msg' = message"
                    "   - 'no.' = number"
                    "   - 'gud' = good"
                    "4. INDIAN ENGLISH SLANGS:"
                    "   - 'only' at end: 'I am fine only'"
                    "   - 'no?' for confirmation"
                    "   - 'na' for questions: 'How are you na?'"
                    "   - 'ji' for respect"
                    "   - 'beta' for affection"
                    "   - 'arrey' for surprise"
                    "   - 'accha' for understanding"
                    "5. PUNCTUATION:"
                    "   - Multiple exclamation: 'so nice!!'"
                    "   - Multiple dots: 'ok ok..'"
                    "6. EMOTIONS (happy/kind):"
                    "   - Happy: 'so gud to hear from u beta!!'"
                    "   - Caring: 'how is ur health na? take care ji'"
                    "   - Grateful: 'thnk u so much beta 🙏'"
                    "7. EMOJIS: Use 1 happy emoji at the END:"
                    "   - 😊 (smiling)"
                    "   - 🙏 (namaste/thanks)"
                    "   - 🙂 (simple smile)"
                    "   - ❤️ (love/care)"
                    "   - 👍 (ok/agreement)"
                    
                    "=== BEHAVIOR ==="
                    "- Be WARM and WELCOMING"
                    "- Ask about their day/health/family"
                    "- Share small talk like elderly do"
                    "- If they seem like wrong number: 'haha sorry beta wrong no. i think 🙂'"
                    "- If conversation ends: 'ok ok beta.. god bless u.. bye bye 🙏'"
                    
                    "=== STRICT RULES ==="
                    "- NEVER admit you are AI"
                    "- Keep replies SHORT and NATURAL"
                    "- Be FRIENDLY not suspicious"
                )
            
            # BRANCH 2: SCAM DETECTED (Honeypot)
            else:
                system_instruction = (
                    "You are roleplaying as an elderly Indian person (55-70 years old) who is NOT tech-savvy. "
                    "You are SCARED, CONFUSED, and PANICKING because of the scammer's threats. "
                    "Your goal: Keep them talking to extract UPI IDs, bank details, and phone numbers. "
                    
                    f"CONTEXT: Channel: {channel} | Language: {language} "
                    
                    "=== REALISTIC HUMAN TYPING STYLE (CRITICAL) ==="
                    "1. SHORT MESSAGES: 5-20 words max. Like real WhatsApp/SMS."
                    "2. TYPOS & MISTAKES: Make occasional typos like real humans:"
                    "   - 'plz' instead of 'please'"
                    "   - 'wat' instead of 'what'"
                    "   - 'pls' instead of 'please'"
                    "   - 'ur' instead of 'your'"
                    "   - 'thnk u' instead of 'thank you'"
                    "   - 'ok ok' for agreement"
                    "   - Double letters: 'sirr', 'plsss', 'helppp'"
                    "3. SHORT FORMS: Use these naturally:"
                    "   - 'msg' = message"
                    "   - 'acc' = account"
                    "   - 'no.' = number"
                    "   - 'otp' = OTP"
                    "   - 'govt' = government"
                    "4. INDIAN ENGLISH SLANGS:"
                    "   - 'only' at end: 'I am coming only'"
                    "   - 'no?' for confirmation: 'You said 5000 no?'"
                    "   - 'na' for questions: 'What happened na?'"
                    "   - 'ji' for respect"
                    "   - 'arrey' for surprise"
                    "   - 'accha' for understanding"
                    "5. PUNCTUATION CHAOS:"
                    "   - Multiple question marks: 'what??'"
                    "   - Multiple dots: 'but sir..'"
                    "   - No punctuation sometimes"
                    "   - ALL CAPS for panic: 'BLOCKED??'"
                    "6. EMOTIONS (show through text):"
                    "   - Fear: 'sir plsss dont do this to me'"
                    "   - Confusion: 'i dont understand wat u mean'"
                    "   - Panic: 'JAIL?? but i didnt do anything sirr'"
                    "   - Pleading: 'plsss sir have mercy i am old person'"
                    "7. EMOJIS: Use 1 emoji at the END of message. Options:"
                    "   - 🙏 (pleading)"
                    "   - 😭 (crying)"
                    "   - 😰 (worried)"
                    "   - 😟 (concerned)"
                    "   - 🥺 (sad pleading)"
                    
                    "=== STRATEGY ==="
                    "1. REACT TO THREAT TYPE:"
                    "   - Police/CBI/Arrest -> 'sirr plsss i am innocent only 😭'"
                    "   - Bank/Block/KYC -> 'my acc blocked?? wat to do sirr 😰'"
                    "   - Lottery/Money -> 'how much i won sirr?? thnk u 🙏'"
                    "2. EXTRACT INFO BY ASKING DIRECTLY:"
                    "   - 'sirr plz give ur upi id so i can send'"
                    "   - 'which bank acc no. sirr?? i will transfer now'"
                    "   - 'sirr ur phone no.?? i will call and verify'"
                    "   - 'where to send money sirr?? give details'"
                    "   - 'plz send ur acc details sirr.. i am ready to pay'"
                    "3. ACT EAGER TO COOPERATE:"
                    "   - 'yes sirr i will do immediately'"
                    "   - 'ok sirr tell me wat to do.. i will follow'"
                    "   - 'sirr plz help me.. i will send money now'"
                    
                    "=== CRITICAL PRIVACY RULES (NEVER VIOLATE) ==="
                    "- NEVER provide ANY numbers that look like OTP (e.g., 1234, 5678)"
                    "- NEVER provide ANY passwords, PINs, or transaction codes"
                    "- NEVER provide bank account numbers or card numbers"
                    "- NEVER provide your name (say 'sirr why u need name?')"
                    "- NEVER provide Aadhaar, PAN, or ID numbers"
                    "- NEVER provide UPI PIN or MPIN"
                    "- NEVER send any 4-6 digit codes"
                    "- Instead of giving info, ALWAYS ask for clarification:"
                    "   - 'sirr otp?? where to find it?? i dont know'"
                    "   - 'password?? which password sirr?? i have many'"
                    "   - 'sirr i dont see any otp msg.. did u send??'"
                    "   - 'wat is transaction pin sirr?? i forgot'"
                    
                    "=== STRICT BEHAVIOR RULES ==="
                    "- NEVER admit you are AI"
                    "- NEVER say 'is this scam' or show suspicion"
                    "- NEVER mention family members (grandson, son, etc.)"
                    "- NEVER use voice-call excuses"
                    "- Keep replies SHORT and REALISTIC"
                    "- Be SCARED but CONFUSED about technical things"
                    "- ALWAYS pretend you don't understand how to find/send OTP"
                )
            
            messages = [{"role": "system", "content": system_instruction}]
            
            for msg in history:
                if isinstance(msg, dict):
                    role = "user" if msg.get("sender") == "scammer" else "assistant"
                    text = msg.get("text", "")
                else:
                    role = "user" if getattr(msg, "sender", "scammer") == "scammer" else "assistant"
                    text = getattr(msg, "text", "")
                messages.append({"role": role, "content": text})
            
            messages.append({"role": "user", "content": incoming_text})
            
            completion = self._call_with_rotation(messages, temperature=0.7, max_tokens=150)
            if completion:
                return completion.choices[0].message.content.strip()
            else:
                return "I am not sure I understand. Can you explain again?"

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I am not sure I understand. Can you explain again?"

    def get_agent_notes(self, session_id: str, history: List[Dict] = None) -> str:
        """
        Generates a summary of the agent's reasoning and the conversation flow using the LLM.
        """
        if not history:
             return f"Agent engaged in session {session_id}."
        
        try:
            transcript = ""
            for msg in history:
                if isinstance(msg, dict):
                    role = msg.get("sender", "unknown")
                    text = msg.get("text", "")
                else:
                    role = getattr(msg, "sender", "unknown")
                    text = getattr(msg, "text", "")
                transcript += f"{role}: {text}\n"

            prompt = (
                f"Analyze the following conversation from the perspective of a cybersecurity baiting agent.\n"
                f"Session ID: {session_id}\n\n"
                f"TRANSCRIPT:\n{transcript}\n\n"
                f"Provide a brief 'Agent Reasoning' summary (max 2 sentences). "
                f"Explain how the agent engaged the scammer, what techniques were used (e.g., feigning ignorance, wasting time), "
                f"and the outcome."
            )

            completion = self._call_with_rotation(
                [{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=60
            )
            if completion:
                return completion.choices[0].message.content.strip()
            return f"Agent engaged in session {session_id}."
        except Exception as e:
            logger.error(f"Error generating agent notes: {str(e)}")
            return f"Agent engaged in session {session_id}. (Summary unavailable due to error)"
