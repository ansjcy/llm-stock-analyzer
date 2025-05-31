"""
Logging utilities for LLM Stock Analysis Tool
"""

import sys
from loguru import logger
from src.utils.config import config


def setup_logger():
    """Setup and configure the logger"""
    # Remove default logger
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Add file handler for persistent logging
    logger.add(
        "logs/stock_analysis.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    return logger


def get_logger(name: str = None):
    """Get a logger instance"""
    if name:
        return logger.bind(name=name)
    return logger


# Initialize logger
setup_logger()
stock_logger = get_logger("stock_analysis") 