"""
OpenAI LLM client for stock analysis and report generation
"""

import json
from typing import Dict, Any, List, Optional
from openai import OpenAI

from src.utils.config import config
from src.utils.logger import stock_logger
from src.llm.base_client import BaseLLMClient
from src.llm.analysis_prompts import AnalysisPrompts


class OpenAIClient(BaseLLMClient):
    """OpenAI API client for stock analysis"""
    
    def __init__(self, language: str = 'en'):
        super().__init__(language)
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4o"  # Use the latest model
        
    def generate_technical_analysis(self, ticker: str, technical_data: Dict[str, Any], 
                                  stock_info: Dict[str, Any]) -> str:
        """Generate technical analysis report using LLM"""
        try:
            prompts = AnalysisPrompts.get_technical_analysis_prompt(ticker, technical_data, stock_info, self.language)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts["system"]},
                    {"role": "user", "content": prompts["user"]}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            stock_logger.error(f"Error generating technical analysis: {e}")
            return f"Error generating technical analysis: {str(e)}"
    
    def generate_fundamental_analysis(self, ticker: str, stock_info: Dict[str, Any], 
                                    financial_data: Dict[str, Any]) -> str:
        """Generate fundamental analysis report using LLM"""
        try:
            prompts = AnalysisPrompts.get_fundamental_analysis_prompt(ticker, stock_info, financial_data, self.language)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts["system"]},
                    {"role": "user", "content": prompts["user"]}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            stock_logger.error(f"Error generating fundamental analysis: {e}")
            return f"Error generating fundamental analysis: {str(e)}"
    
    def generate_news_analysis(self, ticker: str, news_articles: List[Dict[str, Any]], 
                             stock_info: Dict[str, Any]) -> str:
        """Generate news sentiment and impact analysis"""
        try:
            prompts = AnalysisPrompts.get_news_analysis_prompt(ticker, news_articles, stock_info, self.language)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts["system"]},
                    {"role": "user", "content": prompts["user"]}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            stock_logger.error(f"Error generating news analysis: {e}")
            return f"Error generating news analysis: {str(e)}"
    
    def generate_investment_recommendation(self, ticker: str, stock_info: Dict[str, Any],
                                         technical_analysis: str, fundamental_analysis: str,
                                         news_analysis: str) -> str:
        """Generate comprehensive investment recommendation"""
        try:
            prompts = AnalysisPrompts.get_investment_recommendation_prompt(
                ticker, stock_info, technical_analysis, fundamental_analysis, news_analysis, self.language
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts["system"]},
                    {"role": "user", "content": prompts["user"]}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            stock_logger.error(f"Error generating investment recommendation: {e}")
            return f"Error generating investment recommendation: {str(e)}"
    
    def summarize_analysis(self, ticker: str, stock_info: Dict[str, Any],
                          technical_summary: str, fundamental_summary: str,
                          news_summary: str, recommendation: str) -> str:
        """Generate executive summary of all analysis"""
        try:
            prompts = AnalysisPrompts.get_summary_prompt(
                ticker, stock_info, technical_summary, fundamental_summary, 
                news_summary, recommendation, self.language
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts["system"]},
                    {"role": "user", "content": prompts["user"]}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            stock_logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"


def get_openai_client() -> OpenAIClient:
    """Get OpenAI client instance"""
    return OpenAIClient() 