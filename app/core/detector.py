import os
from typing import List, Dict, Tuple
import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

class ScamDetector:
    def __init__(self):
        # Weighted indicators for confidence scoring
        self._high_risk = ["arrest", "jail", "police", "cbi", "cyber crime", "warrant", "fedex", "customs"]
        self._medium_risk = ["block", "suspend", "kyc", "verify", "urgent", "expire", "unauthorized", "otp"]
        self._low_risk = ["lottery", "winner", "refund", "prize", "offer", "cashback"]
        self._indian_scam_keywords = ["bhaiya", "madam", "kripya", "turant", "band", "update karo", "paisa", "aadhar", "pan"]
        
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model_name = "llama-3.3-70b-versatile"
            self.use_llm = True
        else:
            self.use_llm = False

    def analyze_with_confidence(self, message_text: str, history: List[dict] = None) -> Dict:
        """
        Returns dict with is_scam (bool), confidence (0.0-1.0), and reasoning.
        """
        if not self.use_llm:
            return self._heuristic_analyze_with_score(message_text, history)

        try:
            context = ""
            if history:
                for msg in history:
                    if isinstance(msg, dict):
                        sender = msg.get("sender", "unknown")
                        text = msg.get("text", "")
                    else:
                        sender = getattr(msg, "sender", "unknown")
                        text = getattr(msg, "text", "")
                    context += f"{sender}: {text}\n"
            
            prompt = (
                f"Analyze the conversation for scam intent (ANY language/script).\n"
                f"Languages: English, Hindi, South & North Indian Languages.\n"
                f"Scripts: Native or Romanized (Code-mixed).\n"
                f"KNOWN SCAM TYPOLOGIES:\n"
                f"- Digital Arrest / CBI / FedEx / Cyber Crime\n"
                f"- Utility / Electricity Bill\n"
                f"- Job / Task Scams\n"
                f"- Sextortion / Blackmail\n"
                f"- Banking / KYC / UPI\n"
                f"- OLX / Army Officer Fraud\n"
                f"- Stock / IPO / Crypto\n"
                f"- Customs / Gift / Parcel\n"
                f"- 5G / SIM Block\n"
                f"\n"
                f"BENIGN / SAFE (NOT a scam):\n"
                f"- Wrong Number\n"
                f"- Casual Greetings (Hi, Hello, How are you)\n"
                f"- Genuine E-commerce order updates\n"
                f"- Friends/Family chatting\n"
                f"- Normal business inquiries\n"
                f"\n"
                f"Context:\n{context}\n"
                f"New Message: {message_text}\n\n"
                f"Reply in this EXACT format:\n"
                f"SCAM: YES/NO\n"
                f"CONFIDENCE: 0.0-1.0\n"
                f"TYPE: scam_type or NONE"
            )
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50,
                stream=False
            )
            
            result = completion.choices[0].message.content.strip().upper()
            
            # Parse response
            is_scam = "SCAM: YES" in result or "SCAM:YES" in result
            confidence = 0.0
            scam_type = "UNKNOWN"
            
            # Extract confidence
            if "CONFIDENCE:" in result:
                try:
                    conf_part = result.split("CONFIDENCE:")[1].split("\n")[0].strip()
                    confidence = float(conf_part.replace(" ", ""))
                    confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
                except:
                    confidence = 0.85 if is_scam else 0.15
            else:
                confidence = 0.85 if is_scam else 0.15
            
            # Extract type
            if "TYPE:" in result:
                scam_type = result.split("TYPE:")[1].split("\n")[0].strip()
            
            return {
                "is_scam": is_scam,
                "confidence": confidence,
                "scam_type": scam_type if is_scam else "NONE",
                "method": "llm"
            }

        except Exception as e:
            logger.error(f"LLM detection failed: {str(e)}")
            return self._heuristic_analyze_with_score(message_text, history)

    def _heuristic_analyze_with_score(self, message_text: str, history: List[dict]) -> Dict:
        """Fallback heuristic analysis with confidence scoring."""
        full_text = message_text.lower()
        if history:
            for msg in history:
                if isinstance(msg, dict):
                    text = msg.get("text", "")
                else:
                    text = getattr(msg, "text", "")
                full_text += " " + text.lower()
        
        score = 0.0
        matched_keywords = []
        
        # High risk = +0.3 each
        for keyword in self._high_risk:
            if keyword in full_text:
                score += 0.3
                matched_keywords.append(f"HIGH:{keyword}")
        
        # Medium risk = +0.15 each
        for keyword in self._medium_risk:
            if keyword in full_text:
                score += 0.15
                matched_keywords.append(f"MED:{keyword}")
        
        # Low risk = +0.1 each
        for keyword in self._low_risk:
            if keyword in full_text:
                score += 0.1
                matched_keywords.append(f"LOW:{keyword}")
        
        # Indian keywords = +0.05 each (context boost)
        for keyword in self._indian_scam_keywords:
            if keyword in full_text:
                score += 0.05
                matched_keywords.append(f"IND:{keyword}")
        
        # Cap at 1.0
        confidence = min(1.0, score)
        is_scam = confidence >= 0.15  # Single medium-risk keyword should trigger
        
        return {
            "is_scam": is_scam,
            "confidence": round(confidence, 2),
            "scam_type": "HEURISTIC_MATCH" if is_scam else "NONE",
            "method": "heuristic",
            "matched_keywords": matched_keywords
        }

    def analyze(self, message_text: str, history: List[dict] = None) -> bool:
        """Legacy method for backward compatibility."""
        result = self.analyze_with_confidence(message_text, history)
        return result["is_scam"]
