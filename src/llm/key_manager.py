"""
Gemini API Key Manager with rate limiting and load balancing
"""

import time
import threading
from typing import List, Dict, Optional
from collections import deque
from dataclasses import dataclass
from src.utils.logger import stock_logger


@dataclass
class KeyUsage:
    """Track usage statistics for an API key"""
    key: str
    request_times: deque  # Store timestamps of requests
    total_requests: int = 0
    last_used: float = 0.0
    is_rate_limited: bool = False
    rate_limit_until: float = 0.0
    rate_limit_recovery_time: Optional[float] = None  # When key recovered from rate limit
    consecutive_rate_limits: int = 0  # Track how often this key gets rate limited
    rate_limit_history: deque = None  # Track recent rate limit events


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

        # Simple tracking: just track rate limited keys and when they'll be available
        self.rate_limited_keys: Dict[str, float] = {}  # key -> timestamp when available again
        self.request_counts: Dict[str, deque] = {}  # key -> deque of request timestamps

        # Initialize request tracking
        for key in api_keys:
            self.request_counts[key] = deque(maxlen=max_requests_per_minute)
        
        stock_logger.info(f"Initialized Gemini Key Manager with {len(api_keys)} keys, "
                         f"max {max_requests_per_minute} requests per minute per key")

        # Log key identifiers for debugging (last 8 characters)
        key_ids = [f"...{key[-8:]}" for key in api_keys]
        stock_logger.info(f"Available keys: {key_ids}")
    
    def _cleanup_old_requests(self, key_usage: KeyUsage) -> None:
        """Remove request timestamps older than 1 minute"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Remove timestamps older than 1 minute
        while key_usage.request_times and key_usage.request_times[0] < minute_ago:
            key_usage.request_times.popleft()
    
    def _is_key_available(self, key: str) -> bool:
        """Check if a key is available for use (not rate limited)"""
        key_usage = self.key_usage[key]
        current_time = time.time()

        # Check if key is temporarily rate limited
        if key_usage.is_rate_limited and current_time < key_usage.rate_limit_until:
            remaining_time = key_usage.rate_limit_until - current_time
            stock_logger.debug(f"Key ...{key[-8:]} still rate limited for {remaining_time:.1f}s")
            return False

        # Reset rate limit flag if time has passed
        if key_usage.is_rate_limited and current_time >= key_usage.rate_limit_until:
            key_usage.is_rate_limited = False
            key_usage.rate_limit_until = 0.0
            key_usage.rate_limit_recovery_time = current_time  # Track when key recovered
            stock_logger.info(f"Rate limit cleared for key ending in ...{key[-8:]}")

        # Clean up old requests
        old_count = len(key_usage.request_times)
        self._cleanup_old_requests(key_usage)
        new_count = len(key_usage.request_times)

        if old_count != new_count:
            stock_logger.debug(f"Cleaned up {old_count - new_count} old requests for key ...{key[-8:]}")

        # Check if we're under the rate limit
        is_available = len(key_usage.request_times) < self.max_requests_per_minute

        if not is_available:
            stock_logger.debug(f"Key ...{key[-8:]} at capacity: {len(key_usage.request_times)}/{self.max_requests_per_minute}")

        return is_available
    
    def get_available_key(self) -> Optional[str]:
        """
        Get an available API key using intelligent selection that avoids recently rate-limited keys

        Selection criteria (in order of priority):
        1. Avoid keys that recently recovered from rate limits (within last 30 seconds)
        2. Prefer keys with lowest current usage (least likely to hit rate limit)
        3. Prefer keys with fewer recent rate limit events
        4. Prefer keys with lower total usage for long-term balance

        Returns:
            Available API key or None if all keys are rate limited
        """
        with self.lock:
            available_keys = []
            current_time = time.time()

            # First, collect all available keys with their risk scores
            for key in self.api_keys:
                if self._is_key_available(key):
                    key_usage = self.key_usage[key]
                    self._cleanup_old_requests(key_usage)

                    current_requests = len(key_usage.request_times)
                    available_capacity = self.max_requests_per_minute - current_requests

                    # Calculate risk score (lower is better)
                    risk_score = self._calculate_key_risk_score(key_usage, current_time, current_requests)

                    available_keys.append((key, current_requests, available_capacity, risk_score, key_usage))

            if not available_keys:
                stock_logger.debug("No available keys found")
                return None

            # Sort by risk score (ascending - lower risk is better)
            available_keys.sort(key=lambda x: x[3])

            # Select the lowest risk key
            best_key, current_reqs, available_cap, risk_score, key_usage = available_keys[0]

            # Reset consecutive rate limits on successful selection (if key hasn't been rate limited recently)
            if key_usage.rate_limit_recovery_time is None or (current_time - key_usage.rate_limit_recovery_time) > 300:
                key_usage.consecutive_rate_limits = 0

            stock_logger.debug(f"Smart selection: key ...{best_key[-8:]} with {current_reqs}/{self.max_requests_per_minute} "
                             f"current requests, risk score: {risk_score:.2f}")

            # Log selection reasoning for top keys
            if len(available_keys) > 1:
                top_keys_info = []
                for k, cr, ac, rs, ku in available_keys[:3]:  # Show top 3 alternatives
                    recovery_info = ""
                    if ku.rate_limit_recovery_time:
                        time_since_recovery = current_time - ku.rate_limit_recovery_time
                        recovery_info = f", recovered {time_since_recovery:.0f}s ago"

                    top_keys_info.append(f"...{k[-8:]}(risk:{rs:.2f}, usage:{cr}/{self.max_requests_per_minute}{recovery_info})")

                stock_logger.debug(f"Key selection options: {', '.join(top_keys_info)}")

            return best_key

    def _calculate_key_risk_score(self, key_usage: KeyUsage, current_time: float, current_requests: int) -> float:
        """
        Calculate a risk score for a key (lower is better)

        Factors:
        - Current usage (most important): Higher usage = higher risk
        - Recent recovery penalty: Keys that just recovered from rate limit get penalty
        - Rate limit frequency: Keys that get rate limited often get penalty
        - Historical usage: Slight preference for less used keys
        """
        risk_score = 0.0

        # 1. Current usage risk (0-100 points, most important factor)
        usage_ratio = current_requests / self.max_requests_per_minute
        risk_score += usage_ratio * 100

        # 2. Recent recovery penalty (0-50 points)
        if key_usage.rate_limit_recovery_time:
            time_since_recovery = current_time - key_usage.rate_limit_recovery_time
            if time_since_recovery < 30:  # Penalize keys that recovered within last 30 seconds
                recovery_penalty = (30 - time_since_recovery) / 30 * 50
                risk_score += recovery_penalty

        # 3. Rate limit frequency penalty (0-30 points)
        if key_usage.rate_limit_history:
            # Count rate limits in the last 10 minutes
            recent_rate_limits = sum(1 for rl_time in key_usage.rate_limit_history
                                   if current_time - rl_time < 600)
            risk_score += recent_rate_limits * 10

        # 4. Consecutive rate limits penalty (0-20 points)
        risk_score += key_usage.consecutive_rate_limits * 5

        # 5. Historical usage balance (0-10 points)
        # Slight preference for keys with lower total usage
        avg_total_requests = sum(ku.total_requests for ku in self.key_usage.values()) / len(self.key_usage)
        if avg_total_requests > 0:
            usage_deviation = (key_usage.total_requests - avg_total_requests) / avg_total_requests
            risk_score += max(0, usage_deviation) * 10

        return risk_score

    def get_multiple_available_keys(self, count: int = None) -> List[str]:
        """
        Get multiple available keys for parallel processing using smart selection

        Args:
            count: Number of keys to return (None = all available)

        Returns:
            List of available API keys sorted by risk score (lowest risk first)
        """
        with self.lock:
            available_keys = []
            current_time = time.time()

            for key in self.api_keys:
                if self._is_key_available(key):
                    key_usage = self.key_usage[key]
                    self._cleanup_old_requests(key_usage)

                    current_requests = len(key_usage.request_times)
                    risk_score = self._calculate_key_risk_score(key_usage, current_time, current_requests)

                    available_keys.append((key, current_requests, risk_score))

            # Sort by risk score (ascending - lower risk first)
            available_keys.sort(key=lambda x: x[2])

            # Return requested number of keys
            if count is None:
                result_keys = [key for key, _, _ in available_keys]
            else:
                result_keys = [key for key, _, _ in available_keys[:count]]

            if result_keys:
                key_info = [(f"...{k[-8:]}", f"{cr}/{self.max_requests_per_minute}", f"risk:{rs:.1f}")
                           for k, cr, rs in available_keys[:len(result_keys)]]
                stock_logger.info(f"Returning {len(result_keys)} keys for parallel processing: {key_info}")

            return result_keys
    
    def record_request(self, key: str) -> None:
        """Record a successful request for the given key"""
        with self.lock:
            if key in self.key_usage:
                key_usage = self.key_usage[key]
                current_time = time.time()
                
                key_usage.request_times.append(current_time)
                key_usage.total_requests += 1
                key_usage.last_used = current_time
                
                stock_logger.debug(f"Recorded request for key ending in ...{key[-8:]}. "
                                 f"Current usage: {len(key_usage.request_times)}/{self.max_requests_per_minute}")
    
    def record_rate_limit(self, key: str, retry_after: Optional[int] = None) -> None:
        """
        Record that a key hit rate limit

        Args:
            key: The API key that hit rate limit
            retry_after: Seconds to wait before retrying (from API response)
        """
        with self.lock:
            if key in self.key_usage:
                key_usage = self.key_usage[key]
                current_time = time.time()

                # Set rate limit duration (default to 60 seconds if not specified)
                wait_time = retry_after if retry_after else 60
                key_usage.is_rate_limited = True
                key_usage.rate_limit_until = current_time + wait_time
                key_usage.consecutive_rate_limits += 1

                # Track rate limit event in history
                key_usage.rate_limit_history.append(current_time)

                stock_logger.warning(f"Key ending in ...{key[-8:]} hit rate limit. "
                                   f"Will retry after {wait_time} seconds "
                                   f"(consecutive rate limits: {key_usage.consecutive_rate_limits})")
    
    def get_next_available_time(self) -> float:
        """
        Get the timestamp when the next key will become available
        
        Returns:
            Timestamp when a key will be available, or current time if one is available now
        """
        with self.lock:
            current_time = time.time()
            earliest_available = float('inf')
            
            for key in self.api_keys:
                key_usage = self.key_usage[key]
                
                if self._is_key_available(key):
                    return current_time  # Key available now
                
                if key_usage.is_rate_limited:
                    earliest_available = min(earliest_available, key_usage.rate_limit_until)
                else:
                    # Calculate when this key will have capacity based on request times
                    self._cleanup_old_requests(key_usage)
                    if key_usage.request_times:
                        # When the oldest request will be 1 minute old
                        oldest_request = key_usage.request_times[0]
                        available_at = oldest_request + 60
                        earliest_available = min(earliest_available, available_at)
            
            return earliest_available if earliest_available != float('inf') else current_time + 60
    
    def get_usage_stats(self) -> Dict[str, Dict]:
        """Get usage statistics for all keys"""
        with self.lock:
            stats = {}
            current_time = time.time()
            
            for key, usage in self.key_usage.items():
                self._cleanup_old_requests(usage)
                
                stats[f"...{key[-8:]}"] = {
                    "total_requests": usage.total_requests,
                    "current_minute_requests": len(usage.request_times),
                    "max_requests_per_minute": self.max_requests_per_minute,
                    "is_rate_limited": usage.is_rate_limited,
                    "rate_limit_until": usage.rate_limit_until if usage.is_rate_limited else None,
                    "last_used": usage.last_used,
                    "available": self._is_key_available(key)
                }
            
            return stats

    def get_key_summary(self) -> str:
        """Get a quick summary of key availability"""
        with self.lock:
            total_keys = len(self.api_keys)
            available_keys = sum(1 for key in self.api_keys if self._is_key_available(key))
            rate_limited_keys = sum(1 for key in self.api_keys if self.key_usage[key].is_rate_limited)

            return f"{available_keys}/{total_keys} keys available, {rate_limited_keys} rate limited"

    def wait_for_available_key(self, max_wait_time: float = 300) -> Optional[str]:
        """
        Wait for an available key, up to max_wait_time seconds

        Args:
            max_wait_time: Maximum time to wait in seconds

        Returns:
            Available API key or None if timeout reached
        """
        start_time = time.time()
        immediate_retry_count = 0
        max_immediate_retries = 5  # Prevent infinite busy waiting
        min_sleep_time = 0.5  # Minimum sleep to prevent busy waiting

        stock_logger.info(f"Waiting for available API key (max wait: {max_wait_time:.1f}s)")

        while time.time() - start_time < max_wait_time:
            key = self.get_available_key()
            if key:
                stock_logger.info(f"Found available key ending in ...{key[-8:]} after {time.time() - start_time:.1f}s")
                return key

            # Calculate how long to wait
            next_available = self.get_next_available_time()
            current_time = time.time()
            elapsed_time = current_time - start_time
            remaining_time = max_wait_time - elapsed_time

            stock_logger.debug(f"No keys available. Next available at: {next_available:.1f}, current: {current_time:.1f}")

            if next_available <= current_time:
                # Key should be available now, but might need a moment to update
                immediate_retry_count += 1
                if immediate_retry_count >= max_immediate_retries:
                    # Force a minimum sleep to prevent infinite busy waiting
                    stock_logger.warning(f"Too many immediate retries ({immediate_retry_count}), forcing {min_sleep_time}s sleep")
                    time.sleep(min_sleep_time)
                    immediate_retry_count = 0
                else:
                    # Small delay to allow for state updates
                    time.sleep(0.1)
                continue

            # Reset immediate retry counter since we're doing a proper wait
            immediate_retry_count = 0

            wait_time = min(next_available - current_time, remaining_time)

            if wait_time > 0:
                # Add minimum sleep time to prevent too frequent checks
                actual_wait_time = max(wait_time, min_sleep_time)
                stock_logger.info(f"All keys rate limited. Waiting {actual_wait_time:.1f} seconds for next available key... (remaining timeout: {remaining_time:.1f}s)")
                time.sleep(actual_wait_time)
            else:
                # No time left to wait
                break

        stock_logger.error(f"Timeout waiting for available API key after {max_wait_time} seconds")

        # Log current key status for debugging
        stats = self.get_usage_stats()
        for key_id, stat in stats.items():
            stock_logger.error(f"Key {key_id}: available={stat['available']}, rate_limited={stat['is_rate_limited']}, "
                             f"requests={stat['current_minute_requests']}/{stat['max_requests_per_minute']}")

        return None

    def should_abort_waiting(self) -> bool:
        """
        Check if we should abort waiting for keys based on rate limit status

        Returns True if all keys are rate limited for a very long time
        """
        with self.lock:
            current_time = time.time()
            all_keys_long_term_limited = True

            for key in self.api_keys:
                key_usage = self.key_usage[key]

                # If key is not rate limited, we shouldn't abort
                if not key_usage.is_rate_limited:
                    all_keys_long_term_limited = False
                    break

                # If key will be available within 5 minutes, we shouldn't abort
                if key_usage.rate_limit_until - current_time < 300:  # 5 minutes
                    all_keys_long_term_limited = False
                    break

            if all_keys_long_term_limited:
                stock_logger.warning("All keys are rate limited for extended periods. Consider aborting.")
                return True

            return False


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
