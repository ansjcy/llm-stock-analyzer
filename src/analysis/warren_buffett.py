"""
Warren Buffett Investment Analyzer
Implements Warren Buffett's value investing principles and methodologies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import yfinance as yf

from src.utils.logger import stock_logger
from src.data.financial_data_service import get_financial_data_service
from src.utils.translations import t


class WarrenBuffettAnalyzer:
    """Analyzes stocks using Warren Buffett's investment principles"""
    
    def __init__(self, language: str = 'en'):
        self.logger = stock_logger
        self.language = language
    
    def analyze_stock(self, ticker: str, stock_info: Dict[str, Any] = None, 
                     financial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive Warren Buffett-style analysis
        
        Args:
            ticker: Stock ticker symbol
            stock_info: Basic stock information from Yahoo Finance
            financial_data: Financial statements data
            
        Returns:
            Dictionary containing analysis results and investment signal
        """
        try:
            # Get fresh data if not provided
            if not stock_info or not financial_data:
                stock = yf.Ticker(ticker)
                if not stock_info:
                    stock_info = stock.info
                if not financial_data:
                    financial_data = {
                        'income_statement': stock.financials,
                        'balance_sheet': stock.balance_sheet,
                        'cash_flow': stock.cashflow,
                        'quarterly_financials': stock.quarterly_financials,
                        'quarterly_balance_sheet': stock.quarterly_balance_sheet,
                        'quarterly_cashflow': stock.quarterly_cashflow
                    }
            
            # Enhance stock_info with missing financial ratios from alternative sources
            try:
                financial_service = get_financial_data_service()
                stock_info = financial_service.enhance_stock_info(stock_info, ticker)
                self.logger.info(f"Enhanced financial data for {ticker}")
            except Exception as e:
                self.logger.warning(f"Could not enhance financial data for {ticker}: {e}")
            
            # Perform individual analyses
            fundamental_analysis = self._analyze_fundamentals(stock_info, ticker)
            consistency_analysis = self._analyze_consistency(financial_data)
            moat_analysis = self._analyze_economic_moat(stock_info, financial_data)
            management_analysis = self._analyze_management_quality(financial_data)
            intrinsic_value_analysis = self._calculate_intrinsic_value(stock_info, financial_data)
            
            # Calculate margin of safety
            margin_of_safety = self._calculate_margin_of_safety(
                stock_info, intrinsic_value_analysis.get('intrinsic_value')
            )
            
            # Generate overall score and signal
            total_score, max_score = self._calculate_total_score(
                fundamental_analysis, consistency_analysis, moat_analysis, management_analysis
            )
            
            signal = self._generate_investment_signal(
                total_score, max_score, margin_of_safety, intrinsic_value_analysis
            )
            
            # Compile results
            analysis_results = {
                'ticker': ticker,
                'analysis_date': datetime.now().isoformat(),
                'overall_signal': signal['signal'],
                'confidence': signal['confidence'],
                'total_score': total_score,
                'max_possible_score': max_score,
                'score_percentage': (total_score / max_score * 100) if max_score > 0 else 0,
                'margin_of_safety': margin_of_safety,
                'fundamental_analysis': fundamental_analysis,
                'consistency_analysis': consistency_analysis,
                'moat_analysis': moat_analysis,
                'management_analysis': management_analysis,
                'intrinsic_value_analysis': intrinsic_value_analysis,
                'investment_reasoning': signal['reasoning'],
                'buffett_principles': self._evaluate_buffett_principles(
                    fundamental_analysis, consistency_analysis, moat_analysis, 
                    management_analysis, margin_of_safety
                )
            }
            
            self.logger.info(f"Warren Buffett analysis completed for {ticker}")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in Warren Buffett analysis for {ticker}: {e}")
            return {
                'ticker': ticker,
                'error': str(e),
                'overall_signal': 'neutral',
                'confidence': 0.0
            }
    
    def _analyze_fundamentals(self, stock_info: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """
        Analyze company fundamentals based on Buffett's criteria
        Focus on: ROE, debt levels, margins, liquidity
        Now more nuanced for growth companies that reinvest heavily
        """
        score = 0
        max_score = 8
        details = []
        metrics = {}
        
        try:
            # Return on Equity (ROE) - Buffett likes > 15%
            roe = stock_info.get('return_on_equity')
            if roe is not None:
                # Enhanced financial service provides ROE as ratio (e.g., 1.38015 = 138.015%)
                # When ROE > 1, it's already in decimal form representing the percentage
                # (e.g., 1.38015 means 138.015% ROE)
                if roe > 1:
                    roe_decimal = roe  # Already as decimal ratio (1.38015 = 138.015%)
                    roe_percentage = roe  # For display
                else:
                    roe_decimal = roe  # Already as decimal
                    roe_percentage = roe
                    
                metrics['return_on_equity'] = roe_decimal
                
                if roe_decimal > 0.20:  # Exceptional ROE (>20%)
                    score += 2
                    if self.language == 'zh':
                        details.append(f"卓越的ROE {roe_percentage:.1%} (>20%目标)")
                    else:
                        details.append(f"Exceptional ROE of {roe_percentage:.1%} (>20% target)")
                elif roe_decimal > 0.15:  # 15% threshold
                    score += 2
                    if self.language == 'zh':
                        details.append(f"优秀的ROE {roe_percentage:.1%} (>15%目标)")
                    else:
                        details.append(f"Excellent ROE of {roe_percentage:.1%} (>15% target)")
                elif roe_decimal > 0.10:  # 10% still decent
                    score += 1
                    if self.language == 'zh':
                        details.append(f"良好的ROE {roe_percentage:.1%}")
                    else:
                        details.append(f"Good ROE of {roe_percentage:.1%}")
                else:
                    if self.language == 'zh':
                        details.append(f"较弱的ROE {roe_percentage:.1%} (<10%)")
                    else:
                        details.append(f"Weak ROE of {roe_percentage:.1%} (<10%)")
            else:
                if self.language == 'zh':
                    details.append("任何来源均无ROE数据")
                else:
                    details.append("ROE data not available from any source")
            
            # Debt to Equity - More nuanced for growth companies
            debt_to_equity = stock_info.get('debt_to_equity')
            if debt_to_equity is not None:
                # Enhanced financial service provides debt-to-equity as percentage (e.g., 146.994 = 146.994%)
                # Convert to ratio format for consistent analysis
                if debt_to_equity > 10:
                    debt_ratio = debt_to_equity / 100  # Convert percentage to ratio
                else:
                    debt_ratio = debt_to_equity  # Already as ratio
                
                metrics['debt_to_equity'] = debt_ratio
                
                # More lenient thresholds for large-cap growth companies
                market_cap = stock_info.get('market_cap', 0)
                if market_cap > 500e9:  # Large-cap companies (>$500B) get more lenient debt thresholds
                    if debt_ratio < 0.4:  # Very conservative (< 40%)
                        score += 2
                        if self.language == 'zh':
                            details.append(f"大盘股保守的债务水平 ({debt_ratio:.2f})")
                        else:
                            details.append(f"Conservative debt levels for large-cap ({debt_ratio:.2f})")
                    elif debt_ratio < 0.7:  # Reasonable for large growth companies (< 70%)
                        score += 1
                        if self.language == 'zh':
                            details.append(f"大盘成长公司适度的债务水平 ({debt_ratio:.2f})")
                        else:
                            details.append(f"Moderate debt levels for large-cap growth company ({debt_ratio:.2f})")
                    else:
                        if self.language == 'zh':
                            details.append(f"高债务权益比 ({debt_ratio:.2f})")
                        else:
                            details.append(f"High debt to equity ratio ({debt_ratio:.2f})")
                else:
                    # Original thresholds for smaller companies
                    if debt_ratio < 0.3:  # Very conservative (< 30%)
                        score += 2
                        if self.language == 'zh':
                            details.append(f"非常保守的债务水平 ({debt_ratio:.2f})")
                        else:
                            details.append(f"Very conservative debt levels ({debt_ratio:.2f})")
                    elif debt_ratio < 0.5:  # Still good (< 50%)
                        score += 1
                        if self.language == 'zh':
                            details.append(f"适度的债务水平 ({debt_ratio:.2f})")
                        else:
                            details.append(f"Moderate debt levels ({debt_ratio:.2f})")
                    else:
                        if self.language == 'zh':
                            details.append(f"高债务权益比 ({debt_ratio:.2f})")
                        else:
                            details.append(f"High debt to equity ratio ({debt_ratio:.2f})")
            else:
                if self.language == 'zh':
                    details.append("任何来源均无债务权益比数据")
                else:
                    details.append("Debt to equity data not available from any source")
            
            # Operating Margin - More nuanced for different business models
            operating_margin = stock_info.get('operating_margins')
            if operating_margin is not None:
                # Operating margin is typically as decimal (0.31 = 31%)
                metrics['operating_margin'] = operating_margin
                
                # Adjust thresholds based on company size and business model
                # Tech/growth companies that reinvest heavily may have lower margins but still be high quality
                roe_bonus = roe_decimal > 0.20 if roe is not None else False
                
                if operating_margin > 0.20:  # 20%+ is excellent
                    score += 2
                    if self.language == 'zh':
                        details.append(f"优秀的营业利润率 ({operating_margin:.1%})")
                    else:
                        details.append(f"Excellent operating margins ({operating_margin:.1%})")
                elif operating_margin > 0.15:  # 15%+ is good
                    score += 2
                    if self.language == 'zh':
                        details.append(f"强劲的营业利润率 ({operating_margin:.1%})")
                    else:
                        details.append(f"Strong operating margins ({operating_margin:.1%})")
                elif operating_margin > 0.10:  # 10%+ is decent, especially with high ROE
                    if roe_bonus:
                        score += 2  # High ROE compensates for moderate margins
                        if self.language == 'zh':
                            details.append(f"适度的营业利润率 ({operating_margin:.1%}) 但优秀的ROE表明高效的再投资")
                        else:
                            details.append(f"Decent operating margins ({operating_margin:.1%}) but excellent ROE indicates efficient reinvestment")
                    else:
                        score += 1
                        if self.language == 'zh':
                            details.append(f"适度的营业利润率 ({operating_margin:.1%})")
                        else:
                            details.append(f"Moderate operating margins ({operating_margin:.1%})")
                elif operating_margin > 0.05:  # 5%+ with exceptional ROE can still be good
                    if roe_bonus:
                        score += 1  # High ROE compensates
                        if self.language == 'zh':
                            details.append(f"较低的营业利润率 ({operating_margin:.1%})")
                        else:
                            details.append(f"Lower operating margins ({operating_margin:.1%})")
                    else:
                        if self.language == 'zh':
                            details.append(f"较弱的营业利润率 ({operating_margin:.1%})")
                        else:
                            details.append(f"Weak operating margins ({operating_margin:.1%})")
                else:
                    if self.language == 'zh':
                        details.append(f"非常弱的营业利润率 ({operating_margin:.1%})")
                    else:
                        details.append(f"Very weak operating margins ({operating_margin:.1%})")
            else:
                if self.language == 'zh':
                    details.append("任何来源均无营业利润率数据")
                else:
                    details.append("Operating margin data not available from any source")
            
            # Current Ratio - More context-aware
            current_ratio = stock_info.get('current_ratio')
            if current_ratio is not None:
                metrics['current_ratio'] = current_ratio
                
                # Large companies with strong cash flow can operate with lower current ratios
                market_cap = stock_info.get('market_cap', 0)
                
                if current_ratio > 2.0:  # Very strong liquidity
                    score += 2
                    if self.language == 'zh':
                        details.append(f"优秀的流动性 (流动比率: {current_ratio:.1f})")
                    else:
                        details.append(f"Excellent liquidity (current ratio: {current_ratio:.1f})")
                elif current_ratio > 1.5:  # Good liquidity
                    score += 2
                    if self.language == 'zh':
                        details.append(f"强劲的流动性 (流动比率: {current_ratio:.1f})")
                    else:
                        details.append(f"Strong liquidity (current ratio: {current_ratio:.1f})")
                elif current_ratio > 1.0:  # Adequate for large companies with strong FCF
                    if market_cap > 500e9:  # Large-cap companies
                        score += 1
                        if self.language == 'zh':
                            details.append(f"大盘公司充足的流动性 (流动比率: {current_ratio:.1f})")
                        else:
                            details.append(f"Adequate liquidity for large-cap company (current ratio: {current_ratio:.1f})")
                    else:
                        if self.language == 'zh':
                            details.append(f"适度的流动性 (流动比率: {current_ratio:.1f})")
                        else:
                            details.append(f"Moderate liquidity (current ratio: {current_ratio:.1f})")
                else:
                    if self.language == 'zh':
                        details.append(f"较弱的流动性 (流动比率: {current_ratio:.1f})")
                    else:
                        details.append(f"Weak liquidity (current ratio: {current_ratio:.1f})")
            else:
                if self.language == 'zh':
                    details.append("任何来源均无流动比率数据")
                else:
                    details.append("Current ratio data not available from any source")
                
            # Log the availability of financial metrics for debugging
            available_metrics = []
            if roe is not None:
                available_metrics.append('ROE')
            if debt_to_equity is not None:
                available_metrics.append('Debt-to-Equity')
            if operating_margin is not None:
                available_metrics.append('Operating Margin')
            if current_ratio is not None:
                available_metrics.append('Current Ratio')
            
            if available_metrics:
                self.logger.info(f"Available financial metrics for {ticker}: {', '.join(available_metrics)}")
            else:
                self.logger.warning(f"No key financial metrics available for {ticker}")
                
        except Exception as e:
            self.logger.error(f"Error in fundamental analysis for {ticker}: {e}")
            details.append(f"Error in analysis: {e}")
        
        return {
            'score': score,
            'max_score': max_score,
            'score_percentage': (score / max_score * 100) if max_score > 0 else 0,
            'details': details,
            'metrics': metrics,
            'category': 'Financial Strength'
        }
    
    def _analyze_consistency(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze earnings consistency and growth trends
        Buffett loves predictable, growing earnings
        """
        score = 0
        max_score = 4
        details = []
        
        try:
            # Try to get earnings data from income statement
            income_statement = financial_data.get('income_statement')
            quarterly_financials = financial_data.get('quarterly_financials')
            
            earnings_data = None
            period_type = None
            
            # Try annual data first, then quarterly
            if income_statement is not None and not income_statement.empty:
                # Look for net income row
                for index in income_statement.index:
                    if 'net income' in str(index).lower() or 'net earnings' in str(index).lower():
                        earnings_data = income_statement.loc[index].dropna()
                        period_type = 'Annual'
                        break
            
            if earnings_data is None and quarterly_financials is not None and not quarterly_financials.empty:
                for index in quarterly_financials.index:
                    if 'net income' in str(index).lower() or 'net earnings' in str(index).lower():
                        earnings_data = quarterly_financials.loc[index].dropna()
                        period_type = 'Quarterly'
                        break
            
            if earnings_data is not None and len(earnings_data) >= 3:
                # Sort by date (most recent first)
                earnings_data = earnings_data.sort_index(ascending=False)
                earnings_values = earnings_data.values
                
                # Check for positive earnings trend
                positive_earnings = sum(1 for x in earnings_values if x > 0)
                if positive_earnings >= len(earnings_values) * 0.8:  # 80% positive
                    score += 1
                    if self.language == 'zh':
                        details.append(f"在{len(earnings_values)}个{period_type.lower()}期间内持续正收益")
                    else:
                        details.append(f"Consistent positive earnings over {len(earnings_values)} {period_type.lower()} periods")
                
                # Check for growth trend (comparing recent periods)
                if len(earnings_values) >= 4:
                    recent_avg = np.mean(earnings_values[:2])  # Most recent 2 periods
                    older_avg = np.mean(earnings_values[-2:])  # Oldest 2 periods
                    
                    if recent_avg > older_avg:
                        growth_rate = (recent_avg - older_avg) / abs(older_avg) if older_avg != 0 else 0
                        if growth_rate > 0.10:  # 10%+ growth
                            score += 2
                            if self.language == 'zh':
                                details.append(f"强劲的收益增长趋势 ({growth_rate:.1%})")
                            else:
                                details.append(f"Strong earnings growth trend ({growth_rate:.1%})")
                        elif growth_rate > 0.05:  # 5%+ growth
                            score += 1
                            if self.language == 'zh':
                                details.append(f"温和的收益增长趋势 ({growth_rate:.1%})")
                            else:
                                details.append(f"Moderate earnings growth trend ({growth_rate:.1%})")
                        else:
                            if self.language == 'zh':
                                details.append(f"较弱的收益增长趋势 ({growth_rate:.1%})")
                            else:
                                details.append(f"Weak earnings growth trend ({growth_rate:.1%})")
                    else:
                        if self.language == 'zh':
                            details.append("检测到收益下降趋势")
                        else:
                            details.append("Declining earnings trend detected")
                
                # Check for earnings stability (low volatility)
                if len(earnings_values) >= 3:
                    earnings_cv = np.std(earnings_values) / np.mean(earnings_values) if np.mean(earnings_values) != 0 else float('inf')
                    if earnings_cv < 0.3:  # Low volatility
                        score += 1
                        if self.language == 'zh':
                            details.append("稳定、可预测的收益模式")
                        else:
                            details.append("Stable, predictable earnings pattern")
                    else:
                        if self.language == 'zh':
                            details.append("检测到高收益波动性")
                        else:
                            details.append("High earnings volatility detected")
                        
            else:
                if self.language == 'zh':
                    details.append("趋势分析的收益数据不足")
                else:
                    details.append("Insufficient earnings data for trend analysis")
                
        except Exception as e:
            self.logger.error(f"Error in consistency analysis: {e}")
            details.append(f"Error analyzing earnings consistency: {e}")
        
        return {
            'score': score,
            'max_score': max_score,
            'score_percentage': (score / max_score * 100) if max_score > 0 else 0,
            'details': details,
            'category': 'Earnings Consistency'
        }
    
    def _analyze_economic_moat(self, stock_info: Dict[str, Any], 
                              financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the company's economic moat (competitive advantage)
        Look for sustained high returns and stable margins
        """
        score = 0
        max_score = 6
        details = []
        
        try:
            # Check ROE stability over time (using current and historical data)
            roe = stock_info.get('return_on_equity')
            if roe is not None:
                # Apply same ROE interpretation as in fundamental analysis
                if roe > 1:
                    roe_decimal = roe  # Already as decimal ratio (1.38015 = 138.015%)
                else:
                    roe_decimal = roe  # Already as decimal
                    
                if roe_decimal > 0.15:
                    score += 1
                    if self.language == 'zh':
                        details.append(f"当前ROE高于15% ({roe_decimal:.1%}) 表明具有竞争优势")
                    else:
                        details.append(f"Current ROE above 15% ({roe_decimal:.1%}) suggests competitive advantage")
            
            # Check margin stability
            operating_margin = stock_info.get('operating_margins')
            profit_margin = stock_info.get('profit_margins')
            gross_margin = stock_info.get('gross_margins')
            
            high_margin_count = 0
            if operating_margin and operating_margin > 0.15:
                high_margin_count += 1
            if profit_margin and profit_margin > 0.10:
                high_margin_count += 1
            if gross_margin and gross_margin > 0.30:
                high_margin_count += 1
            
            if high_margin_count >= 2:
                score += 2
                if self.language == 'zh':
                    details.append("多个类别的高利润率表明强大的定价能力")
                else:
                    details.append("High margins across multiple categories indicate strong pricing power")
            elif high_margin_count == 1:
                score += 1
                if self.language == 'zh':
                    details.append("通过利润率显示出一定的定价能力")
                else:
                    details.append("Some evidence of pricing power through margins")
            
            # Check for brand value indicators (approximated through ratios)
            price_to_book = stock_info.get('price_to_book')
            if price_to_book and price_to_book > 3:
                score += 1
                if self.language == 'zh':
                    details.append(f"高市净率 ({price_to_book:.1f}) 可能表明无形资产/品牌价值")
                else:
                    details.append(f"High price-to-book ratio ({price_to_book:.1f}) may indicate intangible assets/brand value")
            
            # Market position (approximated through market cap relative to revenue)
            market_cap = stock_info.get('market_cap')
            revenue = stock_info.get('total_revenue')
            if market_cap and revenue and market_cap > 0 and revenue > 0:
                price_to_sales = market_cap / revenue
                if price_to_sales > 5:  # High P/S might indicate strong market position
                    score += 1
                    if self.language == 'zh':
                        details.append("相对于销售额的高市场估值表明强势市场地位")
                    else:
                        details.append("High market valuation relative to sales suggests strong market position")
            
            # Debt levels as moat indicator (low debt = financial flexibility)
            debt_to_equity = stock_info.get('debt_to_equity')
            if debt_to_equity is not None:
                # Apply same debt interpretation as in fundamental analysis
                if debt_to_equity > 10:
                    debt_ratio = debt_to_equity / 100  # Convert percentage to ratio
                else:
                    debt_ratio = debt_to_equity  # Already as ratio
                    
                if debt_ratio < 0.2:  # Very low debt
                    score += 1
                    if self.language == 'zh':
                        details.append("极低的债务提供财务灵活性（护城河指标）")
                    else:
                        details.append("Very low debt provides financial flexibility (moat indicator)")
            
            if score == 0:
                if self.language == 'zh':
                    details.append("可持续竞争优势的证据有限")
                else:
                    details.append("Limited evidence of sustainable competitive advantages")
                
        except Exception as e:
            self.logger.error(f"Error in moat analysis: {e}")
            details.append(f"Error analyzing economic moat: {e}")
        
        return {
            'score': score,
            'max_score': max_score,
            'score_percentage': (score / max_score * 100) if max_score > 0 else 0,
            'details': details,
            'category': 'Economic Moat'
        }
    
    def _analyze_management_quality(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze management quality through capital allocation decisions
        Focus on share buybacks, dividends, and capital efficiency
        Now includes recognition of value-creating reinvestment strategies
        """
        score = 0
        max_score = 4
        details = []
        
        try:
            # Try to analyze cash flow statement for share buybacks and dividends
            cash_flow = financial_data.get('cash_flow')
            
            if cash_flow is not None and not cash_flow.empty:
                # Look for share repurchases (various possible names)
                repurchase_indicators = [
                    'repurchase of capital stock',
                    'purchase of treasury stock',
                    'common stock repurchased',
                    'stock repurchases',
                    'repurchase of common stock'
                ]
                
                buyback_found = False
                for indicator in repurchase_indicators:
                    for index in cash_flow.index:
                        if indicator.lower() in str(index).lower():
                            recent_buybacks = cash_flow.loc[index].dropna()
                            if len(recent_buybacks) > 0:
                                # Negative values indicate cash outflow for buybacks
                                if any(x < 0 for x in recent_buybacks.values[:2]):  # Recent periods
                                    score += 1
                                    if self.language == 'zh':
                                        details.append("公司积极回购股票（对股东友好）")
                                    else:
                                        details.append("Company actively repurchasing shares (shareholder-friendly)")
                                    buyback_found = True
                                    break
                        if buyback_found:
                            break
                    if buyback_found:
                        break
                
                # Look for dividend payments
                dividend_indicators = [
                    'cash dividends paid',
                    'dividends paid',
                    'cash dividend',
                    'dividends and other cash distributions'
                ]
                
                dividend_found = False
                for indicator in dividend_indicators:
                    for index in cash_flow.index:
                        if indicator.lower() in str(index).lower():
                            recent_dividends = cash_flow.loc[index].dropna()
                            if len(recent_dividends) > 0:
                                # Negative values indicate cash outflow for dividends
                                if any(x < 0 for x in recent_dividends.values[:2]):  # Recent periods
                                    score += 1
                                    if self.language == 'zh':
                                        details.append("持续分红体现对股东的重视")
                                    else:
                                        details.append("Consistent dividend payments demonstrate shareholder focus")
                                    dividend_found = True
                                    break
                        if dividend_found:
                            break
                    if dividend_found:
                        break
                
                # Enhanced capital efficiency analysis
                # Look for reasonable capex levels relative to depreciation AND revenue growth
                capex_indicators = ['capital expenditure', 'capital expenditures', 'purchases of property']
                depreciation_indicators = ['depreciation', 'depreciation and amortization']
                operating_cf_indicators = ['operating cash flow', 'cash flow from operating activities']
                
                capex_data = None
                depreciation_data = None
                operating_cf_data = None
                
                for indicator in capex_indicators:
                    for index in cash_flow.index:
                        if indicator.lower() in str(index).lower():
                            capex_data = cash_flow.loc[index].dropna()
                            break
                    if capex_data is not None:
                        break
                
                for indicator in depreciation_indicators:
                    for index in cash_flow.index:
                        if indicator.lower() in str(index).lower():
                            depreciation_data = cash_flow.loc[index].dropna()
                            break
                    if depreciation_data is not None:
                        break
                
                for indicator in operating_cf_indicators:
                    for index in cash_flow.index:
                        if indicator.lower() in str(index).lower():
                            operating_cf_data = cash_flow.loc[index].dropna()
                            break
                    if operating_cf_data is not None:
                        break
                
                # Improved capital allocation assessment
                if capex_data is not None and len(capex_data) > 0:
                    recent_capex = abs(capex_data.iloc[0]) if len(capex_data) > 0 else 0
                    
                    # Check for growth-oriented capital allocation
                    if operating_cf_data is not None and len(operating_cf_data) > 0:
                        recent_operating_cf = operating_cf_data.iloc[0]
                        
                        if recent_operating_cf > 0:
                            capex_to_ocf_ratio = recent_capex / recent_operating_cf
                            
                            # Different thresholds for growth vs mature companies
                            if capex_to_ocf_ratio < 0.3:  # Low capex relative to OCF
                                if depreciation_data is not None and len(depreciation_data) > 0:
                                    recent_depreciation = abs(depreciation_data.iloc[0])
                                    if recent_depreciation > 0:
                                        capex_ratio = recent_capex / recent_depreciation
                                        if capex_ratio >= 1.0:  # Maintaining/growing assets
                                            score += 1
                                            if self.language == 'zh':
                                                details.append("平衡的资本配置 - 高效维护资产基础")
                                            else:
                                                details.append("Balanced capital allocation - maintaining asset base efficiently")
                                        else:
                                            if self.language == 'zh':
                                                details.append("保守的资本支出（可能表明投资不足）")
                                            else:
                                                details.append("Conservative capital expenditure (may indicate underinvestment)")
                                else:
                                    score += 1
                                    if self.language == 'zh':
                                        details.append("保守的资本配置与强劲的现金生成")
                                    else:
                                        details.append("Conservative capital allocation with strong cash generation")
                            elif capex_to_ocf_ratio < 0.6:  # Moderate reinvestment
                                score += 1
                                if self.language == 'zh':
                                    details.append("适度的再投资策略 - 在保持盈利的同时增长业务")
                                else:
                                    details.append("Moderate reinvestment strategy - growing business while maintaining profitability")
                            elif capex_to_ocf_ratio < 0.8:  # High reinvestment but reasonable
                                score += 1
                                if self.language == 'zh':
                                    details.append("高再投资策略 - 优先考虑增长（适合成长型公司）")
                                else:
                                    details.append("High reinvestment strategy - prioritizing growth (appropriate for growth companies)")
                            else:
                                if self.language == 'zh':
                                    details.append("相对于经营现金流的资本支出非常高")
                                else:
                                    details.append("Very high capital expenditure relative to operating cash flow")
                
                # Recognize value creation through reinvestment (especially for growth companies)
                # If a company has high capex but also strong revenue/earnings growth, this can be positive
                if not buyback_found and not dividend_found:
                    # Check if the company is creating value through other means
                    if operating_cf_data is not None and len(operating_cf_data) >= 2:
                        # Look for growing operating cash flow as sign of effective reinvestment
                        recent_ocf = operating_cf_data.iloc[0]
                        prior_ocf = operating_cf_data.iloc[1]
                        
                        if recent_ocf > prior_ocf and recent_ocf > 0 and prior_ocf > 0:
                            ocf_growth = (recent_ocf - prior_ocf) / prior_ocf
                            if ocf_growth > 0.10:  # 10%+ OCF growth
                                score += 1
                                if self.language == 'zh':
                                    details.append("强劲的经营现金流增长表明有效的资本配置")
                                else:
                                    details.append("Strong operating cash flow growth indicates effective capital allocation")
                            else:
                                if self.language == 'zh':
                                    details.append("股东导向的资本配置证据有限")
                                else:
                                    details.append("Limited evidence of shareholder-focused capital allocation")
                        else:
                            if self.language == 'zh':
                                details.append("经营现金流下降引发资本配置担忧")
                            else:
                                details.append("Declining operating cash flow raises capital allocation concerns")
                    else:
                        if self.language == 'zh':
                            details.append("股东导向的资本配置证据有限")
                        else:
                            details.append("Limited evidence of shareholder-focused capital allocation")
                
                # Additional point for companies that generate strong free cash flow
                # This recognizes companies that could return cash to shareholders but choose to reinvest
                if operating_cf_data is not None and capex_data is not None and len(operating_cf_data) > 0 and len(capex_data) > 0:
                    recent_operating_cf = operating_cf_data.iloc[0] if operating_cf_data.iloc[0] > 0 else 0
                    recent_capex = abs(capex_data.iloc[0])
                    free_cash_flow = recent_operating_cf - recent_capex
                    
                    if free_cash_flow > recent_operating_cf * 0.1:  # Positive FCF > 10% of OCF
                        score += 1
                        if self.language == 'zh':
                            details.append("强劲的自由现金流生成提供财务灵活性")
                        else:
                            details.append("Strong free cash flow generation provides financial flexibility")
                
            else:
                if self.language == 'zh':
                    details.append("现金流数据不可用于管理分析")
                else:
                    details.append("Cash flow data not available for management analysis")
                
        except Exception as e:
            self.logger.error(f"Error in management analysis: {e}")
            details.append(f"Error analyzing management quality: {e}")
        
        return {
            'score': score,
            'max_score': max_score,
            'score_percentage': (score / max_score * 100) if max_score > 0 else 0,
            'details': details,
            'category': 'Management Quality'
        }
    
    def _calculate_intrinsic_value(self, stock_info: Dict[str, Any], 
                                  financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate intrinsic value using improved DCF approach
        Tries to use actual free cash flow when available, falls back to estimated owner earnings
        """
        try:
            # Get basic financial metrics
            market_cap = stock_info.get('market_cap')
            shares_outstanding = stock_info.get('shares_outstanding')
            total_revenue = stock_info.get('total_revenue')
            
            # Try to get actual free cash flow from cash flow statement
            owner_earnings = None
            calculation_method = "Estimated owner earnings"
            
            # First, try to calculate free cash flow from actual data
            cash_flow = financial_data.get('cash_flow')
            if cash_flow is not None and not cash_flow.empty:
                operating_cf = None
                capex = None
                
                # Look for operating cash flow
                for index in cash_flow.index:
                    if 'operating cash flow' in str(index).lower() or 'cash flow from operating activities' in str(index).lower():
                        operating_cf = cash_flow.loc[index].dropna()
                        break
                
                # Look for capital expenditures
                for index in cash_flow.index:
                    if 'capital expenditure' in str(index).lower() or 'purchases of property' in str(index).lower():
                        capex = cash_flow.loc[index].dropna()
                        break
                
                # Calculate free cash flow if both are available
                if operating_cf is not None and capex is not None and len(operating_cf) > 0 and len(capex) > 0:
                    # Get most recent year's free cash flow
                    recent_operating_cf = operating_cf.iloc[0]  # Most recent
                    recent_capex = capex.iloc[0]  # Most recent (typically negative)
                    free_cash_flow = recent_operating_cf + recent_capex  # capex is negative
                    
                    if free_cash_flow > 0:
                        owner_earnings = free_cash_flow
                        calculation_method = "Actual free cash flow (Operating CF - CapEx)"
            
            # Fall back to estimated owner earnings if FCF not available
            if owner_earnings is None:
                profit_margin = stock_info.get('profit_margins', 0.05)  # Default 5% if not available
                estimated_earnings = total_revenue * profit_margin
                
                # Use 90% of net income as owner earnings estimate (improved from 80%)
                # This accounts for the fact that many profitable companies have good FCF conversion
                owner_earnings = estimated_earnings * 0.90
                calculation_method = "Estimated owner earnings (90% of net income)"
            
            # Dynamic DCF assumptions based on company characteristics
            # More realistic assumptions for profitable companies
            
            # Determine growth rate based on company size and profitability
            if market_cap and market_cap > 100e9:  # Large cap (>$100B)
                growth_rate = 0.07  # 7% for large cap
            elif market_cap and market_cap > 10e9:  # Mid cap ($10B-$100B)
                growth_rate = 0.09  # 9% for mid cap
            else:
                growth_rate = 0.05  # 5% for small cap (conservative)
            
            # Adjust growth rate for high profitability
            profit_margin = stock_info.get('profit_margins', 0)
            if profit_margin > 0.15:  # High margin companies (>15%)
                growth_rate += 0.02  # Add 2% for high margins
            
            # Determine discount rate (cost of equity)
            discount_rate = 0.09  # Base 9%
            beta = stock_info.get('beta')
            if beta and beta > 1.2:
                discount_rate += 0.01  # Add 1% for high beta
            elif beta and beta < 0.8:
                discount_rate -= 0.01  # Subtract 1% for low beta
            
            # Terminal multiple based on quality metrics
            terminal_multiple = 15  # Base multiple
            
            # Adjust for quality indicators
            roe = stock_info.get('return_on_equity')
            if roe and roe > 0.15:  # High ROE
                terminal_multiple += 3
            
            operating_margin = stock_info.get('operating_margins')
            if operating_margin and operating_margin > 0.20:  # High operating margins
                terminal_multiple += 2
            
            # Cap terminal multiple at reasonable levels
            terminal_multiple = min(terminal_multiple, 22)
            
            projection_years = 10
            
            intrinsic_value = None
            per_share_value = None
            
            if owner_earnings and owner_earnings > 0 and shares_outstanding and shares_outstanding > 0:
                # DCF calculation
                future_value = 0
                for year in range(1, projection_years + 1):
                    future_earnings = owner_earnings * (1 + growth_rate) ** year
                    present_value = future_earnings / (1 + discount_rate) ** year
                    future_value += present_value
                
                # Terminal value
                terminal_value = (owner_earnings * (1 + growth_rate) ** projection_years * terminal_multiple) / ((1 + discount_rate) ** projection_years)
                
                intrinsic_value = future_value + terminal_value
                per_share_value = intrinsic_value / shares_outstanding if shares_outstanding > 0 else None
            
            return {
                'intrinsic_value': intrinsic_value,
                'per_share_value': per_share_value,
                'owner_earnings': owner_earnings,
                'assumptions': {
                    'growth_rate': growth_rate,
                    'discount_rate': discount_rate,
                    'terminal_multiple': terminal_multiple,
                    'projection_years': projection_years
                },
                'method': f'Improved DCF with {calculation_method.lower()}',
                'calculation_details': {
                    'calculation_method': calculation_method,
                    'market_cap_category': 'Large Cap' if market_cap and market_cap > 100e9 else 'Mid Cap' if market_cap and market_cap > 10e9 else 'Small Cap',
                    'quality_adjustments': {
                        'high_profit_margin': profit_margin > 0.15 if profit_margin else False,
                        'high_roe': roe > 0.15 if roe else False,
                        'high_operating_margin': operating_margin > 0.20 if operating_margin else False
                    }
                },
                'limitations': [
                    'DCF models are sensitive to assumptions',
                    'Terminal value represents significant portion of total value',
                    'Growth and multiple assumptions may not reflect future reality'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating intrinsic value: {e}")
            return {
                'intrinsic_value': None,
                'per_share_value': None,
                'error': str(e)
            }
    
    def _calculate_margin_of_safety(self, stock_info: Dict[str, Any], 
                                   intrinsic_value: Optional[float]) -> Optional[float]:
        """
        Calculate margin of safety: (Intrinsic Value - Current Price) / Current Price
        """
        try:
            current_price = stock_info.get('current_price') or stock_info.get('regular_market_price')
            shares_outstanding = stock_info.get('shares_outstanding')
            
            if intrinsic_value and current_price and shares_outstanding:
                intrinsic_per_share = intrinsic_value / shares_outstanding
                margin_of_safety = (intrinsic_per_share - current_price) / current_price
                return margin_of_safety
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating margin of safety: {e}")
            return None
    
    def _calculate_total_score(self, fundamental_analysis: Dict[str, Any],
                              consistency_analysis: Dict[str, Any],
                              moat_analysis: Dict[str, Any],
                              management_analysis: Dict[str, Any]) -> Tuple[float, float]:
        """Calculate total score from all analyses"""
        total_score = (
            fundamental_analysis.get('score', 0) +
            consistency_analysis.get('score', 0) +
            moat_analysis.get('score', 0) +
            management_analysis.get('score', 0)
        )
        
        max_score = (
            fundamental_analysis.get('max_score', 0) +
            consistency_analysis.get('max_score', 0) +
            moat_analysis.get('max_score', 0) +
            management_analysis.get('max_score', 0)
        )
        
        return total_score, max_score
    
    def _generate_investment_signal(self, total_score: float, max_score: float,
                                   margin_of_safety: Optional[float],
                                   intrinsic_value_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate investment signal based on Buffett's criteria
        """
        score_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Base confidence on score
        confidence = min(score_percentage, 95)  # Cap at 95%
        
        reasoning_parts = []
        
        # Determine signal based on score and margin of safety
        if score_percentage >= 75:  # Strong fundamentals
            if margin_of_safety is not None and margin_of_safety >= 0.25:  # 25%+ margin of safety
                signal = "bullish"
                confidence = min(confidence + 10, 95)
                if self.language == 'zh':
                    reasoning_parts.append("强劲的基本面和优秀的安全边际")
                else:
                    reasoning_parts.append("Strong fundamentals with excellent margin of safety")
            elif margin_of_safety is not None and margin_of_safety >= 0.10:  # 10%+ margin
                signal = "bullish"
                if self.language == 'zh':
                    reasoning_parts.append("强劲的基本面和充足的安全边际")
                else:
                    reasoning_parts.append("Strong fundamentals with adequate margin of safety")
            elif margin_of_safety is not None and margin_of_safety < -0.20:  # Overvalued by 20%+
                signal = "neutral"
                confidence *= 0.7  # Reduce confidence
                if self.language == 'zh':
                    reasoning_parts.append("基本面强劲但股票似乎被高估")
                else:
                    reasoning_parts.append("Strong fundamentals but stock appears overvalued")
            else:
                signal = "bullish"
                if self.language == 'zh':
                    reasoning_parts.append("强劲的基本面证明投资合理")
                else:
                    reasoning_parts.append("Strong fundamentals justify investment")
                
        elif score_percentage >= 50:  # Decent fundamentals
            if margin_of_safety is not None and margin_of_safety >= 0.30:  # Need higher margin for weaker fundamentals
                signal = "bullish"
                if self.language == 'zh':
                    reasoning_parts.append("良好的基本面和强劲的安全边际")
                else:
                    reasoning_parts.append("Decent fundamentals with strong margin of safety")
            elif margin_of_safety is not None and margin_of_safety < -0.15:  # Overvalued
                signal = "bearish"
                if self.language == 'zh':
                    reasoning_parts.append("基本面疲弱和高估担忧")
                else:
                    reasoning_parts.append("Weak fundamentals and overvaluation concerns")
            else:
                signal = "neutral"
                if self.language == 'zh':
                    reasoning_parts.append("混合的基本面需要仔细考虑")
                else:
                    reasoning_parts.append("Mixed fundamentals require careful consideration")
                
        else:  # Weak fundamentals
            if margin_of_safety is not None and margin_of_safety < -0.10:  # Any overvaluation is bad
                signal = "bearish"
                if self.language == 'zh':
                    reasoning_parts.append("基本面疲弱加上高估")
                else:
                    reasoning_parts.append("Weak fundamentals combined with overvaluation")
            else:
                signal = "bearish"
                if self.language == 'zh':
                    reasoning_parts.append("基本面疲弱不符合巴菲特的投资标准")
                else:
                    reasoning_parts.append("Weak fundamentals don't meet Buffett's investment criteria")
        
        # Add specific reasoning based on analysis components
        if margin_of_safety is not None:
            if self.language == 'zh':
                reasoning_parts.append(f"安全边际: {margin_of_safety:.1%}")
            else:
                reasoning_parts.append(f"Margin of safety: {margin_of_safety:.1%}")
        
        if self.language == 'zh':
            reasoning_parts.append(f"整体质量评分: {score_percentage:.1f}%")
        else:
            reasoning_parts.append(f"Overall quality score: {score_percentage:.1f}%")
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': ". ".join(reasoning_parts)
        }
    
    def _evaluate_buffett_principles(self, fundamental_analysis: Dict[str, Any],
                                    consistency_analysis: Dict[str, Any],
                                    moat_analysis: Dict[str, Any],
                                    management_analysis: Dict[str, Any],
                                    margin_of_safety: Optional[float]) -> Dict[str, Any]:
        """
        Evaluate how well the stock meets Buffett's key principles
        """
        principles = {
            'financial_strength': {
                'score': fundamental_analysis.get('score_percentage', 0),
                'meets_criteria': fundamental_analysis.get('score_percentage', 0) >= 60,
                'description': '强劲的ROE、低债务、良好的利润率、充足的流动性' if self.language == 'zh' else 'Strong ROE, low debt, good margins, adequate liquidity'
            },
            'predictable_earnings': {
                'score': consistency_analysis.get('score_percentage', 0),
                'meets_criteria': consistency_analysis.get('score_percentage', 0) >= 60,
                'description': '一致、增长和可预测的收益' if self.language == 'zh' else 'Consistent, growing, and predictable earnings'
            },
            'competitive_advantage': {
                'score': moat_analysis.get('score_percentage', 0),
                'meets_criteria': moat_analysis.get('score_percentage', 0) >= 50,
                'description': '可持续的竞争优势（经济护城河）' if self.language == 'zh' else 'Sustainable competitive advantages (economic moat)'
            },
            'quality_management': {
                'score': management_analysis.get('score_percentage', 0),
                'meets_criteria': management_analysis.get('score_percentage', 0) >= 50,
                'description': '对股东友好的资本配置' if self.language == 'zh' else 'Shareholder-friendly capital allocation'
            },
            'margin_of_safety': {
                'score': 100 if margin_of_safety and margin_of_safety > 0.25 else 
                        75 if margin_of_safety and margin_of_safety > 0.10 else
                        25 if margin_of_safety and margin_of_safety > 0 else 0,
                'meets_criteria': margin_of_safety is not None and margin_of_safety > 0.15,
                'description': '以相对于内在价值的显著折价购买' if self.language == 'zh' else 'Buying at significant discount to intrinsic value'
            }
        }
        
        # Calculate overall principle adherence
        total_principles_met = sum(1 for p in principles.values() if p['meets_criteria'])
        adherence_percentage = (total_principles_met / len(principles)) * 100
        
        if self.language == 'zh':
            overall_assessment = (
                '优秀的巴菲特候选股' if adherence_percentage >= 80 else
                '良好的巴菲特候选股' if adherence_percentage >= 60 else
                '边缘巴菲特候选股' if adherence_percentage >= 40 else
                '不符合巴菲特标准'
            )
        else:
            overall_assessment = (
                'Excellent Buffett candidate' if adherence_percentage >= 80 else
                'Good Buffett candidate' if adherence_percentage >= 60 else
                'Marginal Buffett candidate' if adherence_percentage >= 40 else
                'Does not meet Buffett criteria'
            )
        
        return {
            'individual_principles': principles,
            'total_principles_met': total_principles_met,
            'total_principles': len(principles),
            'adherence_percentage': adherence_percentage,
            'overall_assessment': overall_assessment
        }


def get_warren_buffett_analyzer(language: str = 'en') -> WarrenBuffettAnalyzer:
    """Factory function to get Warren Buffett analyzer instance"""
    return WarrenBuffettAnalyzer(language=language) 