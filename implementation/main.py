"""FastAPI application for UniHelp - RAG Assistant with Email Generator."""
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from api.routes import chat, documents, email
from utils.logging import setup_logging

# Setup logging
setup_logging(logging.INFO)
logger = logging.getLogger(__name__)

# Get the base directory
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

print("=" * 50)
print("🚀 UNIHELP APPLICATION STARTING")
print("=" * 50)
print(f"📂 Base directory: {BASE_DIR}")
print(f"📁 Templates directory: {TEMPLATES_DIR}")
print(f"📁 Static directory: {STATIC_DIR}")
print(f"📁 Templates exist: {TEMPLATES_DIR.exists()}")
print(f"📁 Static exist: {STATIC_DIR.exists()}")
print("=" * 50)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
print("✅ Jinja2 templates initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    print("\n" + "=" * 50)
    print("🔄 LIFESPAN: Application starting...")
    print("=" * 50)
    
    logger.info("Application demarree")
    print("✅ Application started successfully")
    yield
    print("\n" + "=" * 50)
    print("🔄 LIFESPAN: Application shutting down...")
    print("=" * 50)
    logger.info("Application arretee")
    print("✅ Application stopped")


# Create FastAPI app
app = FastAPI(
    title="UniHelp API",
    description="RAG Assistant avec Generation d'Emails",
    version="1.0.0",
    lifespan=lifespan
)
print("✅ FastAPI app created")
# In main.py, before routes
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] etc.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    print(f"✅ Static files mounted from {STATIC_DIR}")
else:
    print(f"⚠️ Static directory not found: {STATIC_DIR}")

# Include API routes
print("\n📦 Loading API routes:")
app.include_router(chat.router)
print("   - Chat router loaded")
app.include_router(documents.router)
print("   - Documents router loaded")
app.include_router(email.router)
print("   - Email router loaded")


# HTML Pages (serve templates)
@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Serve the chat page."""
    print(f"\n📄 PAGE REQUEST: / (Chat page)")
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request):
    """Serve the documents management page."""
    print(f"\n📄 PAGE REQUEST: /documents")
    return templates.TemplateResponse("documents.html", {"request": request})


@app.get("/email", response_class=HTMLResponse)
async def email_page(request: Request):
    """Serve the email generator page."""
    print(f"\n📄 PAGE REQUEST: /email")
    return templates.TemplateResponse("email.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    print(f"\n❤️ HEALTH CHECK: /health")
    return {
        "status": "healthy",
        "service": "UniHelp API"
    }


print("\n" + "=" * 50)
print("✅ ALL MODULES LOADED SUCCESSFULLY")
print("=" * 50)
print("🌐 Server will start at: http://localhost:8000")
print("📚 API docs available at: http://localhost:8000/docs")
print("=" * 50 + "\n")

if __name__ == "__main__":
    import uvicorn
    
    print("🎯 Starting uvicorn server...")
    print("   Press Ctrl+C to stop\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )