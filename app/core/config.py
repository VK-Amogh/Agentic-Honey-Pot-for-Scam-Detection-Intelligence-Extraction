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
    # In a real deployment, this should be loaded from a secure vault or environment variable.
    # We default to a placeholder for local development if not set.
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "default-insecure-key-change-me")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    
    # External Services
    EVALUATION_ENDPOINT: str = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

settings = Settings()
