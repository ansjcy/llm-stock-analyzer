"""
Factory for creating LLM clients based on configuration
"""

from typing import Optional
from src.utils.config import config
from src.utils.logger import stock_logger
from src.llm.base_client import BaseLLMClient
from src.llm.openai_client import OpenAIClient
from src.llm.gemini_client import GeminiClient


class LLMClientFactory:
    """Factory for creating LLM clients"""
    
    @staticmethod
    def create_client(provider: Optional[str] = None, language: str = 'en') -> BaseLLMClient:
        """
        Create an LLM client based on the specified provider or default configuration
        
        Args:
            provider: The LLM provider to use ('openai', 'gemini', etc.)
                     If None, uses DEFAULT_LLM_PROVIDER from config
            language: The language for generating insights ('en' or 'zh')
        
        Returns:
            BaseLLMClient: An instance of the appropriate LLM client
        
        Raises:
            ValueError: If the provider is unsupported or API key is missing
        """
        if provider is None:
            provider = config.DEFAULT_LLM_PROVIDER
        
        provider = provider.lower()
        
        try:
            if provider == "openai":
                if not config.OPENAI_API_KEY:
                    raise ValueError("OpenAI API key is required")
                stock_logger.info("Creating OpenAI client")
                return OpenAIClient(language=language)
            
            elif provider == "gemini":
                if not config.GEMINI_API_KEY:
                    raise ValueError("Gemini API key is required")
                stock_logger.info("Creating Gemini client")
                return GeminiClient(language=language)
            
            else:
                supported_providers = ["openai", "gemini"]
                raise ValueError(f"Unsupported LLM provider: {provider}. "
                               f"Supported providers: {', '.join(supported_providers)}")
        
        except Exception as e:
            stock_logger.error(f"Failed to create LLM client for provider '{provider}': {e}")
            raise
    
    @staticmethod
    def get_available_providers() -> list:
        """
        Get list of available LLM providers based on configured API keys
        
        Returns:
            list: List of available provider names
        """
        available = []
        
        if config.OPENAI_API_KEY:
            available.append("openai")
        
        if config.GEMINI_API_KEY:
            available.append("gemini")
        
        return available
    
    @staticmethod
    def validate_provider(provider: str) -> bool:
        """
        Validate if a provider is supported and has required API key
        
        Args:
            provider: The provider name to validate
        
        Returns:
            bool: True if provider is valid and configured
        """
        return provider.lower() in LLMClientFactory.get_available_providers()


# Convenience function for easy import
def create_llm_client(provider: Optional[str] = None, language: str = 'en') -> BaseLLMClient:
    """
    Convenience function to create an LLM client
    
    Args:
        provider: The LLM provider to use
        language: The language for generating insights ('en' or 'zh')
    
    Returns:
        BaseLLMClient: An instance of the appropriate LLM client
    """
    return LLMClientFactory.create_client(provider, language=language) 