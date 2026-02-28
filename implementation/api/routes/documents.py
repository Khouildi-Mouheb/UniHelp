
import logging
from fastapi import APIRouter, HTTPException

from core.indexing import FAISSDocumentIndexer, HuggingFaceEmbeddingProvider

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["Documents"])

# Singleton indexer instance
_indexer = None


def get_indexer() -> FAISSDocumentIndexer:
    global _indexer
    if _indexer is None:
        embedding_provider = HuggingFaceEmbeddingProvider()
        _indexer = FAISSDocumentIndexer(embedding_provider=embedding_provider)
    return _indexer


@router.post("/build-index")
async def build_index():
    try:
        indexer = get_indexer()
        indexer.build_index()
        return {
            "status": "success",
            "message": "Index built successfully",
            "document_count": len(indexer.documents)
        }
    except Exception as exc:
        logger.error("Error building index: %s", exc)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(exc)}")


@router.post("/load-index")
async def load_index():
    try:
        indexer = get_indexer()
        success = indexer.load_index()
        if success:
            return {
                "status": "success",
                "message": "Index loaded successfully",
                "document_count": len(indexer.documents)
            }
        else:
            return {
                "status": "warning",
                "message": "No existing index found"
            }
    except Exception as exc:
        logger.error("Error loading index: %s", exc)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(exc)}")


@router.get("/status")
async def get_status():
    try:
        indexer = get_indexer()
        return {
            "is_ready": indexer.is_index_ready(),
            "document_count": len(indexer.documents) if indexer.is_index_ready() else 0
        }
    except Exception as exc:
        logger.error("Error getting status: %s", exc)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(exc)}")