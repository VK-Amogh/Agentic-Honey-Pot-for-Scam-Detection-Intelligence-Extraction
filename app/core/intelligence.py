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
            "phone_number": re.compile(r"(?:\+91[\-\s]?)?[6-9]\d{9}"),
            "bank_account": re.compile(r"\b\d{9,18}\b"),
            "ifsc_code": re.compile(r"[A-Z]{4}0[A-Z0-9]{6}"),
            "pan_card": re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]{1}"),
            "crypto_wallet": re.compile(r"\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59})\b"),
            "url": re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"),
            "suspicious_keywords": [
                "urgent", "verify", "block", "suspend", "kyc", "expire", 
                "refund", "winner", "lottery", "password", "otp", "police", "cbi", "rbi", "arrest"
            ]
        }

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Analyzes the provided text and returns a dictionary of extracted entities.
        """
        results = {
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": [],
            "ifscCodes": [],
            "panNumbers": [],
            "cryptoWallets": []
        }

        # Extract UPI IDs first (to exclude from other patterns)
        results["upiIds"] = list(set(self._patterns["upi_id"].findall(text)))

        # Extract Phone Numbers - 10 digits starting with 6-9 (Indian format)
        phone_matches = list(set(self._patterns["phone_number"].findall(text)))
        # Normalize phone numbers (remove +91 prefix for comparison)
        normalized_phones = set()
        for phone in phone_matches:
            clean_phone = re.sub(r'[\+\-\s]', '', phone)
            if clean_phone.startswith('91') and len(clean_phone) == 12:
                clean_phone = clean_phone[2:]  # Remove 91 prefix
            normalized_phones.add(clean_phone)
        results["phoneNumbers"] = list(set(phone_matches))

        # Extract Bank Accounts - but EXCLUDE phone numbers
        # Bank accounts are typically 11-18 digits, phone numbers are exactly 10 digits starting with 6-9
        all_numbers = list(set(self._patterns["bank_account"].findall(text)))
        bank_accounts = []
        for num in all_numbers:
            # Skip if this is a phone number (10 digits starting with 6-9)
            if len(num) == 10 and num[0] in '6789':
                continue
            # Skip if it matches a normalized phone number
            if num in normalized_phones:
                continue
            # Skip very short numbers that could be OTPs or PINs
            if len(num) < 11:
                continue
            bank_accounts.append(num)
        results["bankAccounts"] = bank_accounts

        # Extract IFSC Codes
        results["ifscCodes"] = list(set(self._patterns["ifsc_code"].findall(text)))

        # Extract PAN Numbers
        results["panNumbers"] = list(set(self._patterns["pan_card"].findall(text)))
        
        # Extract Crypto Wallets
        results["cryptoWallets"] = list(set([m for m in self._patterns["crypto_wallet"].findall(text)]))

        # Extract URLs
        results["phishingLinks"] = list(set(self._patterns["url"].findall(text)))

        # Extract Suspicious Keywords
        lower_text = text.lower()
        found_keywords = [
            kw for kw in self._patterns["suspicious_keywords"] 
            if kw in lower_text
        ]
        results["suspiciousKeywords"] = list(set(found_keywords))

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
