from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Chat request schema."""
    question: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema."""
    answer: str
    sources: list = []
    session_id: str


class DocumentIndexStatus(BaseModel):
    """Document index status schema."""
    is_ready: bool
    document_count: int = 0


class EmailRequest(BaseModel):
    """Email request schema."""
    recipient: str
    subject: str
    context: str
    template: Optional[str] = None


class EmailResponse(BaseModel):
    """Email response schema."""
    email_content: str
    subject: str
    recipient: str
    created_at: str
