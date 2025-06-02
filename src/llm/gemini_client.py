"""
Google Gemini LLM client for stock analysis and report generation
"""

import time
import signal
from typing import Dict, Any, List
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from src.utils.config import config
from src.utils.logger import stock_logger
from src.llm.base_client import BaseLLMClient
from src.llm.analysis_prompts import AnalysisPrompts
from src.llm.simple_key_manager import GeminiKeyManager, RetryConfig


class APITimeoutError(Exception):
    """Exception raised when API call times out"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for API timeouts"""
    raise APITimeoutError("API call timed out")


class GeminiClient(BaseLLMClient):
    """Google Gemini API client for stock analysis"""

    def __init__(self, language: str = 'en'):
        super().__init__(language)

        # Get all available Gemini API keys
        api_keys = config.get_gemini_api_keys()
        if not api_keys:
            raise ValueError("At least one Gemini API key is required. Set GEMINI_API_KEY or GEMINI_API_KEYS environment variable.")

        # Initialize key manager with rate limiting
        self.key_manager = GeminiKeyManager(
            api_keys=api_keys,
            max_requests_per_minute=config.GEMINI_MAX_REQUESTS_PER_MINUTE
        )

        # Initialize retry configuration
        self.retry_config = RetryConfig(
            max_retries=config.GEMINI_RETRY_MAX_ATTEMPTS,
            base_delay=config.GEMINI_RETRY_BASE_DELAY,
            max_delay=config.GEMINI_RETRY_MAX_DELAY
        )

        # Configure generation parameters for consistent responses
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=1.0,
            top_k=32,
            candidate_count=1,
            max_output_tokens=2000,
        )

        # Model configuration with fallback
        self.primary_model = config.GEMINI_PRIMARY_MODEL
        self.fallback_model = config.GEMINI_FALLBACK_MODEL

        stock_logger.info(f"Initialized Gemini client with {len(api_keys)} API keys, primary model: {self.primary_model}, fallback: {self.fallback_model}")
        
    def _generate_response(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """
        Helper method to generate response from Gemini with rate limiting and retry logic
        """
        # Combine system and user prompts for Gemini
        combined_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"

        # Update generation config with specific max tokens
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=1.0,
            top_k=32,
            candidate_count=1,
            max_output_tokens=max_tokens,
        )

        # Configure safety settings to be maximally permissive for financial analysis
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]

        # Try primary model first, then fallback model
        models_to_try = [self.primary_model, self.fallback_model]

        for i, model_name in enumerate(models_to_try):
            result = self._try_model(model_name, combined_prompt, generation_config, safety_settings)

            # Check if we got a successful response
            if result and not result.startswith("Error:") and "content filtering" not in result.lower():
                return result

            # Handle specific error types
            elif "content filtering" in result.lower() or "safety filters" in result.lower():
                stock_logger.warning(f"Model {model_name} blocked by content filtering, trying next model...")
                continue
            elif "timeouts" in result.lower() or "having issues" in result.lower():
                stock_logger.warning(f"Model {model_name} appears to be having issues (timeouts), trying next model...")
                continue
            elif "not available" in result.lower():
                stock_logger.warning(f"Model {model_name} not available, trying next model...")
                continue
            else:
                stock_logger.warning(f"Model {model_name} failed with error: {result}")
                # If this is the last model, return the error
                if i == len(models_to_try) - 1:
                    return result
                continue

        return "Error: All models failed due to content filtering or other issues. Please try rephrasing your request."

    def _try_model(self, model_name: str, combined_prompt: str, generation_config, safety_settings) -> str:
        """
        Try to generate response with a specific model using simple retry logic
        """
        stock_logger.info(f"Attempting to use model: {model_name}")

        # Limit attempts to avoid infinite loops - try each key once, max 4 attempts
        max_attempts = min(len(self.key_manager.api_keys), 4)
        timeout_count = 0

        for attempt in range(max_attempts):
            try:
                # Get next available key
                api_key = self.key_manager.get_available_key()

                if not api_key:
                    key_summary = self.key_manager.get_key_summary()
                    stock_logger.warning(f"No available keys found on attempt {attempt + 1}. Status: {key_summary}")
                    return "Error: All API keys are rate limited. Please try again later."

                # Configure the API with the selected key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)

                # Make the API request with timeout for fast rate limit detection
                stock_logger.info(f"Making API request to {model_name} with key ...{api_key[-8:]} (attempt {attempt + 1}/{max_attempts})")

                # Set up timeout (10 seconds for quick detection of hanging calls)
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(60)

                try:
                    response = model.generate_content(
                        combined_prompt,
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )
                    stock_logger.info(f"API request to {model_name} completed successfully")
                finally:
                    signal.alarm(0)  # Cancel timeout

                # Record successful request
                self.key_manager.record_request(api_key)

                # Process response
                return self._process_response(response, combined_prompt, model_name)

            except google_exceptions.ResourceExhausted as e:
                # Rate limit error (429) - should be detected quickly
                stock_logger.warning(f"Rate limit hit for key ending in ...{api_key[-8:] if api_key else 'unknown'}: {e}")

                if api_key:
                    # Extract retry-after from error if available
                    retry_after = None
                    if hasattr(e, 'details') and 'Retry after' in str(e.details):
                        try:
                            import re
                            match = re.search(r'Retry after (\d+)', str(e.details))
                            if match:
                                retry_after = int(match.group(1))
                        except:
                            pass

                    self.key_manager.record_rate_limit(api_key, retry_after)

                # Immediately try next key - no waiting
                stock_logger.info(f"Rate limit hit, immediately trying next key (attempt {attempt + 1}/{max_attempts})")
                continue

            except APITimeoutError as e:
                # API call timed out - this key is hanging, try next key immediately
                timeout_count += 1
                stock_logger.warning(f"API call timed out for key ending in ...{api_key[-8:] if api_key else 'unknown'}: {e}")
                stock_logger.info(f"Timeout occurred, immediately trying next key (attempt {attempt + 1}/{max_attempts})")

                # If we've had multiple timeouts, the model itself might be having issues
                if timeout_count >= 2:
                    stock_logger.error(f"Multiple timeouts ({timeout_count}) for model {model_name}, model may be having issues")
                    return f"Error: Model {model_name} appears to be having issues (multiple timeouts)"

                continue

            except Exception as e:
                stock_logger.error(f"Error generating Gemini response with {model_name} on attempt {attempt + 1}: {e}")

                # Check if it's a model not found error
                if "not found" in str(e).lower() or "does not exist" in str(e).lower() or "invalid model" in str(e).lower():
                    stock_logger.warning(f"Model {model_name} not available, skipping to next model")
                    return f"Error: Model {model_name} not available"

                # For other errors, immediately try next key
                stock_logger.info(f"Error occurred, immediately trying next key (attempt {attempt + 1}/{max_attempts})")
                continue

        # If we get here, all attempts failed
        if timeout_count > 0:
            stock_logger.error(f"Model {model_name} failed with {timeout_count} timeouts out of {max_attempts} attempts")
            return f"Error: Model {model_name} appears to be having issues (timeouts)"
        else:
            return "Error: All retry attempts failed."

    def _process_response(self, response, combined_prompt: str, model_name: str = "unknown") -> str:
        """Process the Gemini API response and extract text"""
        try:
            # Check if response was blocked
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    if candidate.finish_reason == 2:  # SAFETY
                        stock_logger.warning(f"Model {model_name} response blocked by safety filters for prompt: {combined_prompt[:100]}...")
                        return "Analysis temporarily unavailable due to content filtering. Please try again or use a different LLM provider."
                    elif candidate.finish_reason == 3:  # RECITATION
                        stock_logger.warning(f"Model {model_name} response blocked due to recitation for prompt: {combined_prompt[:100]}...")
                        return "Analysis temporarily unavailable due to content recitation detection. Please try again or use a different LLM provider."

                # Check if response has text
                if hasattr(response, 'text') and response.text:
                    stock_logger.info(f"Model {model_name} successfully generated response")
                    return response.text
                elif candidate.content and candidate.content.parts:
                    # Try to extract text from parts
                    text_parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    if text_parts:
                        stock_logger.info(f"Model {model_name} successfully generated response from parts")
                        return ''.join(text_parts)

            # If we get here, something went wrong
            finish_reason = response.candidates[0].finish_reason if response.candidates else 'No candidates'
            stock_logger.warning(f"Model {model_name} response has no valid content. Finish reason: {finish_reason}")
            return "Analysis temporarily unavailable. Please try again or use a different LLM provider."

        except Exception as e:
            stock_logger.error(f"Error processing {model_name} response: {e}")
            return f"Error processing response: {str(e)}"

    def get_usage_stats(self) -> Dict[str, Dict]:
        """Get usage statistics for all API keys"""
        stats = {}
        for i, key in enumerate(self.key_manager.api_keys):
            current_requests = len(self.key_manager.request_counts[key])
            is_rate_limited = key in self.key_manager.rate_limited_keys
            stats[f"key_{i+1}"] = {
                "current_requests": current_requests,
                "max_requests": self.key_manager.max_requests_per_minute,
                "is_rate_limited": is_rate_limited
            }
        return stats



    def generate_technical_analysis(self, ticker: str, technical_data: Dict[str, Any],
                                  stock_info: Dict[str, Any]) -> str:
        """Generate technical analysis report using Gemini LLM"""
        return self._generate_technical_analysis_internal(ticker, technical_data, stock_info)

    def _generate_technical_analysis_internal(self, ticker: str, technical_data: Dict[str, Any],
                                            stock_info: Dict[str, Any]) -> str:
        """Internal method for technical analysis generation"""
        try:
            prompts = AnalysisPrompts.get_technical_analysis_prompt(ticker, technical_data, stock_info, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 2000)

        except Exception as e:
            stock_logger.error(f"Error generating technical analysis: {e}")
            return f"Error generating technical analysis: {str(e)}"
    
    def generate_fundamental_analysis(self, ticker: str, stock_info: Dict[str, Any],
                                    financial_data: Dict[str, Any]) -> str:
        """Generate fundamental analysis report using Gemini LLM"""
        return self._generate_fundamental_analysis_internal(ticker, stock_info, financial_data)

    def _generate_fundamental_analysis_internal(self, ticker: str, stock_info: Dict[str, Any],
                                              financial_data: Dict[str, Any]) -> str:
        """Internal method for fundamental analysis generation"""
        try:
            prompts = AnalysisPrompts.get_fundamental_analysis_prompt(ticker, stock_info, financial_data, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 2000)

        except Exception as e:
            stock_logger.error(f"Error generating fundamental analysis: {e}")
            return f"Error generating fundamental analysis: {str(e)}"

    def generate_news_analysis(self, ticker: str, news_articles: List[Dict[str, Any]],
                             stock_info: Dict[str, Any]) -> str:
        """Generate news sentiment and impact analysis using Gemini LLM"""
        return self._generate_news_analysis_internal(ticker, news_articles, stock_info)

    def _generate_news_analysis_internal(self, ticker: str, news_articles: List[Dict[str, Any]],
                                       stock_info: Dict[str, Any]) -> str:
        """Internal method for news analysis generation"""
        try:
            prompts = AnalysisPrompts.get_news_analysis_prompt(ticker, news_articles, stock_info, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 1500)

        except Exception as e:
            stock_logger.error(f"Error generating news analysis: {e}")
            return f"Error generating news analysis: {str(e)}"

    def generate_warren_buffett_analysis(self, ticker: str, warren_buffett_data: Dict[str, Any],
                                       stock_info: Dict[str, Any]) -> str:
        """Generate Warren Buffett style investment analysis using Gemini LLM"""
        return self._generate_warren_buffett_analysis_internal(ticker, warren_buffett_data, stock_info)

    def _generate_warren_buffett_analysis_internal(self, ticker: str, warren_buffett_data: Dict[str, Any],
                                                 stock_info: Dict[str, Any]) -> str:
        """Internal method for Warren Buffett analysis generation"""
        try:
            prompts = AnalysisPrompts.get_warren_buffett_analysis_prompt(ticker, warren_buffett_data, stock_info, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 2500)

        except Exception as e:
            stock_logger.error(f"Error generating Warren Buffett analysis: {e}")
            return f"Error generating Warren Buffett analysis: {str(e)}"

    def generate_peter_lynch_analysis(self, ticker: str, peter_lynch_data: Dict[str, Any],
                                    stock_info: Dict[str, Any]) -> str:
        """Generate Peter Lynch style investment analysis using Gemini LLM"""
        return self._generate_peter_lynch_analysis_internal(ticker, peter_lynch_data, stock_info)

    def _generate_peter_lynch_analysis_internal(self, ticker: str, peter_lynch_data: Dict[str, Any],
                                              stock_info: Dict[str, Any]) -> str:
        """Internal method for Peter Lynch analysis generation"""
        try:
            prompts = AnalysisPrompts.get_peter_lynch_analysis_prompt(ticker, peter_lynch_data, stock_info, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 2500)

        except Exception as e:
            stock_logger.error(f"Error generating Peter Lynch analysis: {e}")
            return f"Error generating Peter Lynch analysis: {str(e)}"

    def generate_investment_recommendation(self, ticker: str, stock_info: Dict[str, Any],
                                         technical_analysis: str, fundamental_analysis: str,
                                         news_analysis: str) -> str:
        """Generate comprehensive investment recommendation using Gemini LLM"""
        return self._generate_investment_recommendation_internal(ticker, stock_info, technical_analysis, fundamental_analysis, news_analysis)

    def _generate_investment_recommendation_internal(self, ticker: str, stock_info: Dict[str, Any],
                                                   technical_analysis: str, fundamental_analysis: str,
                                                   news_analysis: str) -> str:
        """Internal method for investment recommendation generation"""
        try:
            prompts = AnalysisPrompts.get_investment_recommendation_prompt(
                ticker, stock_info, technical_analysis, fundamental_analysis, news_analysis, self.language
            )
            return self._generate_response(prompts["system"], prompts["user"], 2000)

        except Exception as e:
            stock_logger.error(f"Error generating investment recommendation: {e}")
            return f"Error generating investment recommendation: {str(e)}"

    def summarize_analysis(self, ticker: str, stock_info: Dict[str, Any],
                          technical_summary: str, fundamental_summary: str,
                          news_summary: str, recommendation: str) -> str:
        """Generate executive summary of all analysis using Gemini LLM"""
        return self._summarize_analysis_internal(ticker, stock_info, technical_summary, fundamental_summary, news_summary, recommendation)

    def _summarize_analysis_internal(self, ticker: str, stock_info: Dict[str, Any],
                                   technical_summary: str, fundamental_summary: str,
                                   news_summary: str, recommendation: str) -> str:
        """Internal method for executive summary generation"""
        try:
            prompts = AnalysisPrompts.get_summary_prompt(
                ticker, stock_info, technical_summary, fundamental_summary,
                news_summary, recommendation, self.language
            )
            return self._generate_response(prompts["system"], prompts["user"], 1000)

        except Exception as e:
            stock_logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"

