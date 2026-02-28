"""Email models for request/response schemas."""
from pydantic import BaseModel
from typing import Optional


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
