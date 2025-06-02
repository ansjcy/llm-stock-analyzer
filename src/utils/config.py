"""
Configuration management for LLM Stock Analysis Tool
"""

import os
from typing import Optional, List
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
    GEMINI_API_KEYS: Optional[str] = os.getenv("GEMINI_API_KEYS")  # Comma-separated multiple keys
    
    # News API Keys
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY")
    FINNHUB_API_KEY: Optional[str] = os.getenv("FINNHUB_API_KEY")
    
    # Configuration
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CACHE_DURATION: int = int(os.getenv("CACHE_DURATION", "3600"))

    # Rate Limiting Configuration
    GEMINI_MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("GEMINI_MAX_REQUESTS_PER_MINUTE", "10"))
    GEMINI_RETRY_MAX_ATTEMPTS: int = int(os.getenv("GEMINI_RETRY_MAX_ATTEMPTS", "3"))  # Simple retry count
    GEMINI_RETRY_BASE_DELAY: float = float(os.getenv("GEMINI_RETRY_BASE_DELAY", "1.0"))  # Simple 1 second delay
    GEMINI_RETRY_MAX_DELAY: float = float(os.getenv("GEMINI_RETRY_MAX_DELAY", "5.0"))  # Max 5 seconds
    GEMINI_KEY_WAIT_TIMEOUT: int = int(os.getenv("GEMINI_KEY_WAIT_TIMEOUT", "10"))  # Reduced to 10 seconds

    # LLM Analysis Timeout Configuration
    LLM_ANALYSIS_TIMEOUT: int = int(os.getenv("LLM_ANALYSIS_TIMEOUT", "60"))  # 1 minute per LLM analysis step
    LLM_TOTAL_TIMEOUT: int = int(os.getenv("LLM_TOTAL_TIMEOUT", "600"))  # 10 minutes total for all LLM analysis

    # Gemini Configuration
    GEMINI_PRIMARY_MODEL: str = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.5-flash-preview-05-20")
    GEMINI_FALLBACK_MODEL: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash")
    
    # Data Sources Configuration
    YAHOO_FINANCE_ENABLED: bool = os.getenv("YAHOO_FINANCE_ENABLED", "true").lower() == "true"
    SINA_FINANCE_ENABLED: bool = os.getenv("SINA_FINANCE_ENABLED", "true").lower() == "true"
    USE_CACHE: bool = os.getenv("USE_CACHE", "true").lower() == "true"
    
    # Analysis Configuration
    TECHNICAL_ANALYSIS_PERIOD: int = int(os.getenv("TECHNICAL_ANALYSIS_PERIOD", "252").split()[0])
    FUNDAMENTAL_ANALYSIS_ENABLED: bool = os.getenv("FUNDAMENTAL_ANALYSIS_ENABLED", "true").lower() == "true"
    NEWS_ANALYSIS_ENABLED: bool = os.getenv("NEWS_ANALYSIS_ENABLED", "true").lower() == "true"
    SENTIMENT_ANALYSIS_ENABLED: bool = os.getenv("SENTIMENT_ANALYSIS_ENABLED", "true").lower() == "true"
    
    # Report Configuration
    SAVE_REPORTS: bool = os.getenv("SAVE_REPORTS", "true").lower() == "true"
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "./stock-analysis-viewer/public/reports")
    REPORT_FORMAT: str = os.getenv("REPORT_FORMAT", "markdown")
    
    # API Rate Limiting
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "60").split()[0])
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30").split()[0])
    
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

    @classmethod
    def get_gemini_api_keys(cls) -> List[str]:
        """
        Get all available Gemini API keys

        Returns:
            List of Gemini API keys. Prioritizes GEMINI_API_KEYS (comma-separated)
            over single GEMINI_API_KEY
        """
        keys = []

        # First try to get multiple keys from GEMINI_API_KEYS
        if cls.GEMINI_API_KEYS:
            # Split by comma and clean up whitespace
            keys = [key.strip() for key in cls.GEMINI_API_KEYS.split(',') if key.strip()]

        # If no multiple keys, fall back to single key
        if not keys and cls.GEMINI_API_KEY:
            keys = [cls.GEMINI_API_KEY]

        # Filter out empty keys
        return [key for key in keys if key]


# Global config instance
config = Config() 