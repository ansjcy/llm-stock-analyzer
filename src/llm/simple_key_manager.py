"""
Simple Gemini API Key Manager for load balancing and rate limiting
"""

import time
import threading
from collections import deque
from typing import Dict, List, Optional

from src.utils.logger import stock_logger


class GeminiKeyManager:
    """
    Simple Gemini API key manager with round-robin selection and rate limit tracking
    """

    def __init__(self, api_keys: List[str], max_requests_per_minute: int = 10):
        """
        Initialize the key manager
        
        Args:
            api_keys: List of Gemini API keys
            max_requests_per_minute: Maximum requests per key per minute
        """
        if not api_keys:
            raise ValueError("At least one API key must be provided")
        
        self.api_keys = api_keys
        self.max_requests_per_minute = max_requests_per_minute
        self.current_key_index = 0
        self.lock = threading.Lock()
        
        # Simple tracking
        self.rate_limited_keys: Dict[str, float] = {}  # key -> timestamp when available again
        self.request_counts: Dict[str, deque] = {}  # key -> deque of request timestamps
        
        # Initialize request tracking
        for key in api_keys:
            self.request_counts[key] = deque(maxlen=max_requests_per_minute)
        
        stock_logger.info(f"Initialized Gemini Key Manager with {len(api_keys)} keys, "
                         f"max {max_requests_per_minute} requests per minute per key")

    def _cleanup_old_requests(self, key: str) -> None:
        """Remove request timestamps older than 1 minute"""
        current_time = time.time()
        cutoff_time = current_time - 60  # 1 minute ago
        
        # Remove old timestamps
        request_times = self.request_counts[key]
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Clear rate limit if time has passed
        if key in self.rate_limited_keys and current_time >= self.rate_limited_keys[key]:
            del self.rate_limited_keys[key]
            stock_logger.info(f"Key ending in ...{key[-8:]} recovered from rate limit")

    def _is_key_available(self, key: str) -> bool:
        """Check if a key is available for use"""
        current_time = time.time()
        
        # Clean up old requests first
        self._cleanup_old_requests(key)
        
        # Check if rate limited
        if key in self.rate_limited_keys and current_time < self.rate_limited_keys[key]:
            return False

        # Check if we're under the rate limit
        current_requests = len(self.request_counts[key])
        is_available = current_requests < self.max_requests_per_minute

        return is_available

    def get_available_key(self) -> Optional[str]:
        """
        Get an available API key using simple round-robin selection
        
        Returns:
            Available API key or None if all keys are rate limited
        """
        with self.lock:
            # Try each key starting from current index
            for i in range(len(self.api_keys)):
                key_index = (self.current_key_index + i) % len(self.api_keys)
                key = self.api_keys[key_index]
                
                if self._is_key_available(key):
                    # Update current index for next call
                    self.current_key_index = (key_index + 1) % len(self.api_keys)
                    
                    current_requests = len(self.request_counts[key])
                    stock_logger.info(f"Selected key ...{key[-8:]} (usage: {current_requests}/{self.max_requests_per_minute})")
                    return key
            
            # No available keys
            stock_logger.warning("No available API keys found")
            return None

    def record_request(self, key: str) -> None:
        """Record a successful request for the given key"""
        with self.lock:
            if key in self.request_counts:
                current_time = time.time()
                self.request_counts[key].append(current_time)
                
                current_requests = len(self.request_counts[key])
                stock_logger.debug(f"Recorded request for key ending in ...{key[-8:]}. "
                                 f"Current usage: {current_requests}/{self.max_requests_per_minute}")

    def record_rate_limit(self, key: str, retry_after: Optional[int] = None) -> None:
        """
        Record that a key hit rate limit
        
        Args:
            key: The API key that hit rate limit
            retry_after: Seconds to wait before retrying (from API response)
        """
        with self.lock:
            current_time = time.time()
            
            # Set rate limit duration (default to 60 seconds if not specified)
            wait_time = retry_after if retry_after else 60
            self.rate_limited_keys[key] = current_time + wait_time
            
            stock_logger.warning(f"Key ending in ...{key[-8:]} hit rate limit. "
                               f"Will retry after {wait_time} seconds")

    def get_key_summary(self) -> str:
        """Get a quick summary of key availability"""
        with self.lock:
            total_keys = len(self.api_keys)
            available_keys = sum(1 for key in self.api_keys if self._is_key_available(key))
            rate_limited_keys = len(self.rate_limited_keys)

            return f"{available_keys}/{total_keys} keys available, {rate_limited_keys} rate limited"


class RetryConfig:
    """Configuration for retry mechanism"""

    def __init__(self,
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-based)"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)
