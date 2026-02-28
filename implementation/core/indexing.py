
import logging
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
from core.interfaces import DocumentIndexer, EmbeddingProvider
from utils.exceptions import (
    IndexBuildError,
    IndexLoadError,
    IndexNotReadyError,
    NoDocumentsFoundError,
)

logger = logging.getLogger(__name__)


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = config.EMBEDDING_MODEL) -> None:
        self._model_name = model_name
        self._embeddings: Optional[HuggingFaceEmbeddings] = None

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        """Return embeddings (single load on first call)."""
        if self._embeddings is None:
            logger.info("Loading embeddings model: %s", self._model_name)
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self._model_name,
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings


class FAISSDocumentIndexer(DocumentIndexer):

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        index_dir: Path = None,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._index_dir = index_dir or Path(config.FAISS_INDEX_DIR)
        self._vectorstore = None
        self._documents = []

    @property
    def documents(self) -> list:
        return self._documents

    def _load_and_split(self, docs_dir: Path) -> list[Document]:
        if not docs_dir.exists():
            raise NoDocumentsFoundError(f"Directory not found: {docs_dir}")
        
        loader = PyPDFDirectoryLoader(str(docs_dir))
        documents = loader.load()
        
        if not documents:
            raise NoDocumentsFoundError(f"No PDF documents found in {docs_dir}")
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
        )
        
        chunks = splitter.split_documents(documents)
        logger.info("Loaded %d documents, created %d chunks", len(documents), len(chunks))
        
        return chunks

    def build_index(self, docs_dir: Path = None) -> None:
        docs_dir = docs_dir or Path(config.DOCS_DIR)
        
        try:
            chunks = self._load_and_split(docs_dir)
            embeddings = self._embedding_provider.get_embeddings()

            logger.info("Building FAISS index (%d chunks)...", len(chunks))
            self._vectorstore = FAISS.from_documents(chunks, embeddings)
            self._documents = chunks

            self._index_dir.mkdir(parents=True, exist_ok=True)
            self._vectorstore.save_local(str(self._index_dir))
            logger.info("Index saved: %s", self._index_dir)

        except NoDocumentsFoundError:
            raise
        except Exception as exc:
            logger.error("Index build failed: %s", exc)
            raise IndexBuildError(f"Unable to build index: {exc}") from exc

    def load_index(self) -> bool:
        if not self._index_dir.exists():
            logger.info("Index directory not found: %s", self._index_dir)
            return False
        try:
            embeddings = self._embedding_provider.get_embeddings()
            # allow_dangerous_deserialization: local trusted files only
            self._vectorstore = FAISS.load_local(
                str(self._index_dir),
                embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("Index loaded from: %s", self._index_dir)
            return True
        except Exception as exc:
            logger.error("Unable to load index: %s", exc)
            return False

    def is_index_ready(self) -> bool:
        """Return True if vectorstore is operational in memory."""
        return self._vectorstore is not None

    def as_retriever(self, k: int = 5):
        if not self.is_index_ready():
            raise IndexNotReadyError(
                "FAISS index not loaded. "
                "Call build_index() or load_index() first."
            )
        return self._vectorstore.as_retriever(search_kwargs={"k": k})


# Export classes
__all__ = ["FAISSDocumentIndexer", "HuggingFaceEmbeddingProvider"]
