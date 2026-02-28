"""Custom exceptions for UniHelp application."""


class IITBaseError(Exception):
    """Base exception for all IIT application errors."""
    pass


class ConfigurationError(IITBaseError):
    """Raised when configuration is invalid or missing."""
    pass


class IndexBuildError(IITBaseError):
    """Raised when index building fails."""
    pass


class IndexLoadError(IITBaseError):
    """Raised when index loading fails."""
    pass


class IndexNotReadyError(IITBaseError):
    """Raised when index is not ready for use."""
    pass


class NoDocumentsFoundError(IITBaseError):
    """Raised when no documents are found in the specified directory."""
    pass


class RAGPipelineError(IITBaseError):
    """Raised when RAG pipeline execution fails."""
    pass


class UnknownEmailTypeError(IITBaseError):
    """Raised when an unknown email type is requested."""
    pass


class EmailRenderError(IITBaseError):
    """Raised when email rendering fails."""
    pass
