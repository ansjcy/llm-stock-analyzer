"""
Yahoo Finance data fetcher for stock information
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import json
import os
from pathlib import Path

from src.utils.logger import stock_logger
from src.utils.config import config


class YahooFinanceAPI:
    """Yahoo Finance data API wrapper with enhanced anti-blocking measures"""

    def __init__(self):
        self.session = requests.Session()
        # Enhanced user agents with more recent versions
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            # Firefox on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        ]
        self.current_ua_index = 0
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        self.cache_dir = Path("cache/yahoo_finance")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._setup_session()

    def _setup_session(self):
        """Setup session with browser-like headers"""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        self._update_user_agent()

    def _update_user_agent(self):
        """Update session with next user agent and randomize some headers"""
        self.session.headers.update({
            'User-Agent': self.user_agents[self.current_ua_index]
        })
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)

        # Add some randomization to headers
        if random.random() < 0.3:  # 30% chance to add referer
            self.session.headers['Referer'] = 'https://finance.yahoo.com/'
        elif 'Referer' in self.session.headers:
            del self.session.headers['Referer']

    def _rate_limit(self):
        """Implement rate limiting to avoid being blocked"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last + random.uniform(0.1, 0.5)
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_cache_path(self, ticker: str, data_type: str) -> Path:
        """Get cache file path for a ticker and data type"""
        today = datetime.now().strftime("%Y%m%d")
        return self.cache_dir / f"{ticker}_{data_type}_{today}.json"

    def _load_from_cache(self, ticker: str, data_type: str) -> Optional[Dict[str, Any]]:
        """Load data from cache if available and recent"""
        cache_path = self._get_cache_path(ticker, data_type)
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                stock_logger.info(f"Loaded {data_type} for {ticker} from cache")
                return cached_data
            except Exception as e:
                stock_logger.warning(f"Failed to load cache for {ticker} {data_type}: {e}")
        return None

    def _save_to_cache(self, ticker: str, data_type: str, data: Dict[str, Any]):
        """Save data to cache"""
        try:
            cache_path = self._get_cache_path(ticker, data_type)
            with open(cache_path, 'w') as f:
                json.dump(data, f, default=str, indent=2)
            stock_logger.debug(f"Cached {data_type} for {ticker}")
        except Exception as e:
            stock_logger.warning(f"Failed to cache data for {ticker} {data_type}: {e}")

    def _load_yesterday_data(self, ticker: str, data_type: str) -> Optional[Dict[str, Any]]:
        """Load yesterday's data as fallback"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        cache_path = self.cache_dir / f"{ticker}_{data_type}_{yesterday}.json"
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                stock_logger.info(f"Using yesterday's {data_type} data for {ticker} as fallback")
                return cached_data
            except Exception as e:
                stock_logger.warning(f"Failed to load yesterday's cache for {ticker} {data_type}: {e}")
        return None
    
    def get_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get basic stock information with enhanced retry logic and caching"""
        # Try to load from cache first
        cached_data = self._load_from_cache(ticker, "stock_info")
        if cached_data:
            return cached_data

        max_retries = 5  # Increased retries
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                # Rate limiting and user agent rotation
                self._rate_limit()
                if attempt > 0:
                    self._update_user_agent()
                    stock_logger.info(f"Retry {attempt} for {ticker} with new user agent")

                # Let yfinance handle its own session management (newer versions require curl_cffi)
                stock = yf.Ticker(ticker)
                info = stock.info

                # Check if we got valid data
                if not info or len(info) < 5:  # Basic validation
                    raise ValueError("Insufficient data returned")

                stock_logger.info(f"Retrieved stock info for {ticker}")

                # Normalize financial ratios to handle different formats
                normalized_info = self._normalize_financial_ratios(info)

                result = {
                    'symbol': ticker,
                    'name': info.get('longName', ticker),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'country': info.get('country', 'N/A'),
                    'currency': info.get('currency', 'USD'),
                    'market_cap': info.get('marketCap'),
                    'shares_outstanding': info.get('sharesOutstanding'),
                    'total_revenue': info.get('totalRevenue'),
                    'total_cash': info.get('totalCash'),
                    'total_debt': info.get('totalDebt'),
                    'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                    'regular_market_price': info.get('regularMarketPrice'),
                    'previous_close': info.get('previousClose'),
                    'open': info.get('open'),
                    'day_high': info.get('dayHigh'),
                    'day_low': info.get('dayLow'),
                    'volume': info.get('volume'),
                    'avg_volume': info.get('averageVolume'),
                    'pe_ratio': info.get('trailingPE'),
                    'forward_pe': info.get('forwardPE'),
                    'peg_ratio': info.get('pegRatio'),
                    'price_to_book': info.get('priceToBook'),
                    'price_to_sales': info.get('priceToSalesTrailing12Months'),
                    'dividend_yield': info.get('dividendYield'),
                    'beta': info.get('beta'),
                    'trailing_eps': info.get('trailingEps'),
                    'forward_eps': info.get('forwardEps'),
                    'book_value': normalized_info.get('bookValue'),
                    'price_to_book': normalized_info.get('priceToBook'),
                    'return_on_equity': normalized_info.get('returnOnEquity'),
                    'return_on_assets': normalized_info.get('returnOnAssets'),
                    'debt_to_equity': normalized_info.get('debtToEquity'),
                    'current_ratio': normalized_info.get('currentRatio'),
                    'quick_ratio': normalized_info.get('quickRatio'),
                    'gross_margins': normalized_info.get('grossMargins'),
                    'operating_margins': normalized_info.get('operatingMargins'),
                    'profit_margins': normalized_info.get('profitMargins'),
                    'revenue_growth': normalized_info.get('revenueGrowth'),
                    'earnings_growth': normalized_info.get('earningsGrowth'),
                    '52_week_high': info.get('fiftyTwoWeekHigh'),
                    '52_week_low': info.get('fiftyTwoWeekLow'),
                    'analyst_target_price': info.get('targetMeanPrice'),
                    'recommendation': info.get('recommendationMean'),
                    'recommendation_key': info.get('recommendationKey'),
                    'number_of_analyst_opinions': normalized_info.get('numberOfAnalystOpinions'),
                    'full_time_employees': normalized_info.get('fullTimeEmployees'),
                    'data_source': 'yahoo_finance',
                    'retrieved_at': datetime.now().isoformat()
                }

                # Cache the successful result
                self._save_to_cache(ticker, "stock_info", result)
                return result

            except Exception as e:
                error_msg = str(e)
                stock_logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {error_msg}")

                # Check if it's a 401 error specifically
                if "401" in error_msg or "Unauthorized" in error_msg:
                    stock_logger.warning(f"401 Unauthorized error for {ticker}, trying enhanced bypass methods")
                    # Longer delay for 401 errors
                    delay = base_delay * (2 ** attempt) + random.uniform(1, 3)
                    time.sleep(delay)
                elif "429" in error_msg or "Too Many Requests" in error_msg:
                    stock_logger.warning(f"Rate limit hit for {ticker}, backing off")
                    delay = base_delay * (3 ** attempt) + random.uniform(2, 5)
                    time.sleep(delay)
                else:
                    # Standard progressive delay
                    delay = base_delay * (1.5 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(delay)

                if attempt == max_retries - 1:
                    stock_logger.error(f"All {max_retries} attempts failed for {ticker}")

                    # Try alternative access methods before giving up
                    alt_info = self._try_alternative_yfinance_access(ticker)
                    if alt_info:
                        # Process the alternative data the same way
                        normalized_info = self._normalize_financial_ratios(alt_info)
                        result = {
                            'symbol': ticker,
                            'name': alt_info.get('longName', ticker),
                            'sector': alt_info.get('sector', 'N/A'),
                            'industry': alt_info.get('industry', 'N/A'),
                            'country': alt_info.get('country', 'N/A'),
                            'currency': alt_info.get('currency', 'USD'),
                            'market_cap': alt_info.get('marketCap'),
                            'shares_outstanding': alt_info.get('sharesOutstanding'),
                            'total_revenue': alt_info.get('totalRevenue'),
                            'total_cash': alt_info.get('totalCash'),
                            'total_debt': alt_info.get('totalDebt'),
                            'current_price': alt_info.get('currentPrice') or alt_info.get('regularMarketPrice'),
                            'regular_market_price': alt_info.get('regularMarketPrice'),
                            'previous_close': alt_info.get('previousClose'),
                            'open': alt_info.get('open'),
                            'day_high': alt_info.get('dayHigh'),
                            'day_low': alt_info.get('dayLow'),
                            'volume': alt_info.get('volume'),
                            'avg_volume': alt_info.get('averageVolume'),
                            'pe_ratio': alt_info.get('trailingPE'),
                            'forward_pe': alt_info.get('forwardPE'),
                            'peg_ratio': alt_info.get('pegRatio'),
                            'price_to_book': alt_info.get('priceToBook'),
                            'price_to_sales': alt_info.get('priceToSalesTrailing12Months'),
                            'dividend_yield': alt_info.get('dividendYield'),
                            'beta': alt_info.get('beta'),
                            'trailing_eps': alt_info.get('trailingEps'),
                            'forward_eps': alt_info.get('forwardEps'),
                            'book_value': normalized_info.get('bookValue'),
                            'price_to_book': normalized_info.get('priceToBook'),
                            'return_on_equity': normalized_info.get('returnOnEquity'),
                            'return_on_assets': normalized_info.get('returnOnAssets'),
                            'debt_to_equity': normalized_info.get('debtToEquity'),
                            'current_ratio': normalized_info.get('currentRatio'),
                            'quick_ratio': normalized_info.get('quickRatio'),
                            'gross_margins': normalized_info.get('grossMargins'),
                            'operating_margins': normalized_info.get('operatingMargins'),
                            'profit_margins': normalized_info.get('profitMargins'),
                            'revenue_growth': normalized_info.get('revenueGrowth'),
                            'earnings_growth': normalized_info.get('earningsGrowth'),
                            '52_week_high': alt_info.get('fiftyTwoWeekHigh'),
                            '52_week_low': alt_info.get('fiftyTwoWeekLow'),
                            'analyst_target_price': alt_info.get('targetMeanPrice'),
                            'recommendation': alt_info.get('recommendationMean'),
                            'recommendation_key': alt_info.get('recommendationKey'),
                            'number_of_analyst_opinions': normalized_info.get('numberOfAnalystOpinions'),
                            'full_time_employees': normalized_info.get('fullTimeEmployees'),
                            'data_source': 'yahoo_finance_alternative',
                            'retrieved_at': datetime.now().isoformat()
                        }
                        self._save_to_cache(ticker, "stock_info", result)
                        return result

                    # Try to load yesterday's data as final fallback
                    fallback_data = self._load_yesterday_data(ticker, "stock_info")
                    if fallback_data:
                        fallback_data['data_source'] = 'cache_fallback'
                        fallback_data['retrieved_at'] = datetime.now().isoformat()
                        return fallback_data
                    return None

        return None

    def _normalize_financial_ratios(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize financial ratios to handle different formats and edge cases"""
        normalized = info.copy()

        # Normalize debt-to-equity ratio
        debt_to_equity = info.get('debtToEquity')
        if debt_to_equity is not None and debt_to_equity > 0:
            # Yahoo Finance sometimes returns debt-to-equity as a percentage (180.05)
            # when it should be a ratio (1.8005). Values > 10 are likely percentages.
            if debt_to_equity > 10:
                normalized['debtToEquity'] = debt_to_equity / 100
            else:
                normalized['debtToEquity'] = debt_to_equity

        # Normalize ROE - handle both decimal and percentage formats
        roe = info.get('returnOnEquity')
        if roe is not None:
            # If ROE > 1, it's likely a percentage, convert to decimal
            if roe > 1:
                normalized['returnOnEquity'] = roe / 100
            else:
                normalized['returnOnEquity'] = roe

        # Normalize earnings growth - handle extreme values
        earnings_growth = info.get('earningsGrowth')
        if earnings_growth is not None:
            # Cap extreme values and handle negatives
            if earnings_growth < -1 or earnings_growth > 10:  # Cap at 1000% growth
                normalized['earningsGrowth'] = None
            else:
                normalized['earningsGrowth'] = earnings_growth

        # Normalize revenue growth - handle extreme values
        revenue_growth = info.get('revenueGrowth')
        if revenue_growth is not None:
            # Cap extreme values and handle negatives
            if revenue_growth < -1 or revenue_growth > 10:  # Cap at 1000% growth
                normalized['revenueGrowth'] = None
            else:
                normalized['revenueGrowth'] = revenue_growth

        # Normalize P/E ratio - handle extreme values
        pe_ratio = info.get('trailingPE')
        if pe_ratio is not None:
            # Filter out unrealistic P/E ratios
            if pe_ratio <= 0 or pe_ratio > 1000:
                normalized['trailingPE'] = None
            else:
                normalized['trailingPE'] = pe_ratio

        return normalized
    
    def get_historical_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical stock data with enhanced error handling"""
        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                if attempt > 0:
                    self._update_user_agent()
                    stock_logger.info(f"Retry {attempt} for historical data {ticker}")

                stock = yf.Ticker(ticker)
                hist = stock.history(period=period, interval=interval)

                if hist.empty:
                    stock_logger.warning(f"No historical data found for {ticker}")
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (attempt + 1))
                        continue
                    return None

                # Ensure the DataFrame has the expected columns
                expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in expected_columns:
                    if col not in hist.columns:
                        stock_logger.warning(f"Missing column {col} in historical data for {ticker}")

                stock_logger.info(f"Retrieved {len(hist)} days of historical data for {ticker}")
                return hist

            except Exception as e:
                error_msg = str(e)
                stock_logger.warning(f"Attempt {attempt + 1} failed for historical data {ticker}: {error_msg}")

                if attempt == max_retries - 1:
                    stock_logger.error(f"All attempts failed for historical data {ticker}")
                    return None

                # Progressive delay with randomization
                delay = base_delay * (1.5 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(delay)

        return None

    def _try_alternative_yfinance_access(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Try alternative methods to access Yahoo Finance data"""
        stock_logger.info(f"Trying alternative access methods for {ticker}")

        try:
            # Method 1: Clear yfinance cache and retry
            import yfinance.utils as yf_utils

            # Reset yfinance cache
            if hasattr(yf_utils, '_CACHE'):
                yf_utils._CACHE = {}

            stock = yf.Ticker(ticker)
            info = stock.info

            if info and len(info) > 5:
                stock_logger.info(f"Alternative method 1 (cache reset) succeeded for {ticker}")
                return info

        except Exception as e:
            stock_logger.debug(f"Alternative method 1 failed for {ticker}: {e}")

        try:
            # Method 2: Try with a small delay and fresh ticker instance
            time.sleep(random.uniform(2, 5))
            stock = yf.Ticker(ticker)
            info = stock.info

            if info and len(info) > 5:
                stock_logger.info(f"Alternative method 2 (delayed retry) succeeded for {ticker}")
                return info

        except Exception as e:
            stock_logger.debug(f"Alternative method 2 failed for {ticker}: {e}")

        stock_logger.warning(f"All alternative methods failed for {ticker}")
        return None

    def _configure_proxy_if_available(self):
        """Configure proxy if available in environment"""
        proxy_url = os.getenv('YAHOO_FINANCE_PROXY')
        if proxy_url:
            self.session.proxies.update({
                'http': proxy_url,
                'https': proxy_url
            })
            stock_logger.info("Configured proxy for Yahoo Finance requests")

    def get_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive financial data with enhanced retry logic"""
        # Try to load from cache first
        cached_data = self._load_from_cache(ticker, "financial_data")
        if cached_data:
            return cached_data

        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                if attempt > 0:
                    self._update_user_agent()
                    stock_logger.info(f"Retry {attempt} for financial data {ticker}")

                stock = yf.Ticker(ticker)

                # Get financial statements
                financials = {}

                try:
                    financials['income_statement'] = stock.financials
                    financials['balance_sheet'] = stock.balance_sheet
                    financials['cash_flow'] = stock.cashflow
                    financials['quarterly_financials'] = stock.quarterly_financials
                    financials['quarterly_balance_sheet'] = stock.quarterly_balance_sheet
                    financials['quarterly_cashflow'] = stock.quarterly_cashflow
                except Exception as e:
                    stock_logger.warning(f"Some financial data unavailable for {ticker}: {e}")

                stock_logger.info(f"Retrieved financial data for {ticker}")

                # Cache the result
                self._save_to_cache(ticker, "financial_data", financials)
                return financials

            except Exception as e:
                error_msg = str(e)
                stock_logger.warning(f"Attempt {attempt + 1} failed for financial data {ticker}: {error_msg}")

                if attempt == max_retries - 1:
                    stock_logger.error(f"All attempts failed for financial data {ticker}")
                    # Try to load yesterday's data as fallback
                    fallback_data = self._load_yesterday_data(ticker, "financial_data")
                    if fallback_data:
                        return fallback_data
                    return {}

                # Progressive delay
                delay = base_delay * (1.5 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(delay)

        return {}
    
    def get_analyst_recommendations(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get analyst recommendations with enhanced retry logic"""
        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                if attempt > 0:
                    self._update_user_agent()
                    stock_logger.info(f"Retry {attempt} for analyst recommendations {ticker}")

                stock = yf.Ticker(ticker)
                recommendations = stock.recommendations

                if recommendations is None or recommendations.empty:
                    stock_logger.warning(f"No analyst recommendations found for {ticker}")
                    return None

                stock_logger.info(f"Retrieved analyst recommendations for {ticker}")
                return recommendations

            except Exception as e:
                error_msg = str(e)
                stock_logger.warning(f"Attempt {attempt + 1} failed for analyst recommendations {ticker}: {error_msg}")

                if attempt == max_retries - 1:
                    stock_logger.error(f"All attempts failed for analyst recommendations {ticker}")
                    return None

                # Progressive delay
                delay = base_delay * (1.5 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(delay)

        return None
    
    def get_institutional_holders(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get institutional holders information"""
        try:
            stock = yf.Ticker(ticker)
            holders = stock.institutional_holders
            
            if holders is None or holders.empty:
                stock_logger.warning(f"No institutional holders data found for {ticker}")
                return None
            
            stock_logger.info(f"Retrieved institutional holders for {ticker}")
            return holders
            
        except Exception as e:
            stock_logger.error(f"Error fetching institutional holders for {ticker}: {e}")
            return None
    
    def get_insider_transactions(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get insider transactions"""
        try:
            stock = yf.Ticker(ticker)
            insider_transactions = stock.insider_transactions
            
            if insider_transactions is None or insider_transactions.empty:
                stock_logger.warning(f"No insider transactions found for {ticker}")
                return None
            
            stock_logger.info(f"Retrieved insider transactions for {ticker}")
            return insider_transactions
            
        except Exception as e:
            stock_logger.error(f"Error fetching insider transactions for {ticker}: {e}")
            return None
    
    def get_earnings_calendar(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get earnings calendar with enhanced retry logic"""
        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                if attempt > 0:
                    self._update_user_agent()
                    stock_logger.info(f"Retry {attempt} for earnings calendar {ticker}")

                stock = yf.Ticker(ticker)
                calendar = stock.calendar

                # Handle both DataFrame and dict responses
                if calendar is None:
                    stock_logger.warning(f"No earnings calendar found for {ticker}")
                    return None
                elif hasattr(calendar, 'empty') and calendar.empty:
                    stock_logger.warning(f"Empty earnings calendar found for {ticker}")
                    return None
                elif isinstance(calendar, dict) and len(calendar) == 0:
                    stock_logger.warning(f"Empty earnings calendar dict found for {ticker}")
                    return None

                stock_logger.info(f"Retrieved earnings calendar for {ticker}")
                return calendar

            except Exception as e:
                error_msg = str(e)
                stock_logger.warning(f"Attempt {attempt + 1} failed for earnings calendar {ticker}: {error_msg}")

                if attempt == max_retries - 1:
                    stock_logger.error(f"All attempts failed for earnings calendar {ticker}")
                    return None

                # Progressive delay
                delay = base_delay * (1.5 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(delay)

        return None
    
    def search_stock_news(self, ticker: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for recent news about a stock with enhanced retry logic"""
        # Try to load from cache first
        cached_data = self._load_from_cache(ticker, "stock_news")
        if cached_data:
            return cached_data

        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                if attempt > 0:
                    self._update_user_agent()
                    stock_logger.info(f"Retry {attempt} for stock news {ticker}")

                stock = yf.Ticker(ticker)
                news = stock.news

                if not news:
                    stock_logger.warning(f"No news found for {ticker}")
                    return []

                # Limit results
                news = news[:max_results]

                processed_news = []
                for article in news:
                    # Handle both old and new API structure
                    if 'content' in article:
                        # New API structure with nested content
                        content = article['content']
                        processed_news.append({
                            'title': content.get('title', ''),
                            'publisher': content.get('provider', {}).get('displayName', '') if content.get('provider') else '',
                            'link': content.get('clickThroughUrl', {}).get('url', '') if content.get('clickThroughUrl') else '',
                            'publish_time': self._safe_timestamp(content.get('pubDate')),
                            'type': content.get('contentType', ''),
                            'thumbnail': content.get('thumbnail', {}).get('url', '') if content.get('thumbnail') else '',
                            'summary': content.get('description', '')
                        })
                    else:
                        # Old API structure (fallback)
                        processed_news.append({
                            'title': article.get('title', ''),
                            'publisher': article.get('publisher', ''),
                            'link': article.get('link', ''),
                            'publish_time': self._safe_timestamp(article.get('providerPublishTime')),
                            'type': article.get('type', ''),
                            'thumbnail': article.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '') if article.get('thumbnail') else '',
                            'summary': article.get('summary', '')
                        })

                stock_logger.info(f"Retrieved {len(processed_news)} news articles for {ticker}")

                # Cache the result
                self._save_to_cache(ticker, "stock_news", processed_news)
                return processed_news

            except Exception as e:
                error_msg = str(e)
                stock_logger.warning(f"Attempt {attempt + 1} failed for stock news {ticker}: {error_msg}")

                if attempt == max_retries - 1:
                    stock_logger.error(f"All attempts failed for stock news {ticker}")
                    # Try to load yesterday's data as fallback
                    fallback_data = self._load_yesterday_data(ticker, "stock_news")
                    if fallback_data:
                        return fallback_data
                    return []

                # Progressive delay
                delay = base_delay * (1.5 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(delay)

        return []
    
    def get_real_time_quote(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote data with enhanced retry logic"""
        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                if attempt > 0:
                    self._update_user_agent()
                    stock_logger.info(f"Retry {attempt} for real-time quote {ticker}")

                stock = yf.Ticker(ticker)

                # Get the most recent data
                hist = stock.history(period="2d", interval="1m")
                if hist.empty:
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (attempt + 1))
                        continue
                    return None

                latest = hist.iloc[-1]
                info = stock.info

                return {
                    'symbol': ticker,
                    'price': float(latest['Close']),
                    'change': float(latest['Close'] - info.get('previousClose', latest['Close'])),
                    'change_percent': ((latest['Close'] - info.get('previousClose', latest['Close'])) / info.get('previousClose', latest['Close'])) * 100,
                    'volume': int(latest['Volume']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'open': float(latest['Open']),
                    'previous_close': info.get('previousClose', float(latest['Close'])),
                    'timestamp': latest.name,
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('trailingPE'),
                    'dividend_yield': info.get('dividendYield')
                }

            except Exception as e:
                error_msg = str(e)
                stock_logger.warning(f"Attempt {attempt + 1} failed for real-time quote {ticker}: {error_msg}")

                if attempt == max_retries - 1:
                    stock_logger.error(f"All attempts failed for real-time quote {ticker}")
                    return None

                # Progressive delay
                delay = base_delay * (1.5 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(delay)

        return None

    def _safe_timestamp(self, timestamp):
        """Safely parse timestamp from various formats"""
        if not timestamp:
            return None
        try:
            # Try parsing as Unix timestamp (numeric)
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp)
            # Try parsing as ISO string format
            elif isinstance(timestamp, str):
                # Handle ISO format with Z timezone
                if timestamp.endswith('Z'):
                    timestamp = timestamp[:-1] + '+00:00'
                # Try different ISO formats
                for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(timestamp.replace('+00:00', ''), fmt)
                    except ValueError:
                        continue
                return None
            else:
                return None
        except (ValueError, TypeError) as e:
            stock_logger.warning(f"Invalid timestamp format: {timestamp} - {e}")
            return None

    def get_historical_pe_ratios(self, ticker: str, period: str = "2y") -> Optional[pd.DataFrame]:
        """Get historical PE ratios using earnings and price data with enhanced retry logic"""
        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                self._rate_limit()
                if attempt > 0:
                    self._update_user_agent()
                    stock_logger.info(f"Retry {attempt} for historical PE ratios {ticker}")

                stock = yf.Ticker(ticker)

                # Get historical price data
                hist_prices = stock.history(period=period, interval="1d")
                if hist_prices.empty:
                    stock_logger.warning(f"No historical price data found for {ticker}")
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (attempt + 1))
                        continue
                    return None

                # Get quarterly financials to calculate EPS
                try:
                    # Use income statement instead of deprecated earnings
                    quarterly_income = stock.quarterly_income_stmt
                    if quarterly_income is None or quarterly_income.empty:
                        stock_logger.warning(f"No quarterly income statement found for {ticker}")
                        if attempt < max_retries - 1:
                            time.sleep(base_delay * (attempt + 1))
                            continue
                        return None

                    # Find net income row
                    net_income_row = None
                    for idx in quarterly_income.index:
                        if any(term in str(idx).lower() for term in ['net income', 'net earnings']):
                            net_income_row = idx
                            break

                    if net_income_row is None:
                        stock_logger.warning(f"Could not find net income in income statement for {ticker}")
                        if attempt < max_retries - 1:
                            time.sleep(base_delay * (attempt + 1))
                            continue
                        return None

                    # Get shares outstanding from stock info
                    info = stock.info
                    shares_outstanding = info.get('sharesOutstanding', info.get('impliedSharesOutstanding'))

                    if not shares_outstanding:
                        stock_logger.warning(f"Could not get shares outstanding for {ticker}")
                        if attempt < max_retries - 1:
                            time.sleep(base_delay * (attempt + 1))
                            continue
                        return None

                    # Calculate quarterly EPS
                    quarterly_net_income = quarterly_income.loc[net_income_row]
                    quarterly_eps = quarterly_net_income / shares_outstanding

                    # Filter out invalid data
                    quarterly_eps = quarterly_eps.dropna()
                    if quarterly_eps.empty:
                        stock_logger.warning(f"No valid EPS data for {ticker}")
                        if attempt < max_retries - 1:
                            time.sleep(base_delay * (attempt + 1))
                            continue
                        return None

                except Exception as e:
                    stock_logger.warning(f"Error processing financial data for {ticker}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (attempt + 1))
                        continue
                    return None

                # Calculate TTM (Trailing Twelve Months) EPS for each date
                pe_data = []

                # Sort dates to ensure proper order
                quarterly_dates = sorted(quarterly_eps.index, reverse=True)

                # Normalize timezone for quarterly dates
                quarterly_dates_normalized = []
                for q_date in quarterly_dates:
                    if hasattr(q_date, 'tz_localize'):
                        # If it has timezone info, normalize it
                        if q_date.tz is not None:
                            q_date = q_date.tz_localize(None)
                    quarterly_dates_normalized.append(q_date)

                # Process every 5th day to reduce data points while maintaining trend
                price_dates = hist_prices.index[::5]  # Every 5th day

                for date in price_dates:
                    # Normalize the date for comparison
                    date_normalized = date
                    if hasattr(date, 'tz_localize') and date.tz is not None:
                        date_normalized = date.tz_localize(None)

                    price = hist_prices.loc[date, 'Close']

                    # Find the four most recent quarters before this date
                    relevant_quarters = []
                    for i, q_date in enumerate(quarterly_dates_normalized):
                        if q_date <= date_normalized:
                            relevant_quarters.append(quarterly_eps.iloc[i])
                        if len(relevant_quarters) == 4:
                            break

                    if len(relevant_quarters) >= 4:
                        ttm_eps = sum(relevant_quarters)
                        if ttm_eps > 0:
                            pe_ratio = price / ttm_eps
                            # Filter out unrealistic PE ratios
                            if 0 < pe_ratio <= 150:  # Reasonable PE range
                                pe_data.append({
                                    'Date': date.isoformat(),  # Convert to ISO format string for better JSON serialization
                                    'Close': price,
                                    'TTM_EPS': ttm_eps,
                                    'PE_Ratio': pe_ratio,
                                    'timestamp': int(date.timestamp())  # Add Unix timestamp for frontend usage
                                })

                if pe_data:
                    pe_df = pd.DataFrame(pe_data)
                    # Convert Date back to datetime for DataFrame index, but keep the ISO string in the data
                    pe_df['DateIndex'] = pd.to_datetime(pe_df['Date'])
                    pe_df.set_index('DateIndex', inplace=True)
                    stock_logger.info(f"Retrieved {len(pe_df)} PE ratio data points for {ticker}")
                    return pe_df
                else:
                    stock_logger.warning(f"Could not calculate PE ratios for {ticker}")
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (attempt + 1))
                        continue
                    return None

            except Exception as e:
                error_msg = str(e)
                stock_logger.warning(f"Attempt {attempt + 1} failed for historical PE ratios {ticker}: {error_msg}")

                if attempt == max_retries - 1:
                    stock_logger.error(f"All attempts failed for historical PE ratios {ticker}")
                    return None

                # Progressive delay
                delay = base_delay * (1.5 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(delay)

        return None

    def get_comprehensive_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive stock information including historical PE ratios"""
        try:
            # Get basic stock info
            basic_info = self.get_stock_info(ticker)
            if not basic_info:
                return None
            
            # Get historical PE ratios
            historical_pe = self.get_historical_pe_ratios(ticker)
            
            # Add historical PE data to the result
            pe_history = {}
            if historical_pe is not None and not historical_pe.empty:
                # Calculate PE statistics
                pe_ratios = historical_pe['PE_Ratio']
                
                # Remove outliers (PE > 100 or < 0)
                valid_pe_ratios = pe_ratios[(pe_ratios > 0) & (pe_ratios <= 100)]
                
                if len(valid_pe_ratios) > 0:
                    # Convert DataFrame to records with proper timestamp handling
                    historical_records = []
                    for _, row in historical_pe.tail(252).iterrows():  # Last year of data
                        historical_records.append({
                            'Date': row['Date'],  # ISO format string
                            'Close': float(row['Close']),
                            'TTM_EPS': float(row['TTM_EPS']),
                            'PE_Ratio': float(row['PE_Ratio']),
                            'timestamp': int(row['timestamp'])  # Unix timestamp
                        })
                    
                    pe_history = {
                        'historical_data': historical_records,
                        'current_pe': float(valid_pe_ratios.iloc[-1]) if len(valid_pe_ratios) > 0 else None,
                        'avg_pe_1y': float(valid_pe_ratios.tail(252).mean()) if len(valid_pe_ratios) >= 252 else float(valid_pe_ratios.mean()),
                        'avg_pe_6m': float(valid_pe_ratios.tail(126).mean()) if len(valid_pe_ratios) >= 126 else float(valid_pe_ratios.mean()),
                        'avg_pe_3m': float(valid_pe_ratios.tail(63).mean()) if len(valid_pe_ratios) >= 63 else float(valid_pe_ratios.mean()),
                        'min_pe_1y': float(valid_pe_ratios.tail(252).min()) if len(valid_pe_ratios) >= 252 else float(valid_pe_ratios.min()),
                        'max_pe_1y': float(valid_pe_ratios.tail(252).max()) if len(valid_pe_ratios) >= 252 else float(valid_pe_ratios.max()),
                        'median_pe_1y': float(valid_pe_ratios.tail(252).median()) if len(valid_pe_ratios) >= 252 else float(valid_pe_ratios.median()),
                        'pe_percentile': float((valid_pe_ratios.iloc[-1] <= valid_pe_ratios).mean() * 100) if len(valid_pe_ratios) > 1 else 50.0
                    }
            
            # Combine basic info with PE history
            comprehensive_info = {
                **basic_info,
                'pe_history': pe_history
            }
            
            return comprehensive_info
            
        except Exception as e:
            stock_logger.error(f"Error fetching comprehensive stock info for {ticker}: {e}")
            return basic_info  # Return basic info as fallback


def get_yahoo_finance_api() -> YahooFinanceAPI:
    """Get Yahoo Finance API instance"""
    return YahooFinanceAPI() 