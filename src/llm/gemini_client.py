"""
Google Gemini LLM client for stock analysis and report generation
"""

import time
import signal
import threading
import concurrent.futures
from typing import Dict, Any, List, Optional, Tuple
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from src.utils.config import config
from src.utils.logger import stock_logger
from src.llm.base_client import BaseLLMClient
from src.llm.analysis_prompts import AnalysisPrompts
from src.llm.key_manager import GeminiKeyManager, RetryConfig


class APITimeoutError(Exception):
    """Exception raised when API call times out"""
    pass


def timeout_api_call(func, timeout_seconds=120):
    """
    Execute a function with a timeout using threading

    Args:
        func: Function to execute
        timeout_seconds: Timeout in seconds

    Returns:
        Function result or raises APITimeoutError
    """
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)

    if thread.is_alive():
        # Thread is still running, which means timeout occurred
        stock_logger.error(f"API call timed out after {timeout_seconds} seconds")
        raise APITimeoutError(f"API call timed out after {timeout_seconds} seconds")

    if exception[0]:
        raise exception[0]

    return result[0]


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

        for model_name in models_to_try:
            result = self._try_model(model_name, combined_prompt, generation_config, safety_settings)
            if result and not result.startswith("Error:") and "content filtering" not in result.lower():
                return result
            elif "content filtering" in result.lower() or "safety filters" in result.lower():
                stock_logger.warning(f"Model {model_name} blocked by content filtering, trying next model...")
                continue
            else:
                stock_logger.warning(f"Model {model_name} failed with error: {result}")
                continue

        return "Error: All models failed due to content filtering or other issues. Please try rephrasing your request."

    def _try_model(self, model_name: str, combined_prompt: str, generation_config, safety_settings) -> str:
        """
        Try to generate response with a specific model
        """
        stock_logger.info(f"Attempting to use model: {model_name}")

        # Retry logic with exponential backoff
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Get an available API key (this now uses intelligent load balancing)
                api_key = self.key_manager.get_available_key()

                if not api_key:
                    # Log current key status
                    key_summary = self.key_manager.get_key_summary()
                    stock_logger.warning(f"No available keys found. Status: {key_summary}")

                    # Check if we should abort immediately due to long-term rate limits
                    if self.key_manager.should_abort_waiting():
                        stock_logger.error("All API keys are rate limited for extended periods. Aborting immediately.")
                        return "Error: All API keys are rate limited for extended periods. Please try again later."

                    # All keys are rate limited, but only wait briefly since we have multiple keys
                    stock_logger.warning("All API keys are currently rate limited. Waiting briefly for one to become available...")
                    # Use a much shorter timeout since we have multiple keys
                    max_wait_time = min(config.GEMINI_KEY_WAIT_TIMEOUT if hasattr(config, 'GEMINI_KEY_WAIT_TIMEOUT') else 90, 30)
                    api_key = self.key_manager.wait_for_available_key(max_wait_time=max_wait_time)

                    if not api_key:
                        final_summary = self.key_manager.get_key_summary()
                        stock_logger.error(f"All API keys still rate limited after waiting {max_wait_time}s. Final status: {final_summary}")
                        return f"Error: All API keys are rate limited and timeout reached after {max_wait_time}s. Please try again later."

                # Configure the API with the selected key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)

                # Make the API request with timeout
                stock_logger.info(f"Making API request to {model_name} with key ...{api_key[-8:]}")

                def make_api_call():
                    return model.generate_content(
                        combined_prompt,
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )

                # Use configurable timeout for API calls
                api_timeout = config.LLM_ANALYSIS_TIMEOUT if hasattr(config, 'LLM_ANALYSIS_TIMEOUT') else 120
                response = timeout_api_call(make_api_call, timeout_seconds=api_timeout)

                stock_logger.info(f"API request to {model_name} completed successfully")

                # Record successful request
                self.key_manager.record_request(api_key)

                # Process response
                return self._process_response(response, combined_prompt, model_name)

            except google_exceptions.ResourceExhausted as e:
                # Rate limit error (429)
                stock_logger.warning(f"Rate limit hit for key ending in ...{api_key[-8:] if api_key else 'unknown'}: {e}")

                if api_key:
                    # Extract retry-after from error if available
                    retry_after = None
                    if hasattr(e, 'details') and 'Retry after' in str(e.details):
                        try:
                            # Try to extract retry-after seconds from error message
                            import re
                            match = re.search(r'Retry after (\d+)', str(e.details))
                            if match:
                                retry_after = int(match.group(1))
                        except:
                            pass

                    self.key_manager.record_rate_limit(api_key, retry_after)

                # Check if we have other available keys before waiting
                key_summary = self.key_manager.get_key_summary()
                stock_logger.info(f"After rate limit, key status: {key_summary}")

                # Try to get another key immediately
                another_key = self.key_manager.get_available_key()
                if another_key:
                    stock_logger.info(f"Found alternative key ...{another_key[-8:]}, retrying immediately")
                    # Don't sleep, just continue to next iteration with new key
                    continue

                # If this is the last attempt, return error
                if attempt == self.retry_config.max_retries:
                    stock_logger.error(f"Rate limit exceeded for all {self.retry_config.max_retries + 1} attempts")
                    return f"Error: Rate limit exceeded for all attempts. Please try again later."

                # Only wait if no other keys are available
                delay = self.retry_config.get_delay(attempt)
                stock_logger.info(f"No alternative keys available. Retrying in {delay:.1f} seconds (attempt {attempt + 1}/{self.retry_config.max_retries + 1})")
                time.sleep(delay)

            except APITimeoutError as e:
                # API call timed out
                stock_logger.error(f"API call timed out for {model_name} with key ...{api_key[-8:] if api_key else 'unknown'}: {e}")

                # If this is the last attempt, return error
                if attempt == self.retry_config.max_retries:
                    return f"Error: API call timed out after {config.LLM_ANALYSIS_TIMEOUT if hasattr(config, 'LLM_ANALYSIS_TIMEOUT') else 120} seconds. Please try again later."

                # Wait before retrying for timeout errors (shorter delay)
                delay = min(self.retry_config.get_delay(attempt), 10)  # Cap at 10 seconds for timeouts
                stock_logger.info(f"Retrying in {delay:.1f} seconds due to timeout (attempt {attempt + 1}/{self.retry_config.max_retries + 1})")
                time.sleep(delay)

            except Exception as e:
                stock_logger.error(f"Error generating Gemini response with {model_name} (attempt {attempt + 1}): {e}")

                # Check if it's a model not found error
                if "not found" in str(e).lower() or "does not exist" in str(e).lower() or "invalid model" in str(e).lower():
                    stock_logger.warning(f"Model {model_name} not available, skipping to next model")
                    return f"Error: Model {model_name} not available"

                # If this is the last attempt, return error
                if attempt == self.retry_config.max_retries:
                    return f"Error generating response: {str(e)}"

                # Wait before retrying for non-rate-limit errors
                delay = self.retry_config.get_delay(attempt)
                stock_logger.info(f"Retrying in {delay:.1f} seconds due to error (attempt {attempt + 1}/{self.retry_config.max_retries + 1})")
                time.sleep(delay)

        return "Error: Maximum retry attempts exceeded."

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
        return self.key_manager.get_usage_stats()

    def generate_technical_analysis(self, ticker: str, technical_data: Dict[str, Any],
                                  stock_info: Dict[str, Any]) -> str:
        """Generate technical analysis report using Gemini LLM"""
        try:
            prompts = AnalysisPrompts.get_technical_analysis_prompt(ticker, technical_data, stock_info, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 2000)
            
        except Exception as e:
            stock_logger.error(f"Error generating technical analysis: {e}")
            return f"Error generating technical analysis: {str(e)}"
    
    def generate_fundamental_analysis(self, ticker: str, stock_info: Dict[str, Any], 
                                    financial_data: Dict[str, Any]) -> str:
        """Generate fundamental analysis report using Gemini LLM"""
        try:
            prompts = AnalysisPrompts.get_fundamental_analysis_prompt(ticker, stock_info, financial_data, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 2000)
            
        except Exception as e:
            stock_logger.error(f"Error generating fundamental analysis: {e}")
            return f"Error generating fundamental analysis: {str(e)}"
    
    def generate_news_analysis(self, ticker: str, news_articles: List[Dict[str, Any]], 
                             stock_info: Dict[str, Any]) -> str:
        """Generate news sentiment and impact analysis using Gemini LLM"""
        try:
            prompts = AnalysisPrompts.get_news_analysis_prompt(ticker, news_articles, stock_info, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 1500)
            
        except Exception as e:
            stock_logger.error(f"Error generating news analysis: {e}")
            return f"Error generating news analysis: {str(e)}"
    
    def generate_warren_buffett_analysis(self, ticker: str, warren_buffett_data: Dict[str, Any], 
                                       stock_info: Dict[str, Any]) -> str:
        """Generate Warren Buffett style investment analysis using Gemini LLM"""
        try:
            prompts = AnalysisPrompts.get_warren_buffett_analysis_prompt(ticker, warren_buffett_data, stock_info, self.language)
            return self._generate_response(prompts["system"], prompts["user"], 2500)
            
        except Exception as e:
            stock_logger.error(f"Error generating Warren Buffett analysis: {e}")
            return f"Error generating Warren Buffett analysis: {str(e)}"
    
    def generate_peter_lynch_analysis(self, ticker: str, peter_lynch_data: Dict[str, Any], 
                                    stock_info: Dict[str, Any]) -> str:
        """Generate Peter Lynch style investment analysis using Gemini LLM"""
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
        try:
            prompts = AnalysisPrompts.get_summary_prompt(
                ticker, stock_info, technical_summary, fundamental_summary, 
                news_summary, recommendation, self.language
            )
            return self._generate_response(prompts["system"], prompts["user"], 1000)
            
        except Exception as e:
            stock_logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"

    def generate_parallel_analysis(self, analysis_requests: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate multiple LLM analyses in parallel using different API keys

        Args:
            analysis_requests: List of analysis request dictionaries, each containing:
                - 'type': Analysis type (e.g., 'technical', 'fundamental', 'news')
                - 'method': Method name to call (e.g., 'generate_technical_analysis')
                - 'args': Arguments to pass to the method

        Returns:
            Dictionary mapping analysis type to result
        """
        if not analysis_requests:
            return {}

        # Get available keys for parallel processing
        available_keys = self.key_manager.get_multiple_available_keys(count=len(analysis_requests))

        if not available_keys:
            stock_logger.warning("No keys available for parallel processing, falling back to sequential")
            return self._generate_sequential_analysis(analysis_requests)

        stock_logger.info(f"Starting parallel analysis with {len(available_keys)} keys for {len(analysis_requests)} requests")

        results = {}

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(available_keys)) as executor:
            # Submit all tasks
            future_to_analysis = {}

            for i, request in enumerate(analysis_requests):
                # Assign key in round-robin fashion
                assigned_key = available_keys[i % len(available_keys)]

                future = executor.submit(
                    self._execute_single_analysis_with_key,
                    request,
                    assigned_key
                )
                future_to_analysis[future] = request['type']

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_analysis, timeout=600):  # 10 minute timeout
                analysis_type = future_to_analysis[future]
                try:
                    result = future.result()
                    results[analysis_type] = result
                    stock_logger.info(f"Completed parallel analysis: {analysis_type}")
                except Exception as e:
                    stock_logger.error(f"Parallel analysis failed for {analysis_type}: {e}")
                    results[analysis_type] = f"Error in parallel processing: {str(e)}"

        stock_logger.info(f"Parallel analysis completed. Results: {list(results.keys())}")
        return results

    def _execute_single_analysis_with_key(self, request: Dict[str, Any], api_key: str) -> str:
        """
        Execute a single analysis request with a specific API key

        Args:
            request: Analysis request dictionary
            api_key: Specific API key to use

        Returns:
            Analysis result string
        """
        analysis_type = request['type']
        method_name = request['method']
        args = request.get('args', [])
        kwargs = request.get('kwargs', {})

        stock_logger.debug(f"Executing {analysis_type} analysis with key ...{api_key[-8:]}")

        try:
            # Get the method from this instance
            method = getattr(self, method_name)

            # Temporarily override the key selection to use the assigned key
            original_get_key = self.key_manager.get_available_key

            def get_assigned_key():
                # Check if the assigned key is still available
                if self.key_manager._is_key_available(api_key):
                    return api_key
                else:
                    # Fall back to normal key selection if assigned key is no longer available
                    return original_get_key()

            self.key_manager.get_available_key = get_assigned_key

            try:
                # Execute the analysis method
                result = method(*args, **kwargs)
                return result
            finally:
                # Restore original key selection method
                self.key_manager.get_available_key = original_get_key

        except Exception as e:
            stock_logger.error(f"Error executing {analysis_type} with key ...{api_key[-8:]}: {e}")
            return f"Error executing {analysis_type}: {str(e)}"

    def _generate_sequential_analysis(self, analysis_requests: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Fallback method to generate analyses sequentially

        Args:
            analysis_requests: List of analysis request dictionaries

        Returns:
            Dictionary mapping analysis type to result
        """
        results = {}

        for request in analysis_requests:
            analysis_type = request['type']
            method_name = request['method']
            args = request.get('args', [])
            kwargs = request.get('kwargs', {})

            try:
                method = getattr(self, method_name)
                result = method(*args, **kwargs)
                results[analysis_type] = result
                stock_logger.info(f"Completed sequential analysis: {analysis_type}")
            except Exception as e:
                stock_logger.error(f"Sequential analysis failed for {analysis_type}: {e}")
                results[analysis_type] = f"Error in sequential processing: {str(e)}"

        return results