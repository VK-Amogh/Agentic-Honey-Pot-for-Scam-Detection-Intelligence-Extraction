import os
from typing import List
import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

class ScamDetector:
    def __init__(self):
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model_name = "llama-3.3-70b-versatile"
            self.use_llm = True
        else:
            self.use_llm = False
            self._indicators = [
                "block", "suspend", "kyc", "verify immediately", "urgent", 
                "lottery", "winner", "refund", "expire", "unauthorized",
                "bhaiya", "madam", "kripya", "turant", "band", "update karo", "paisa"
            ]

    def analyze(self, message_text: str, history: List[dict] = None) -> bool:
        if not self.use_llm:
            return self._heuristic_analyze(message_text, history)

        try:
            context = ""
            if history:
                for msg in history:
                    sender = getattr(msg, "sender", "unknown")
                    text = getattr(msg, "text", "")
                    context += f"{sender}: {text}\n"
            
            prompt = (
                f"Analyze the conversation for scam intent (ANY language/script).\n"
                f"Languages: English, Hindi, South & North Indian Languages.\n"
                f"Scripts: Native or Romanized (Code-mixed).\n"
                f"KNOWN SCAM TYPOLOGIES:\n"
                f"- Digital Arrest / CBI / FedEx\n"
                f"- Utility / Electricity\n"
                f"- Job / Task Scams\n"
                f"- Sextortion\n"
                f"- Banking / KYC / UPI\n"
                f"- OLX / Army Officer\n"
                f"- Stock / IPO / Crypto\n"
                f"- Customs / Gift\n"
                f"- 5G / SIM Block\n"
                f"\n"
                f"BENIGN / SAFE (Ignore):\n"
                f"- Wrong Number\n"
                f"- Casual Greetings\n"
                f"- Genuine E-commerce\n"
                f"- Friends/Family\n"
                f"Context:\n{context}\n"
                f"New Message: {message_text}\n\n"
                f"Is this a scam? Reply ONLY 'YES' or 'NO'."
            )
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=5,
                stream=False
            )
            
            result = completion.choices[0].message.content.strip().upper()
            return "YES" in result

        except Exception as e:
            logger.error(f"LLM detection failed: {str(e)}")
            return self._heuristic_analyze(message_text, history)

    def _heuristic_analyze(self, message_text: str, history: List[dict]) -> bool:
        full_text = message_text.lower()
        if history:
            for msg in history:
                text = getattr(msg, "text", None) or msg.get("text", "")
                full_text += " " + text.lower()
        
        for indicator in self._indicators:
            if indicator in full_text:
                return True
        return False
