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

from src.utils.logger import stock_logger
from src.utils.config import config


class YahooFinanceAPI:
    """Yahoo Finance data API wrapper"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get basic stock information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            stock_logger.info(f"Retrieved stock info for {ticker}")

            # Normalize financial ratios to handle different formats
            normalized_info = self._normalize_financial_ratios(info)

            return {
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
                'full_time_employees': normalized_info.get('fullTimeEmployees')
            }
        except Exception as e:
            stock_logger.error(f"Error fetching stock info for {ticker}: {e}")
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
        """Get historical stock data"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                stock_logger.warning(f"No historical data found for {ticker}")
                return None
            
            # Ensure the DataFrame has the expected columns
            expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in expected_columns:
                if col not in hist.columns:
                    stock_logger.warning(f"Missing column {col} in historical data for {ticker}")
            
            stock_logger.info(f"Retrieved {len(hist)} days of historical data for {ticker}")
            return hist
            
        except Exception as e:
            stock_logger.error(f"Error fetching historical data for {ticker}: {e}")
            return None
    
    def get_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive financial data"""
        try:
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
            return financials
            
        except Exception as e:
            stock_logger.error(f"Error fetching financial data for {ticker}: {e}")
            return {}
    
    def get_analyst_recommendations(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get analyst recommendations"""
        try:
            stock = yf.Ticker(ticker)
            recommendations = stock.recommendations
            
            if recommendations is None or recommendations.empty:
                stock_logger.warning(f"No analyst recommendations found for {ticker}")
                return None
            
            stock_logger.info(f"Retrieved analyst recommendations for {ticker}")
            return recommendations
            
        except Exception as e:
            stock_logger.error(f"Error fetching analyst recommendations for {ticker}: {e}")
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
        """Get earnings calendar"""
        try:
            stock = yf.Ticker(ticker)
            calendar = stock.calendar
            
            if calendar is None or calendar.empty:
                stock_logger.warning(f"No earnings calendar found for {ticker}")
                return None
            
            stock_logger.info(f"Retrieved earnings calendar for {ticker}")
            return calendar
            
        except Exception as e:
            stock_logger.error(f"Error fetching earnings calendar for {ticker}: {e}")
            return None
    
    def search_stock_news(self, ticker: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for recent news about a stock"""
        try:
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
            return processed_news
            
        except Exception as e:
            stock_logger.error(f"Error fetching news for {ticker}: {e}")
            return []
    
    def get_real_time_quote(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote data"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get the most recent data
            hist = stock.history(period="2d", interval="1m")
            if hist.empty:
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
            stock_logger.error(f"Error fetching real-time quote for {ticker}: {e}")
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
        """Get historical PE ratios using earnings and price data"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get historical price data
            hist_prices = stock.history(period=period, interval="1d")
            if hist_prices.empty:
                stock_logger.warning(f"No historical price data found for {ticker}")
                return None
            
            # Get quarterly financials to calculate EPS
            try:
                # Use income statement instead of deprecated earnings
                quarterly_income = stock.quarterly_income_stmt
                if quarterly_income is None or quarterly_income.empty:
                    stock_logger.warning(f"No quarterly income statement found for {ticker}")
                    return None
                
                # Find net income row
                net_income_row = None
                for idx in quarterly_income.index:
                    if any(term in str(idx).lower() for term in ['net income', 'net earnings']):
                        net_income_row = idx
                        break
                
                if net_income_row is None:
                    stock_logger.warning(f"Could not find net income in income statement for {ticker}")
                    return None
                
                # Get shares outstanding from stock info
                info = stock.info
                shares_outstanding = info.get('sharesOutstanding', info.get('impliedSharesOutstanding'))
                
                if not shares_outstanding:
                    stock_logger.warning(f"Could not get shares outstanding for {ticker}")
                    return None
                
                # Calculate quarterly EPS
                quarterly_net_income = quarterly_income.loc[net_income_row]
                quarterly_eps = quarterly_net_income / shares_outstanding
                
                # Filter out invalid data
                quarterly_eps = quarterly_eps.dropna()
                if quarterly_eps.empty:
                    stock_logger.warning(f"No valid EPS data for {ticker}")
                    return None
                
            except Exception as e:
                stock_logger.warning(f"Error processing financial data for {ticker}: {e}")
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
                return None
                
        except Exception as e:
            stock_logger.error(f"Error fetching historical PE ratios for {ticker}: {e}")
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