from typing import List, Optional
from pydantic import BaseModel, Field

class Metadata(BaseModel):
    """
    Metadata associated with the communication channel.
    """
    channel: Optional[str] = Field(None, description="Communication channel (e.g., SMS, WhatsApp)")
    language: Optional[str] = Field(None, description="Language of the message")
    locale: Optional[str] = Field(None, description="Regional locale")

class MessageContent(BaseModel):
    """
    Represents the content of a single message.
    """
    sender: str = Field(..., description="Sender type: 'scammer' or 'user'")
    text: str = Field(..., description="The actual text content of the message")
    timestamp: int = Field(..., description="Epoch time format in ms")

class IncomingMessageRequest(BaseModel):
    """
    Structure for the incoming API request representing a message event.
    """
    sessionId: str = Field(..., description="Unique identifier for the session")
    message: MessageContent
    conversationHistory: List[MessageContent] = Field(default_factory=list, description="History of the conversation")
    metadata: Optional[Metadata] = None

class AgentResponse(BaseModel):
    """
    Standard response format for the agent API.
    """
    status: str = Field(..., description="Response status (e.g., 'success')")
    reply: str = Field(..., description="The agent's generated reply")
