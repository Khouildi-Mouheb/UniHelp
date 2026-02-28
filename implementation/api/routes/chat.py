import logging
import uuid
from fastapi import APIRouter, HTTPException

from config import Settings
from core.indexing import FAISSDocumentIndexer, HuggingFaceEmbeddingProvider
from core.llm import get_llm_provider
from core.retrieval import RAGPipeline
from utils.exceptions import IITBaseError
from api.schemas import ChatRequest, ChatResponse, DocumentIndexStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Singleton instances
_indexer = None
_pipeline = None


def get_indexer() -> FAISSDocumentIndexer:
    global _indexer
    if _indexer is None:
        embedding_provider = HuggingFaceEmbeddingProvider()
        _indexer = FAISSDocumentIndexer(embedding_provider=embedding_provider)
    return _indexer


def get_pipeline() -> RAGPipeline | None:
    global _pipeline
    if _pipeline is None:
        indexer = get_indexer()
        
        if indexer.is_index_ready():
            try:
                settings = Settings.from_env()
                llm_provider = get_llm_provider(settings)
                
                _pipeline = RAGPipeline(indexer=indexer, llm_provider=llm_provider)
            except IITBaseError as exc:
                logger.warning("RAG pipeline not initialized: %s", exc)
        else:
            print("    Index not ready, pipeline not initialized")
    return _pipeline


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest) -> ChatResponse:

    
    pipeline = get_pipeline()
    if pipeline is None:
        print(" ERROR: RAG pipeline not initialized")
        raise HTTPException(
            status_code=503,
            detail="Pipeline RAG non initialise. Veuillez construire l'index d'abord."
        )
    
    try:
        session_id = request.session_id or str(uuid.uuid4())
        result = pipeline.retrieve_and_answer(request.question)
        
        response = ChatResponse(
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            session_id=session_id
        )
        
        
        return response
    except Exception as exc:
        logger.error("Error processing question: %s", exc)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(exc)}")


@router.get("/index-status", response_model=DocumentIndexStatus)
async def get_index_status() -> DocumentIndexStatus:
    try:
        indexer = get_indexer()
        doc_count = 0
        if indexer.is_index_ready():
            try:
                doc_count = indexer._vectorstore.index.ntotal
            except Exception:
                doc_count = 0
        return DocumentIndexStatus(is_ready=indexer.is_index_ready(), document_count=doc_count)
    except Exception as exc:
        logger.error("/index-status error: %s", exc)
        return DocumentIndexStatus(is_ready=False, document_count=0)