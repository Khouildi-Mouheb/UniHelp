
import os
from dataclasses import dataclass

from dotenv import load_dotenv

from utils.exceptions import ConfigurationError

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application environment settings.
    
    Frozen dataclass: immutable after instantiation, thread-safe.
    All sensitive configuration (API keys) is encapsulated here.
    
    Attributes:
        llm_provider: Type of LLM provider ('openai' or 'groq', default: 'openai').
        api_key: API key for the LLM provider (required).
        llm_model: LLM model identifier.
    """

    llm_provider: str
    api_key: str
    llm_model: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Build Settings from environment variables.
        
        Raises:
            ConfigurationError: If neither OPENAI_API_KEY nor GROQ_API_KEY are present.
        """
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        
        if groq_key:
            provider = "groq"
            api_key = groq_key
            default_model = "mixtral-8x7b-32768"
        elif openai_key:
            provider = "openai"
            api_key = openai_key
            default_model = "gpt-4o-mini"
        else:
            raise ConfigurationError(
                "Aucune cle API trouvee. "
                "Creez un fichier .env avec OPENAI_API_KEY=sk-... ou GROQ_API_KEY=gsk-..."
            )
        
        return cls(
            llm_provider=provider,
            api_key=api_key,
            llm_model=os.getenv("LLM_MODEL", default_model).strip(),
        )


# RAG Parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
FAISS_INDEX_DIR = os.path.join(BASE_DIR, "faiss_index")
