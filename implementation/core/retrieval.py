"""RAG pipeline for retrieval-augmented generation."""
import logging
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from core.indexing import FAISSDocumentIndexer
from core.interfaces import LLMProvider, QuestionAnswerer
from core.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT
from utils.exceptions import RAGPipelineError

logger = logging.getLogger(__name__)


class RAGPipeline(QuestionAnswerer):
    """Complete RAG pipeline: FAISS retrieval + LLM generation via LCEL.
    
    Depends on abstractions (LLMProvider, FAISSDocumentIndexer) and not
    on concrete implementations → facilitates testing and provider switching.
    
    Args:
        indexer: FAISS indexer already loaded.
        llm_provider: LLM provider (OpenAI, Anthropic, etc.).
    """

    def __init__(
        self,
        indexer: FAISSDocumentIndexer,
        llm_provider: LLMProvider,
    ) -> None:
        self._indexer = indexer
        self._llm_provider = llm_provider
        self._chain = self._build_chain()

    # ------------------------------------------------------------------
    # LCEL Chain Construction
    # ------------------------------------------------------------------

    @staticmethod
    def _format_docs(docs: list[Document]) -> str:
        """Format retrieved documents into structured context block.
        
        The [Source | Page] format allows the LLM to cite its sources.
        """
        return "\n\n---\n\n".join(
            f"[Source : {doc.metadata.get('source', 'Unknown')} "
            f"| Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
            for doc in docs
        )

    def _build_chain(self):
        """Build LCEL chain with parallel retrieval.
        
        Architecture:
            retriever ──> format_docs ──> context ──┐
                                                      ├───> prompt -> LLM -> parser
            passthrough ──────────────> question ──┘
            retriever ──────────────────────────────> source_docs (for UI)
        """
        retriever = self._indexer.as_retriever()
        llm = self._llm_provider.get_llm()

        prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_SYSTEM_PROMPT),
            ("human", RAG_USER_PROMPT),
        ])

        # Parallel execution: formatted context + raw question + raw docs
        return (
            RunnableParallel(
                context=retriever | self._format_docs,
                question=RunnablePassthrough(),
                source_docs=retriever,
            )
            | {
                "answer": (
                    (lambda x: {"context": x["context"], "question": x["question"]})
                    | prompt
                    | llm
                    | StrOutputParser()
                ),
                "source_docs": lambda x: x["source_docs"],
            }
        )

    # ------------------------------------------------------------------
    # QuestionAnswerer Interface
    # ------------------------------------------------------------------

    def answer(self, question: str) -> dict[str, Any]:
        """Generate RAG answer with sources used.
        
        Args:
            question: Question posed by the student.
            
        Returns:
            Dict with 'answer' (str) and 'source_docs' (list[Document]).
            
        Raises:
            RAGPipelineError: If retrieval or generation fails.
        """
        try:
            result = self._chain.invoke(question)
            return {
                "answer": result["answer"],
                "source_docs": result.get("source_docs", []),
            }
        except Exception as exc:
            logger.error("RAG pipeline error: %s", exc)
            raise RAGPipelineError(f"Generation failed: {exc}") from exc

    def retrieve_and_answer(self, question: str) -> dict[str, Any]:
        """Alias for answer method for backward compatibility."""
        return self.answer(question)


# Export
__all__ = ["RAGPipeline"]
