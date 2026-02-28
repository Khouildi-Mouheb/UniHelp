"""Logging setup for UniHelp application."""
import logging
import sys


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Setup logging configuration for the application.
    
    Args:
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("unihelp")
    logger.setLevel(level)
    
    return logger


# Export a default logger
logger = setup_logging()
