"""
Enhanced Financial Data Service
Provides missing financial metrics using alternative data sources
"""

import os
import requests
from typing import Dict, Any, Optional
from src.utils.logger import stock_logger


class FinancialDataService:
    """
    Enhanced financial data service that uses multiple APIs to provide comprehensive financial metrics
    """
    
    def __init__(self):
        self.logger = stock_logger
        self.fmp_api_key = os.getenv('FMP_API_KEY')
        self.fmp_base_url = "https://financialmodelingprep.com/api/v3"
        
    def get_enhanced_financial_ratios(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive financial ratios using Financial Modeling Prep API
        Falls back to basic calculations if API data unavailable
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with financial ratios
        """
        ratios = {}
        
        try:
            if self.fmp_api_key:
                # Get financial ratios from FMP API
                fmp_ratios = self._get_fmp_financial_ratios(ticker)
                if fmp_ratios:
                    ratios.update(fmp_ratios)
                    self.logger.info(f"Successfully fetched FMP financial ratios for {ticker}")
                else:
                    self.logger.warning(f"No FMP financial ratios data for {ticker}")
            else:
                self.logger.info("FMP API key not configured, skipping enhanced ratio data")
                
        except Exception as e:
            self.logger.error(f"Error fetching enhanced financial ratios for {ticker}: {e}")
            
        return ratios
    
    def _get_fmp_financial_ratios(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch financial ratios from Financial Modeling Prep API
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with financial ratios or None if error
        """
        try:
            # Get TTM (Trailing Twelve Months) ratios for most current data
            url = f"{self.fmp_base_url}/ratios-ttm/{ticker}"
            params = {
                'apikey': self.fmp_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) == 0:
                self.logger.warning(f"No TTM ratios data returned for {ticker}")
                return None
                
            # Extract the most recent ratios (first item in array)
            latest_ratios = data[0] if isinstance(data, list) else data
            
            # Map FMP field names to our standard field names
            ratios = {}
            
            # Return on Equity
            if 'returnOnEquity' in latest_ratios and latest_ratios['returnOnEquity'] is not None:
                ratios['return_on_equity'] = latest_ratios['returnOnEquity']
            
            # Debt to Equity Ratio
            if 'debtEquityRatio' in latest_ratios and latest_ratios['debtEquityRatio'] is not None:
                ratios['debt_to_equity'] = latest_ratios['debtEquityRatio']
            
            # Operating Margin (as decimal)
            if 'operatingProfitMargin' in latest_ratios and latest_ratios['operatingProfitMargin'] is not None:
                ratios['operating_margin'] = latest_ratios['operatingProfitMargin']
            
            # Current Ratio
            if 'currentRatio' in latest_ratios and latest_ratios['currentRatio'] is not None:
                ratios['current_ratio'] = latest_ratios['currentRatio']
            
            # Additional useful ratios
            if 'returnOnAssets' in latest_ratios and latest_ratios['returnOnAssets'] is not None:
                ratios['return_on_assets'] = latest_ratios['returnOnAssets']
                
            if 'grossProfitMargin' in latest_ratios and latest_ratios['grossProfitMargin'] is not None:
                ratios['gross_profit_margin'] = latest_ratios['grossProfitMargin']
                
            if 'netProfitMargin' in latest_ratios and latest_ratios['netProfitMargin'] is not None:
                ratios['net_profit_margin'] = latest_ratios['netProfitMargin']
                
            if 'quickRatio' in latest_ratios and latest_ratios['quickRatio'] is not None:
                ratios['quick_ratio'] = latest_ratios['quickRatio']
                
            self.logger.debug(f"Extracted {len(ratios)} financial ratios for {ticker}")
            return ratios
            
        except requests.RequestException as e:
            self.logger.error(f"HTTP error fetching FMP ratios for {ticker}: {e}")
            return None
        except ValueError as e:
            self.logger.error(f"JSON parsing error for FMP ratios {ticker}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching FMP ratios for {ticker}: {e}")
            return None
    
    def enhance_stock_info(self, stock_info: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Enhance Yahoo Finance stock info with missing financial ratios
        
        Args:
            stock_info: Original stock info from Yahoo Finance
            ticker: Stock ticker symbol
            
        Returns:
            Enhanced stock info with additional financial ratios
        """
        enhanced_info = stock_info.copy()
        
        try:
            # Get enhanced ratios
            enhanced_ratios = self.get_enhanced_financial_ratios(ticker)
            
            # Fill in missing values from Yahoo Finance with enhanced data
            if enhanced_ratios:
                # Return on Equity
                if (not enhanced_info.get('returnOnEquity') and 
                    'return_on_equity' in enhanced_ratios):
                    enhanced_info['returnOnEquity'] = enhanced_ratios['return_on_equity']
                
                # Debt to Equity
                if (not enhanced_info.get('debtToEquity') and 
                    'debt_to_equity' in enhanced_ratios):
                    enhanced_info['debtToEquity'] = enhanced_ratios['debt_to_equity']
                
                # Operating Margins
                if (not enhanced_info.get('operatingMargins') and 
                    'operating_margin' in enhanced_ratios):
                    enhanced_info['operatingMargins'] = enhanced_ratios['operating_margin']
                
                # Current Ratio
                if (not enhanced_info.get('currentRatio') and 
                    'current_ratio' in enhanced_ratios):
                    enhanced_info['currentRatio'] = enhanced_ratios['current_ratio']
                
                # Additional ratios
                if 'return_on_assets' in enhanced_ratios:
                    enhanced_info['returnOnAssets'] = enhanced_ratios['return_on_assets']
                    
                if 'gross_profit_margin' in enhanced_ratios:
                    enhanced_info['grossProfitMargin'] = enhanced_ratios['gross_profit_margin']
                    
                if 'net_profit_margin' in enhanced_ratios:
                    enhanced_info['netProfitMargin'] = enhanced_ratios['net_profit_margin']
                    
                if 'quick_ratio' in enhanced_ratios:
                    enhanced_info['quickRatio'] = enhanced_ratios['quick_ratio']
                
                self.logger.info(f"Enhanced stock info for {ticker} with additional financial ratios")
                
        except Exception as e:
            self.logger.error(f"Error enhancing stock info for {ticker}: {e}")
            
        return enhanced_info


def get_financial_data_service() -> FinancialDataService:
    """Get financial data service instance"""
    return FinancialDataService() 