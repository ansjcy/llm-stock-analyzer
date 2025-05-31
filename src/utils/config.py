"""
Configuration management for LLM Stock Analysis Tool
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the application"""
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # News API Keys
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY")
    FINNHUB_API_KEY: Optional[str] = os.getenv("FINNHUB_API_KEY")
    
    # Configuration
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CACHE_DURATION: int = int(os.getenv("CACHE_DURATION", "3600"))
    
    # Data Sources Configuration
    YAHOO_FINANCE_ENABLED: bool = os.getenv("YAHOO_FINANCE_ENABLED", "true").lower() == "true"
    SINA_FINANCE_ENABLED: bool = os.getenv("SINA_FINANCE_ENABLED", "true").lower() == "true"
    USE_CACHE: bool = os.getenv("USE_CACHE", "true").lower() == "true"
    
    # Analysis Configuration
    TECHNICAL_ANALYSIS_PERIOD: int = int(os.getenv("TECHNICAL_ANALYSIS_PERIOD", "252"))
    FUNDAMENTAL_ANALYSIS_ENABLED: bool = os.getenv("FUNDAMENTAL_ANALYSIS_ENABLED", "true").lower() == "true"
    NEWS_ANALYSIS_ENABLED: bool = os.getenv("NEWS_ANALYSIS_ENABLED", "true").lower() == "true"
    SENTIMENT_ANALYSIS_ENABLED: bool = os.getenv("SENTIMENT_ANALYSIS_ENABLED", "true").lower() == "true"
    
    # Report Configuration
    SAVE_REPORTS: bool = os.getenv("SAVE_REPORTS", "true").lower() == "true"
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "./stock-analysis-viewer/public/reports")
    REPORT_FORMAT: str = os.getenv("REPORT_FORMAT", "markdown")
    
    # API Rate Limiting
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "60"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        errors = []
        warnings = []
        
        # Check if any LLM provider is available
        available_llm_providers = []
        if cls.OPENAI_API_KEY:
            available_llm_providers.append("openai")
        if cls.CLAUDE_API_KEY:
            available_llm_providers.append("claude")
        if cls.GROQ_API_KEY:
            available_llm_providers.append("groq")
        if cls.GEMINI_API_KEY:
            available_llm_providers.append("gemini")
        
        # Only warn if no LLM providers are available, don't fail validation
        if not available_llm_providers:
            warnings.append("No LLM API keys configured. AI analysis will be disabled.")
        elif cls.DEFAULT_LLM_PROVIDER not in available_llm_providers:
            # Try to set a valid default provider if current one is not available
            cls.DEFAULT_LLM_PROVIDER = available_llm_providers[0]
            warnings.append(f"Default LLM provider changed to {cls.DEFAULT_LLM_PROVIDER}")
        
        # Print warnings
        for warning in warnings:
            print(f"Warning: {warning}")
        
        # Print errors (if any)
        for error in errors:
            print(f"Configuration Error: {error}")
        
        # Return True if no critical errors (warnings are acceptable)
        return len(errors) == 0
    
    @classmethod
    def get_llm_api_key(cls) -> Optional[str]:
        """Get the API key for the configured LLM provider"""
        if cls.DEFAULT_LLM_PROVIDER == "openai":
            return cls.OPENAI_API_KEY
        elif cls.DEFAULT_LLM_PROVIDER == "claude":
            return cls.CLAUDE_API_KEY
        elif cls.DEFAULT_LLM_PROVIDER == "groq":
            return cls.GROQ_API_KEY
        elif cls.DEFAULT_LLM_PROVIDER == "gemini":
            return cls.GEMINI_API_KEY
        return None


# Global config instance
config = Config() 