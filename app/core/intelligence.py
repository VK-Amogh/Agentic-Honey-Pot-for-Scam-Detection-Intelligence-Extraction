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
            # UPI IDs: user@bank format (e.g., name@ybl, name@paytm, name@oksbi)
            "upi_id": re.compile(r"[a-zA-Z0-9\.\-_]+@[a-zA-Z]{2,}", re.IGNORECASE),
            
            # Phone: +91/+1/etc OR plain 10-digit starting with 6-9
            "phone_number": re.compile(r"(?:\+\d{1,3}[\-\s]?)?[6-9]\d{9}"),
            
            # Bank account: 9-18 digits (Indian bank accounts are typically 9-18 digits)
            "bank_account": re.compile(r"\b\d{9,18}\b"),
            
            # Aadhaar: 12 digits (may have spaces)
            "aadhaar": re.compile(r"\b\d{4}[\s]?\d{4}[\s]?\d{4}\b"),
            
            # IFSC: 4 letters + 0 + 6 alphanumeric
            "ifsc_code": re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", re.IGNORECASE),
            
            # PAN: 5 letters + 4 digits + 1 letter
            "pan_card": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE),
            
            # Crypto wallets
            "crypto_wallet": re.compile(r"\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59})\b"),
            
            # URLs
            "url": re.compile(r"https?://[^\s<>\"{}|\\^`\[\]]+"),
            
            # Email addresses
            "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
            
            "suspicious_keywords": [
                "urgent", "verify", "block", "suspend", "kyc", "expire", 
                "refund", "winner", "lottery", "password", "otp", "police", 
                "cbi", "rbi", "arrest", "fedex", "customs", "parcel", "seized"
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
            "cryptoWallets": [],
            "aadhaarNumbers": [],
            "emails": []
        }

        # 1. Extract UPI IDs (exclude common email domains)
        upi_matches = self._patterns["upi_id"].findall(text)
        email_domains = ['.com', '.in', '.org', '.net', '.co', '.io', '.edu', '.gov']
        upi_ids = []
        for upi in upi_matches:
            if not any(upi.lower().endswith(domain) for domain in email_domains):
                upi_ids.append(upi.lower())
        results["upiIds"] = list(set(upi_ids))

        # 2. Extract Emails
        results["emails"] = list(set(self._patterns["email"].findall(text)))

        # 3. Extract Phone Numbers with deduplication
        phone_matches = self._patterns["phone_number"].findall(text)
        seen_base_numbers = {}
        for phone in phone_matches:
            clean = re.sub(r'[\+\-\s]', '', phone)
            base_number = clean[-10:] if len(clean) >= 10 else clean
            if base_number not in seen_base_numbers:
                seen_base_numbers[base_number] = phone
            elif phone.startswith('+'):
                seen_base_numbers[base_number] = phone
        results["phoneNumbers"] = list(seen_base_numbers.values())
        phone_digits = set(seen_base_numbers.keys())

        # 4. Extract Aadhaar Numbers (12 digits)
        aadhaar_matches = self._patterns["aadhaar"].findall(text)
        aadhaar_numbers = [re.sub(r'\s', '', a) for a in aadhaar_matches]
        valid_aadhaar = []
        for num in aadhaar_numbers:
            if len(num) == 12 and num not in phone_digits:
                # Aadhaar doesn't start with 0 or 1
                if num[0] not in '01':
                    valid_aadhaar.append(num)
        results["aadhaarNumbers"] = list(set(valid_aadhaar))
        aadhaar_digits = set(valid_aadhaar)

        # 5. Extract Bank Accounts (9-18 digits, excluding phone/aadhaar)
        all_numbers = self._patterns["bank_account"].findall(text)
        bank_accounts = []
        for num in all_numbers:
            # Skip phone numbers (10 digits starting with 6-9)
            if len(num) == 10 and num[0] in '6789':
                continue
            # Skip if already identified as phone
            if num in phone_digits:
                continue
            # Skip if it's aadhaar (12 digits starting 2-9)
            if len(num) == 12 and num in aadhaar_digits:
                continue
            # Valid bank account
            bank_accounts.append(num)
        results["bankAccounts"] = list(set(bank_accounts))

        # 6. Extract IFSC Codes
        results["ifscCodes"] = list(set([c.upper() for c in self._patterns["ifsc_code"].findall(text)]))

        # 7. Extract PAN Numbers
        results["panNumbers"] = list(set([p.upper() for p in self._patterns["pan_card"].findall(text)]))
        
        # 8. Extract Crypto Wallets
        results["cryptoWallets"] = list(set(self._patterns["crypto_wallet"].findall(text)))

        # 9. Extract URLs (phishing links)
        results["phishingLinks"] = list(set(self._patterns["url"].findall(text)))

        # 10. Extract Suspicious Keywords
        lower_text = text.lower()
        found_keywords = [kw for kw in self._patterns["suspicious_keywords"] if kw in lower_text]
        results["suspiciousKeywords"] = list(set(found_keywords))

        return results

    def merge_intelligence(self, current: Dict, new_data: Dict) -> Dict:
        """
        Merges new intelligence data into an existing intelligence dictionary, 
        ensuring uniqueness of values.
        """
        for key in current:
            if key in new_data:
                current[key] = list(set(current[key] + new_data[key]))
        return current
