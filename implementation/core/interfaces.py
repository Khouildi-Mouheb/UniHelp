
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DocumentIndexer(ABC):
    """Interface for any document indexing system."""

    @abstractmethod
    def build_index(self, docs_dir: Path = None) -> None:
        """Build and persist the vector index.
        
        Args:
            docs_dir: Directory containing source documents.
            
        Raises:
            NoDocumentsFoundError: No document found.
            IndexBuildError: Build failed.
        """
        ...

    @abstractmethod
    def load_index(self) -> bool:
        """Load a persisted index from disk.
        
        Returns:
            True if loaded successfully, False otherwise.
        """
        ...

    @abstractmethod
    def is_index_ready(self) -> bool:
        """Return True if the index is operational in memory."""
        ...


class EmbeddingProvider(ABC):

    @abstractmethod
    def get_embeddings(self):
        pass


class LLMProvider(ABC):

    @abstractmethod
    def get_llm(self):
        pass

class QuestionAnswerer(ABC):

    @abstractmethod
    def answer(self, question: str) -> dict[str, Any]:
        pass