# UniHelp - RAG Assistant with Email Generator

A comprehensive Retrieval-Augmented Generation (RAG) application with FastAPI backend and modern web dashboard for document indexing, question answering, and automated email generation.

## Features

🔍 **Document Management**
- Upload and manage PDF documents
- Automatic FAISS indexing
- Vector-based document retrieval
- Support for Groq and OpenAI LLMs

💬 **Chat Features**
- RAG-powered question answering
- Source document tracking
- Real-time streaming responses

✉️ **Email Generation**
- AI-powered email composition
- Template support
- Context-aware content generation
- Multiple tone options

## Project Structure

```
unihelp/
├── implementation/           # Main application
│   ├── api/                 # API routes (chat, documents, email)
│   ├── core/                # RAG pipeline & LLM providers
│   ├── models/              # Data models
│   ├── services/            # Business logic services
│   ├── static/              # CSS, JavaScript files
│   ├── templates/           # Jinja2 HTML templates
│   ├── utils/               # Utilities and exceptions
│   ├── docs/                # Document storage (PDFs)
│   ├── faiss_index/         # Vector index storage
│   ├── config.py            # Application configuration
│   ├── main.py              # FastAPI entry point
│   └── requirements.txt      # Python dependencies
├── .env                     # Environment configuration (create this)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Prerequisites

- Python 3.10 or higher
- API key (OpenAI or Groq)

## Installation

### 1. Navigate to Project Directory

```
bash
cd unihelp
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```
powershell
python -m venv uni-env
.\uni-env\Scripts\Activate
```

**Windows (CMD):**
```
cmd
python -m venv uni-env
uni-env\Scripts\activate.bat
```

**Linux/Mac:**
```
bash
python -m venv uni-env
source uni-env/bin/activate
```

### 3. Install Dependencies

```
bash
cd implementation
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root (`unihelp/.env`):

**Option A: Groq (Free, Fast)**
```
env
GROQ_API_KEY=gsk_your_key_here
LLM_MODEL=mixtral-8x7b-32768
```

**Option B: OpenAI**
```
env
OPENAI_API_KEY=sk_your_key_here
LLM_MODEL=gpt-4o-mini
```

> **Note:** Get your API keys from:
> - Groq: https://console.groq.com/
> - OpenAI: https://platform.openai.com/

## Running the Application

### Start the FastAPI Server

From the `implementation` directory:

```
bash
python main.py
```

Or with uvicorn:

```
bash
python -m uvicorn main:app --reload --port 8000
```

### Access the Application

Open your browser and navigate to:

| Page | URL |
|------|-----|
| Chat | http://localhost:8000 |
| Documents | http://localhost:8000/documents |
| Email Generator | http://localhost:8000/email |
| API Documentation | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

## Usage Workflow

1. **Start the server** - Run `python main.py` in the implementation directory

2. **Upload Documents**
   - Go to http://localhost:8000/documents
   - Upload PDF files
   - Click "Build Index" to create the search index

3. **Ask Questions**
   - Go to http://localhost:8000
   - Ask questions about your uploaded documents
   - View source citations

4. **Generate Emails**
   - Go to http://localhost:8000/email
   - Enter context and parameters
   - Generate AI-powered emails

## API Endpoints

### Chat
- `POST /api/chat/ask` - Ask a question
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear chat history

### Documents
- `POST /api/documents/upload` - Upload PDF
- `GET /api/documents/list` - List documents
- `DELETE /api/documents/{filename}` - Delete document
- `POST /api/documents/rebuild-index` - Rebuild search index

### Email
- `POST /api/email/generate` - Generate email
- `GET /api/email/templates` - List templates

### System
- `GET /health` - Health check
- `GET /api/docs` - Swagger UI

## Configuration

### LLM Provider Selection

The app automatically detects the available API key:
- `GROQ_API_KEY` in `.env` → Uses Groq
- `OPENAI_API_KEY` in `.env` → Uses OpenAI

### Available Models

**Groq:**
- `mixtral-8x7b-32768` (default, fast)
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`

**OpenAI:**
- `gpt-4o-mini` (default)
- `gpt-4o`

### RAG Parameters

You can modify these in `implementation/config.py`:
- `CHUNK_SIZE` - Text chunk size (default: 1000)
- `CHUNK_OVERLAP` - Chunk overlap (default: 200)
- `EMBEDDING_MODEL` - Sentence transformer model

## Troubleshooting

### "Aucune cle API trouvee" Error
- Ensure `.env` file exists in project root
- Verify API key is correct
- Check there are no extra spaces around the key

### Index Not Building
- Ensure PDFs are uploaded successfully
- Check the `docs/` folder exists
- Review console logs for errors

### Server Won't Start
- Verify port 8000 is available
- Check all dependencies are installed
- Ensure Python 3.10+ is being used

### Slow Responses
- Try Groq for faster responses
- Reduce document chunk size
- Use smaller embedding model

## Key Technologies

- **FastAPI** - Modern async web framework
- **LangChain** - RAG pipeline orchestration
- **FAISS** - Vector similarity search
- **Sentence Transformers** - Text embeddings
- **Groq/OpenAI** - Language models
- **Jinja2** - HTML templating

## Development

### Running in Development Mode

```
bash
cd implementation
python -m uvicorn main:app --reload
```

### Adding New Features

1. **New API Routes**: Add to `implementation/api/routes/`
2. **New Templates**: Add to `implementation/templates/`
3. **New Components**: Add to `implementation/static/`
4. **New Config**: Modify `implementation/config.py`

## License

MIT License

---

**Built with ❤️ using FastAPI and LangChain**
