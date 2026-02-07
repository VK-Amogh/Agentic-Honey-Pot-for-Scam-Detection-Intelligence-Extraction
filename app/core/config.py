import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Settings:
    """
    Application configuration settings.
    """
    PROJECT_NAME: str = "Agentic Honey-Pot System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Security
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "default-insecure-key-change-me")
    
    # GROQ API Keys - supports up to 8 keys for load balancing
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_API_KEY_2: str = os.getenv("GROQ_API_KEY_2")
    GROQ_API_KEY_3: str = os.getenv("GROQ_API_KEY_3")
    GROQ_API_KEY_4: str = os.getenv("GROQ_API_KEY_4")
    GROQ_API_KEY_5: str = os.getenv("GROQ_API_KEY_5")
    GROQ_API_KEY_6: str = os.getenv("GROQ_API_KEY_6")
    GROQ_API_KEY_7: str = os.getenv("GROQ_API_KEY_7")
    GROQ_API_KEY_8: str = os.getenv("GROQ_API_KEY_8")
    
    @property
    def GROQ_API_KEYS(self) -> list:
        """Returns list of all available GROQ API keys."""
        keys = []
        for attr in ['GROQ_API_KEY', 'GROQ_API_KEY_2', 'GROQ_API_KEY_3', 'GROQ_API_KEY_4',
                     'GROQ_API_KEY_5', 'GROQ_API_KEY_6', 'GROQ_API_KEY_7', 'GROQ_API_KEY_8']:
            key = getattr(self, attr, None)
            if key:
                keys.append(key)
        return keys
    
    # External Services
    EVALUATION_ENDPOINT: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

settings = Settings()

