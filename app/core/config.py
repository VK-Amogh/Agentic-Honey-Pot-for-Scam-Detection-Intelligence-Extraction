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
    
    # GROQ API Keys - supports up to 4 keys for rotation
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_API_KEY_2: str = os.getenv("GROQ_API_KEY_2")
    GROQ_API_KEY_3: str = os.getenv("GROQ_API_KEY_3")
    GROQ_API_KEY_4: str = os.getenv("GROQ_API_KEY_4")
    
    @property
    def GROQ_API_KEYS(self) -> list:
        """Returns list of all available GROQ API keys."""
        keys = []
        if self.GROQ_API_KEY:
            keys.append(self.GROQ_API_KEY)
        if self.GROQ_API_KEY_2:
            keys.append(self.GROQ_API_KEY_2)
        if self.GROQ_API_KEY_3:
            keys.append(self.GROQ_API_KEY_3)
        if self.GROQ_API_KEY_4:
            keys.append(self.GROQ_API_KEY_4)
        return keys
    
    # External Services
    EVALUATION_ENDPOINT: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

settings = Settings()

