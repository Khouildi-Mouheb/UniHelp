
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from api.schemas import EmailRequest, EmailResponse
from services.email import EmailGenerator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/email", tags=["Email"])

_email_generator = None


def get_email_generator() -> EmailGenerator:
    global _email_generator
    if _email_generator is None:
        _email_generator = EmailGenerator()
    return _email_generator


@router.post("/generate", response_model=EmailResponse)
async def generate_email(request: EmailRequest) -> EmailResponse:

    try:
        generator = get_email_generator()
        
        # Generate content
        email_content = generator.generate_email(
            context=request.context,
            template=request.template
        )
        
        return EmailResponse(
            email_content=email_content,
            subject=request.subject,
            recipient=request.recipient,
            created_at=datetime.now().isoformat()
        )
    except Exception as exc:
        logger.error("Error generating email: %s", exc)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(exc)}")


@router.get("/templates")
async def list_templates():
    try:
        generator = get_email_generator()
        templates = generator.get_templates()
        
        return {
            "templates": templates,
            "total": len(templates)
        }
    except Exception as exc:
        logger.error("Error retrieving templates: %s", exc)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(exc)}")