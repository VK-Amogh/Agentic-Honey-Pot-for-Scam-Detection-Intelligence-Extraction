import re
from typing import List, Dict, Set

class IntelligenceExtractor:
    """
    Responsible for parsing conversation text to extract actionable intelligence
    such as bank account numbers, UPI IDs, phone numbers, and potential phishing links.
    """

    def __init__(self):
        # Compiled patterns for efficiency
        self._patterns = {
            "upi_id": re.compile(r"[\w\.\-_]+@[\w]+", re.IGNORECASE),
            # simplistic pattern for Indian mobile numbers
            "phone_number": re.compile(r"(?:\+91[\-\s]?)?[6-9]\d{9}"),
            "bank_account": re.compile(r"\b\d{9,18}\b"),
            "url": re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"),
            "suspicious_keywords": [
                "urgent", "verify", "block", "suspend", "kyc", "expire", 
                "refund", "winner", "lottery", "password", "otp"
            ]
        }

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Analyzes the provided text and returns a dictionary of extracted entities.
        
        Args:
            text: The full conversation text or message content to analyze.
            
        Returns:
            A dictionary containing lists of unique extracted items.
        """
        results = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }

        # Extract UPI IDs
        results["upiIds"] = list(set(self._patterns["upi_id"].findall(text)))

        # Extract Phone Numbers
        results["phoneNumbers"] = list(set(self._patterns["phone_number"].findall(text)))

        # Extract Bank Accounts (Contextual validation would be better, but regex serves as a first pass)
        results["bankAccounts"] = list(set(self._patterns["bank_account"].findall(text)))

        # Extract URLs
        results["phishingLinks"] = list(set(self._patterns["url"].findall(text)))

        # Extract Suspicious Keywords
        lower_text = text.lower()
        found_keywords = [
            kw for kw in self._patterns["suspicious_keywords"] 
            if kw in lower_text
        ]
        results["suspicious_keywords"] = list(set(found_keywords))

        return results

    def merge_intelligence(self, current: Dict, new_data: Dict) -> Dict:
        """
        Merges new intelligence data into an existing intelligence dictionary, 
        ensuring uniqueness of values.
        """
        for key in current:
            if key in new_data:
                # Combine lists and remove duplicates
                current[key] = list(set(current[key] + new_data[key]))
        return current
