"""
Abstract base class for LLM clients
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseLLMClient(ABC):
    """Abstract base class for LLM integrations"""
    
    def __init__(self, language: str = 'en'):
        self.language = language
    
    @abstractmethod
    def generate_technical_analysis(self, ticker: str, technical_data: Dict[str, Any], 
                                  stock_info: Dict[str, Any]) -> str:
        """Generate technical analysis report using LLM"""
        pass
    
    @abstractmethod
    def generate_fundamental_analysis(self, ticker: str, stock_info: Dict[str, Any], 
                                    financial_data: Dict[str, Any]) -> str:
        """Generate fundamental analysis report using LLM"""
        pass
    
    @abstractmethod
    def generate_news_analysis(self, ticker: str, news_articles: List[Dict[str, Any]], 
                             stock_info: Dict[str, Any]) -> str:
        """Generate news sentiment and impact analysis"""
        pass
    
    @abstractmethod
    def generate_investment_recommendation(self, ticker: str, stock_info: Dict[str, Any],
                                         technical_analysis: str, fundamental_analysis: str,
                                         news_analysis: str) -> str:
        """Generate comprehensive investment recommendation"""
        pass
    
    @abstractmethod
    def summarize_analysis(self, ticker: str, stock_info: Dict[str, Any],
                          technical_summary: str, fundamental_summary: str,
                          news_summary: str, recommendation: str) -> str:
        """Generate executive summary of all analysis"""
        pass 