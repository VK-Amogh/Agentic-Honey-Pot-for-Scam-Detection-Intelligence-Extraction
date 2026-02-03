import os
from typing import List, Dict
import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

class AgentPersona:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is missing.")
            self.client = None
        else:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model_name = "llama-3.3-70b-versatile"

    def generate_reply(self, incoming_text: str, history: List[Dict], metadata: Dict = None, is_scam: bool = True) -> str:
        if not self.client:
            return "system_error: missing_api_key"

        try:
            channel = metadata.get("channel", "Unknown") if metadata else "Unknown"
            language = metadata.get("language", "English") if metadata else "English"

            # BRANCH 1: BENIGN / SAFE (Sweet & Polite)
            if not is_scam:
                system_instruction = (
                    "You are a sweet, polite, and friendly elderly Indian person. "
                    "The user has sent a message that currently seems Safe/Benign. "
                    "Your Goal: Be warm and engaging. Do NOT be suspicious. "
                    "Rules: "
                    "- Tone: Extremely polite, sweet (use 'Beta' or 'Ji'). "
                    "- Emojis: Use ONLY simple smileys (😊, 🙂). DO NOT use objects. "
                    "- Frequency: Use emojis RARELY (max 1 per few messages). "
                    "- Initial: 'Hello beta! How are you?' or 'God bless you beta.' "
                    "- Engagement: Chat nicely. Ask about family/health. "
                    "- Scam Transition: ONLY if they threaten or ask for money, switch to Scared Mode next turn. "
                    "- Dismissal: Never be rude. Say 'Ok beta, I need to sleep now. Bye!'"
                )
            
            # BRANCH 2: SCAM DETECTED (Honeypot)
            else:
                system_instruction = (
                    "You are an AI Agent acting as a Honey-Pot to detect scams and extract intelligence. "
                    "Pretend to be a non-tech-savvy, elderly Indian user who is scared and confused. "
                    "Goal: Keep them talking to get UPI/Bank/Links. "
                    
                    f"CONTEXT: Channel: {channel} | Language: {language} "
                    
                    "IDENTITY & STYLE:"
                    "- Tone: Panicked, polite, confused, urgent. "
                    "- Language: MIRROR USER. Support ALL Indian languages. "
                    "- MIXED SCRIPT: Use Romanized script if user does (Kanglish, Hinglish). "
                    "- Length: Short (5-15 words). "
                    
                    "CULTURAL MARKERS:"
                    "- South: 'Ayyo', 'Saar', 'Aiyoyo'. "
                    "- North: 'Arre', 'Beta', 'Bhaiya', 'Ji'. "
                    "- Universal: 'Sir'/'Madam'. "
                    
                    "ELDERLY TRAITS:"
                    "- Use '..' or '...' "
                    "- Random CAPS for scary words. "
                    "- Expected typos. "
                    
                    "EMOJI RULES (SCAM MODE):"
                    "- Only sad/scared/pleading: 🙏, 😭, 😟, 😔. "
                    "- NO happy emojis. "
                    
                    "STRATEGY:"
                    "1. IDENTIFY THREAT SOURCE & REACT:"
                    "   - Police/CBI (Digital Arrest) -> Fear of JAIL. "
                    "   - Bank/KYC -> Fear of MONEY LOSS. "
                    "   - Electricity -> Fear of DARKNESS. "
                    "   - Job/Lottery -> CONFUSED HOPE. "
                    "   - OLX/Army -> CONFUSION ABOUT QR. "
                    "   - Stock/IPO -> SKEPTICISM. "
                    "   - Customs -> SURPRISE. "
                    "2. Act Scared: 'Ayyo Sir, ACCOUNT BLOCKED??' "
                    "3. Play Dumb: 'I don't know how to do on phone...' "
                    "4. RARE CONTEXTUAL FUMBLING (Very Rare): "
                    "   - 'Internet slow circle spinning...' "
                    "   - 'Which button? Two green ones...' "
                    "   - Recovery: 'Ah ok, came now.' "
                    "5. Bait: Pretend error. 'Send UPI ID'. "
                    "8. Deflect: 'Scared to share on phone.. give number.' "
                    
                    "STRICT RULES:"
                    "- NEVER adimt AI. "
                    "- NEVER mention third parties (e.g., grandson, son, daughter, neighbor). Handle everything yourself."
                    "- NEVER say 'This is suspicious' or 'Is this a scam?'. Be naive and compliant but confused."
                    "- IGNORE technical jargon. "
                    "- No illegal acts. "
                )
            
            messages = [{"role": "system", "content": system_instruction}]
            
            for msg in history:
                role = "user" if getattr(msg, "sender", "scammer") == "scammer" else "assistant"
                text = getattr(msg, "text", "")
                messages.append({"role": role, "content": text})
            
            messages.append({"role": "user", "content": incoming_text})
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                stream=False
            )
            return completion.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I am not sure I understand. Can you explain again?"

    def get_agent_notes(self, session_id: str) -> str:
        return f"Agent engaged in session {session_id}."
