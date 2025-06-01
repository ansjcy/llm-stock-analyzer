"""
Peter Lynch Investment Analyzer
Implements Peter Lynch's growth at reasonable price (GARP) investment principles
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import yfinance as yf

from src.utils.logger import stock_logger
from src.data.financial_data_service import get_financial_data_service
from src.utils.translations import t


class PeterLynchAnalyzer:
    """Analyzes stocks using Peter Lynch's investment principles"""
    
    def __init__(self, language: str = 'en'):
        self.logger = stock_logger
        self.language = language
    
    def analyze_stock(self, ticker: str, stock_info: Dict[str, Any] = None, 
                     financial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive Peter Lynch-style analysis
        
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
            garp_analysis = self._analyze_garp_metrics(stock_info, financial_data)
            growth_analysis = self._analyze_growth_consistency(financial_data, stock_info)
            business_quality_analysis = self._analyze_business_quality(stock_info, financial_data)
            market_position_analysis = self._analyze_market_position(stock_info, financial_data)
            
            # Calculate total score and signal
            total_score, max_score = self._calculate_total_score(
                garp_analysis, growth_analysis, business_quality_analysis, market_position_analysis
            )
            
            signal = self._generate_investment_signal(
                total_score, max_score, garp_analysis, growth_analysis
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
                'garp_analysis': garp_analysis,
                'growth_analysis': growth_analysis,
                'business_quality_analysis': business_quality_analysis,
                'market_position_analysis': market_position_analysis,
                'investment_reasoning': signal['reasoning'],
                'lynch_principles': self._evaluate_lynch_principles(
                    garp_analysis, growth_analysis, business_quality_analysis, market_position_analysis
                )
            }
            
            self.logger.info(f"Peter Lynch analysis completed for {ticker}")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in Peter Lynch analysis for {ticker}: {e}")
            return {
                'ticker': ticker,
                'error': str(e),
                'overall_signal': 'neutral',
                'confidence': 0.0
            }
    
    def _analyze_garp_metrics(self, stock_info: Dict[str, Any], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Growth At Reasonable Price metrics - Lynch's core philosophy
        Focus on: PEG ratio, P/E relative to growth, earnings growth rate
        """
        score = 0
        max_score = 10
        details = []
        metrics = {}
        
        try:
            # PEG Ratio Analysis - Lynch's favorite metric
            peg_ratio = stock_info.get('peg_ratio')
            pe_ratio = stock_info.get('pe_ratio')
            earnings_growth = stock_info.get('earnings_growth')
            revenue_growth = stock_info.get('revenue_growth')
            
            if peg_ratio is not None:
                metrics['peg_ratio'] = peg_ratio
                
                if peg_ratio < 0.5:  # Exceptional GARP opportunity
                    score += 4
                    if self.language == 'zh':
                        details.append(f"优秀的PEG比率 {peg_ratio:.2f} - 典型的林奇式机会")
                    else:
                        details.append(f"Excellent PEG ratio of {peg_ratio:.2f} - classic Lynch opportunity")
                elif peg_ratio < 1.0:  # Lynch's sweet spot
                    score += 3
                    if self.language == 'zh':
                        details.append(f"有吸引力的PEG比率 {peg_ratio:.2f} (林奇目标 <1.0)")
                    else:
                        details.append(f"Attractive PEG ratio of {peg_ratio:.2f} (Lynch target <1.0)")
                elif peg_ratio < 1.5:  # Still reasonable
                    score += 2
                    if self.language == 'zh':
                        details.append(f"合理的PEG比率 {peg_ratio:.2f}")
                    else:
                        details.append(f"Reasonable PEG ratio of {peg_ratio:.2f}")
                elif peg_ratio < 2.0:  # Borderline
                    score += 1
                    if self.language == 'zh':
                        details.append(f"边缘PEG比率 {peg_ratio:.2f}")
                    else:
                        details.append(f"Borderline PEG ratio of {peg_ratio:.2f}")
                else:
                    if self.language == 'zh':
                        details.append(f"高PEG比率 {peg_ratio:.2f} - 不符合林奇标准")
                    else:
                        details.append(f"High PEG ratio of {peg_ratio:.2f} - doesn't meet Lynch criteria")
            else:
                # Try to calculate PEG using available data
                growth_rate_for_peg = None
                
                # First try earnings growth
                if earnings_growth and earnings_growth > 0:
                    growth_rate_for_peg = earnings_growth
                    growth_source = "earnings"
                # If no earnings growth, try revenue growth as proxy
                elif revenue_growth and revenue_growth > 0:
                    growth_rate_for_peg = revenue_growth
                    growth_source = "revenue"
                
                if pe_ratio and growth_rate_for_peg and pe_ratio > 0:
                    # Handle growth rate properly - if it's already a percentage (>1), use as is
                    # If it's a decimal (<1), convert to percentage
                    growth_percentage = growth_rate_for_peg * 100 if growth_rate_for_peg <= 1 else growth_rate_for_peg
                    calculated_peg = pe_ratio / growth_percentage
                    metrics['calculated_peg'] = calculated_peg
                    metrics['peg_growth_source'] = growth_source
                    
                    if calculated_peg < 1.0:
                        score += 2
                        if self.language == 'zh':
                            details.append(f"基于{growth_source}增长计算的PEG比率 {calculated_peg:.2f} 显示GARP机会")
                        else:
                            details.append(f"Calculated PEG ratio of {calculated_peg:.2f} (based on {growth_source} growth) shows GARP opportunity")
                    elif calculated_peg < 2.0:
                        score += 1
                        if self.language == 'zh':
                            details.append(f"基于{growth_source}增长计算的PEG比率 {calculated_peg:.2f} 尚可接受")
                        else:
                            details.append(f"Calculated PEG ratio of {calculated_peg:.2f} (based on {growth_source} growth) is acceptable")
                    else:
                        if self.language == 'zh':
                            details.append(f"基于{growth_source}增长计算的PEG比率 {calculated_peg:.2f} 偏高")
                        else:
                            details.append(f"Calculated PEG ratio of {calculated_peg:.2f} (based on {growth_source} growth) is elevated")
                else:
                    if self.language == 'zh':
                        details.append("PEG比率数据不可用 - 缺少关键增长或估值数据")
                    else:
                        details.append("PEG ratio unavailable - missing key growth or valuation data")
            
            # P/E Ratio Analysis (Lynch preferred moderate P/E ratios)
            if pe_ratio is not None:
                metrics['pe_ratio'] = pe_ratio
                
                if 10 <= pe_ratio <= 20:  # Lynch's preferred range
                    score += 2
                    if self.language == 'zh':
                        details.append(f"理想的市盈率范围 {pe_ratio:.1f} (林奇偏好10-20)")
                    else:
                        details.append(f"Ideal P/E range of {pe_ratio:.1f} (Lynch preferred 10-20)")
                elif 5 <= pe_ratio < 10:  # Very cheap, but check for problems
                    score += 1
                    if self.language == 'zh':
                        details.append(f"低市盈率 {pe_ratio:.1f} - 需要检查是否有问题")
                    else:
                        details.append(f"Low P/E of {pe_ratio:.1f} - check for underlying issues")
                elif 20 < pe_ratio <= 30 and earnings_growth and earnings_growth > 0.20:  # High P/E justified by growth
                    score += 1
                    if self.language == 'zh':
                        details.append(f"高市盈率 {pe_ratio:.1f} 但强劲增长可能证明其合理性")
                    else:
                        details.append(f"High P/E of {pe_ratio:.1f} but strong growth may justify it")
                else:
                    if self.language == 'zh':
                        details.append(f"市盈率 {pe_ratio:.1f} 超出林奇偏好范围")
                    else:
                        details.append(f"P/E of {pe_ratio:.1f} outside Lynch's preferred range")
            else:
                if self.language == 'zh':
                    details.append("市盈率数据不可用")
                else:
                    details.append("P/E ratio not available")
            
            # Earnings Growth Rate Analysis - adjusted for large companies
            if earnings_growth is not None:
                metrics['earnings_growth'] = earnings_growth
                # Handle both decimal and percentage formats
                growth_percentage = earnings_growth * 100 if earnings_growth <= 1 else earnings_growth
                
                # Get market cap to adjust growth expectations
                market_cap = stock_info.get('market_cap', 0)
                
                if market_cap > 100e9:  # Large cap (>$100B) - lower growth expectations
                    if 8 <= growth_percentage <= 20:  # Adjusted for large caps
                        score += 3
                        if self.language == 'zh':
                            details.append(f"大型公司的良好盈利增长率 {growth_percentage:.1f}%")
                        else:
                            details.append(f"Good earnings growth of {growth_percentage:.1f}% for large cap")
                    elif 5 <= growth_percentage < 8:  # Decent for large cap
                        score += 2
                        if self.language == 'zh':
                            details.append(f"大型公司的适度盈利增长率 {growth_percentage:.1f}%")
                        else:
                            details.append(f"Decent earnings growth of {growth_percentage:.1f}% for large cap")
                    elif growth_percentage > 20:  # Strong growth for large cap
                        score += 2
                        if self.language == 'zh':
                            details.append(f"大型公司的强劲盈利增长率 {growth_percentage:.1f}%")
                        else:
                            details.append(f"Strong earnings growth of {growth_percentage:.1f}% for large cap")
                    else:
                        if self.language == 'zh':
                            details.append(f"大型公司的低盈利增长率 {growth_percentage:.1f}%")
                        else:
                            details.append(f"Low earnings growth of {growth_percentage:.1f}% for large cap")
                elif market_cap > 10e9:  # Mid cap ($10B-$100B)
                    if 15 <= growth_percentage <= 30:  # Lynch's sweet spot
                        score += 3
                        if self.language == 'zh':
                            details.append(f"理想的盈利增长率 {growth_percentage:.1f}% (林奇目标15-30%)")
                        else:
                            details.append(f"Ideal earnings growth of {growth_percentage:.1f}% (Lynch target 15-30%)")
                    elif 10 <= growth_percentage < 15:  # Decent growth
                        score += 2
                        if self.language == 'zh':
                            details.append(f"适度的盈利增长率 {growth_percentage:.1f}%")
                        else:
                            details.append(f"Decent earnings growth of {growth_percentage:.1f}%")
                    elif 30 < growth_percentage <= 50:  # High growth, but sustainable?
                        score += 2
                        if self.language == 'zh':
                            details.append(f"高盈利增长率 {growth_percentage:.1f}% - 检查可持续性")
                        else:
                            details.append(f"High earnings growth of {growth_percentage:.1f}% - check sustainability")
                    elif growth_percentage > 50:  # Too high, unsustainable
                        score += 1
                        if self.language == 'zh':
                            details.append(f"非常高的盈利增长率 {growth_percentage:.1f}% - 可能不可持续")
                        else:
                            details.append(f"Very high earnings growth of {growth_percentage:.1f}% - likely unsustainable")
                    else:
                        if self.language == 'zh':
                            details.append(f"低盈利增长率 {growth_percentage:.1f}% - 不符合林奇标准")
                        else:
                            details.append(f"Low earnings growth of {growth_percentage:.1f}% - doesn't meet Lynch criteria")
                else:  # Small cap (<$10B) - original criteria
                    if 15 <= growth_percentage <= 30:  # Lynch's sweet spot
                        score += 3
                        if self.language == 'zh':
                            details.append(f"理想的盈利增长率 {growth_percentage:.1f}% (林奇目标15-30%)")
                        else:
                            details.append(f"Ideal earnings growth of {growth_percentage:.1f}% (Lynch target 15-30%)")
                    elif 10 <= growth_percentage < 15:  # Decent growth
                        score += 2
                        if self.language == 'zh':
                            details.append(f"适度的盈利增长率 {growth_percentage:.1f}%")
                        else:
                            details.append(f"Decent earnings growth of {growth_percentage:.1f}%")
                    elif 30 < growth_percentage <= 50:  # High growth, but sustainable?
                        score += 2
                        if self.language == 'zh':
                            details.append(f"高盈利增长率 {growth_percentage:.1f}% - 检查可持续性")
                        else:
                            details.append(f"High earnings growth of {growth_percentage:.1f}% - check sustainability")
                    elif growth_percentage > 50:  # Too high, unsustainable
                        score += 1
                        if self.language == 'zh':
                            details.append(f"非常高的盈利增长率 {growth_percentage:.1f}% - 可能不可持续")
                        else:
                            details.append(f"Very high earnings growth of {growth_percentage:.1f}% - likely unsustainable")
                    else:
                        if self.language == 'zh':
                            details.append(f"低盈利增长率 {growth_percentage:.1f}% - 不符合林奇标准")
                        else:
                            details.append(f"Low earnings growth of {growth_percentage:.1f}% - doesn't meet Lynch criteria")
            else:
                if self.language == 'zh':
                    details.append("盈利增长率数据不可用")
                else:
                    details.append("Earnings growth data not available")
            
            # Price-to-Sales Analysis (Lynch liked reasonable P/S ratios)
            price_to_sales = stock_info.get('price_to_sales')
            if price_to_sales is not None:
                metrics['price_to_sales'] = price_to_sales
                
                if price_to_sales < 1.0:  # Very attractive
                    score += 1
                    if self.language == 'zh':
                        details.append(f"有吸引力的市销率 {price_to_sales:.2f}")
                    else:
                        details.append(f"Attractive price-to-sales ratio of {price_to_sales:.2f}")
                elif price_to_sales > 5.0:  # Too expensive
                    if self.language == 'zh':
                        details.append(f"高市销率 {price_to_sales:.2f} 可能表明估值过高")
                    else:
                        details.append(f"High price-to-sales ratio of {price_to_sales:.2f} may indicate overvaluation")
                        
        except Exception as e:
            self.logger.error(f"Error in GARP analysis: {e}")
            details.append(f"Error in GARP analysis: {e}")
        
        return {
            'score': score,
            'max_score': max_score,
            'score_percentage': (score / max_score * 100) if max_score > 0 else 0,
            'details': details,
            'metrics': metrics,
            'category': 'Growth At Reasonable Price'
        }
    
    def _analyze_growth_consistency(self, financial_data: Dict[str, Any], stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze growth consistency - Lynch valued predictable growth
        Focus on: Revenue growth trends, earnings consistency, margins stability
        """
        score = 0
        max_score = 8
        details = []
        
        try:
            # Get market cap for context
            market_cap = stock_info.get('market_cap', 0)
            
            # Revenue growth consistency
            income_statement = financial_data.get('income_statement')
            if income_statement is not None and not income_statement.empty:
                revenue_data = None
                
                # Look for revenue/total revenue row
                for index in income_statement.index:
                    if 'total revenue' in str(index).lower() or 'revenue' in str(index).lower():
                        revenue_data = income_statement.loc[index].dropna()
                        break
                
                if revenue_data is not None and len(revenue_data) >= 3:
                    revenue_data = revenue_data.sort_index(ascending=False)  # Most recent first
                    revenue_values = revenue_data.values
                    
                    # Calculate year-over-year growth rates
                    growth_rates = []
                    for i in range(len(revenue_values) - 1):
                        if revenue_values[i+1] > 0:
                            growth_rate = (revenue_values[i] - revenue_values[i+1]) / revenue_values[i+1]
                            growth_rates.append(growth_rate)
                    
                    if len(growth_rates) >= 2:
                        avg_growth = np.mean(growth_rates)
                        growth_volatility = np.std(growth_rates)
                        
                        # Adjust expectations based on company size
                        if market_cap > 100e9:  # Large cap - lower growth expectations
                            if avg_growth > 0.05 and growth_volatility < 0.15:  # 5%+ growth, low volatility
                                score += 3
                                if self.language == 'zh':
                                    details.append(f"大型公司的一致收入增长 {avg_growth:.1%} ± {growth_volatility:.1%}")
                                else:
                                    details.append(f"Consistent revenue growth for large cap: {avg_growth:.1%} ± {growth_volatility:.1%}")
                            elif avg_growth > 0.02:  # At least some growth for large cap
                                score += 2
                                if self.language == 'zh':
                                    details.append(f"大型公司的适度收入增长 {avg_growth:.1%}")
                                else:
                                    details.append(f"Moderate revenue growth for large cap: {avg_growth:.1%}")
                            else:
                                if self.language == 'zh':
                                    details.append("收入增长缓慢或下降")
                                else:
                                    details.append("Slow or declining revenue growth")
                        else:  # Mid/small cap - original criteria
                            if avg_growth > 0.10 and growth_volatility < 0.15:  # 10%+ growth, low volatility
                                score += 3
                                if self.language == 'zh':
                                    details.append(f"一致的收入增长 {avg_growth:.1%} ± {growth_volatility:.1%}")
                                else:
                                    details.append(f"Consistent revenue growth of {avg_growth:.1%} ± {growth_volatility:.1%}")
                            elif avg_growth > 0.05:  # At least some growth
                                score += 2
                                if self.language == 'zh':
                                    details.append(f"适度的收入增长 {avg_growth:.1%}")
                                else:
                                    details.append(f"Moderate revenue growth of {avg_growth:.1%}")
                            else:
                                if self.language == 'zh':
                                    details.append("收入增长缓慢或下降")
                                else:
                                    details.append("Slow or declining revenue growth")
            
            # Earnings quality and consistency
            quarterly_financials = financial_data.get('quarterly_financials')
            if quarterly_financials is not None and not quarterly_financials.empty:
                earnings_data = None
                
                for index in quarterly_financials.index:
                    if 'net income' in str(index).lower():
                        earnings_data = quarterly_financials.loc[index].dropna()
                        break
                
                if earnings_data is not None and len(earnings_data) >= 3:  # Adjust for varying data length
                    earnings_data = earnings_data.sort_index(ascending=False)
                    earnings_values = earnings_data.values
                    
                    # Check for positive earnings trend - use available quarters
                    quarters_to_check = min(4, len(earnings_values))
                    positive_quarters = sum(1 for x in earnings_values[:quarters_to_check] if x > 0)
                    
                    if positive_quarters == quarters_to_check:  # All positive
                        score += 2
                        if self.language == 'zh':
                            details.append(f"连续{quarters_to_check}个季度盈利")
                        else:
                            details.append(f"{quarters_to_check} consecutive quarters of positive earnings")
                    elif positive_quarters >= quarters_to_check * 0.75:  # Mostly positive
                        score += 1
                        if self.language == 'zh':
                            details.append("大部分季度盈利")
                        else:
                            details.append("Mostly positive quarterly earnings")
                    else:
                        if self.language == 'zh':
                            details.append("盈利不稳定")
                        else:
                            details.append("Inconsistent earnings pattern")
                            
                    # Check for earnings acceleration - adjust for available data
                    if len(earnings_values) >= 6:  # Need at least 6 quarters for comparison
                        recent_quarters = min(3, len(earnings_values) // 2)
                        older_quarters = min(3, len(earnings_values) - recent_quarters)
                        
                        recent_avg = np.mean(earnings_values[:recent_quarters])
                        older_avg = np.mean(earnings_values[recent_quarters:recent_quarters + older_quarters])
                        
                        if recent_avg > older_avg and older_avg > 0:
                            acceleration = (recent_avg - older_avg) / older_avg
                            if acceleration > 0.20:  # 20%+ acceleration
                                score += 2
                                if self.language == 'zh':
                                    details.append(f"盈利加速增长 {acceleration:.1%}")
                                else:
                                    details.append(f"Earnings acceleration of {acceleration:.1%}")
                            elif acceleration > 0.10:  # 10%+ acceleration
                                score += 1
                                if self.language == 'zh':
                                    details.append(f"适度的盈利加速 {acceleration:.1%}")
                                else:
                                    details.append(f"Moderate earnings acceleration of {acceleration:.1%}")
            
            # Margin stability (Lynch preferred stable or improving margins)
            profit_margin = stock_info.get('profit_margins')
            operating_margin = stock_info.get('operating_margins')
            
            if profit_margin and profit_margin > 0.05:  # At least 5% profit margin
                score += 1
                if self.language == 'zh':
                    details.append(f"健康的净利润率 {profit_margin:.1%}")
                else:
                    details.append(f"Healthy profit margin of {profit_margin:.1%}")
                    
        except Exception as e:
            self.logger.error(f"Error in growth consistency analysis: {e}")
            details.append(f"Error analyzing growth consistency: {e}")
        
        return {
            'score': score,
            'max_score': max_score,
            'score_percentage': (score / max_score * 100) if max_score > 0 else 0,
            'details': details,
            'category': 'Growth Consistency'
        }
    
    def _analyze_business_quality(self, stock_info: Dict[str, Any], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze business quality - Lynch looked for simple, understandable businesses
        Focus on: ROE, debt levels, business model simplicity indicators
        """
        score = 0
        max_score = 6
        details = []
        
        try:
            # Return on Equity - Lynch liked companies that could reinvest earnings profitably
            roe = stock_info.get('return_on_equity')
            if roe is not None:
                # Handle ROE values properly - ROE is typically given as decimal (0.25 = 25%)
                # But sometimes as percentage (25.0 = 25%), so we need to detect which format
                if roe > 1:
                    roe_decimal = roe / 100  # Convert percentage to decimal
                else:
                    roe_decimal = roe  # Already as decimal
                
                if roe_decimal > 0.15:  # 15%+ ROE
                    score += 2
                    if self.language == 'zh':
                        details.append(f"强劲的股本回报率 {roe_decimal:.1%}")
                    else:
                        details.append(f"Strong ROE of {roe_decimal:.1%}")
                elif roe_decimal > 0.10:  # 10%+ ROE
                    score += 1
                    if self.language == 'zh':
                        details.append(f"适度的股本回报率 {roe_decimal:.1%}")
                    else:
                        details.append(f"Moderate ROE of {roe_decimal:.1%}")
                elif roe_decimal > 0:  # Positive but low ROE
                    if self.language == 'zh':
                        details.append(f"较低的股本回报率 {roe_decimal:.1%}")
                    else:
                        details.append(f"Low ROE of {roe_decimal:.1%}")
                else:  # Negative ROE - problematic
                    if self.language == 'zh':
                        details.append(f"负股本回报率 {roe_decimal:.1%} - 亏损公司")
                    else:
                        details.append(f"Negative ROE of {roe_decimal:.1%} - loss-making company")
            else:
                if self.language == 'zh':
                    details.append("股本回报率数据不可用")
                else:
                    details.append("ROE data not available")
            
            # Debt levels - Lynch preferred companies with manageable debt
            debt_to_equity = stock_info.get('debt_to_equity')
            if debt_to_equity is not None:
                # Handle debt-to-equity ratio - typically given as percentage or ratio
                # In your example: debt_to_equity = 51.641, which likely means 51.64%
                if debt_to_equity > 10:
                    debt_ratio = debt_to_equity / 100  # Convert percentage to decimal
                else:
                    debt_ratio = debt_to_equity  # Already as decimal ratio
                    
                if debt_ratio < 0.25:  # Very low debt (< 25%)
                    score += 2
                    if self.language == 'zh':
                        details.append(f"低债务水平 {debt_ratio:.1%} - 财务灵活性强")
                    else:
                        details.append(f"Low debt level of {debt_ratio:.1%} - high financial flexibility")
                elif debt_ratio < 0.50:  # Moderate debt (25-50%)
                    score += 1
                    if self.language == 'zh':
                        details.append(f"适度的债务水平 {debt_ratio:.1%}")
                    else:
                        details.append(f"Moderate debt level of {debt_ratio:.1%}")
                elif debt_ratio < 1.0:  # High debt (50-100%)
                    if self.language == 'zh':
                        details.append(f"高债务水平 {debt_ratio:.1%} - 增加风险")
                    else:
                        details.append(f"High debt level of {debt_ratio:.1%} - increases risk")
                else:  # Very high debt (>100%) - potentially problematic
                    if self.language == 'zh':
                        details.append(f"非常高的债务水平 {debt_ratio:.1%} - 财务风险极高")
                    else:
                        details.append(f"Very high debt level of {debt_ratio:.1%} - severe financial risk")
            else:
                if self.language == 'zh':
                    details.append("债务股权比数据不可用")
                else:
                    details.append("Debt-to-equity data not available")
            
            # Free Cash Flow - Lynch valued companies that generated cash
            free_cash_flow = stock_info.get('free_cash_flow')
            if free_cash_flow and free_cash_flow > 0:
                score += 1
                if self.language == 'zh':
                    details.append("正自由现金流 - 能够自我投资")
                else:
                    details.append("Positive free cash flow - able to self-fund investments")
            elif free_cash_flow and free_cash_flow < 0:
                if self.language == 'zh':
                    details.append("负自由现金流 - 需要外部资金")
                else:
                    details.append("Negative free cash flow - requires external funding")
            
            # Current Ratio - Lynch wanted financially stable companies
            current_ratio = stock_info.get('current_ratio')
            if current_ratio is not None:
                if current_ratio > 1.5:  # Good liquidity
                    score += 1
                    if self.language == 'zh':
                        details.append(f"强劲的流动性 {current_ratio:.1f}")
                    else:
                        details.append(f"Strong liquidity ratio of {current_ratio:.1f}")
                elif current_ratio < 1.0:  # Poor liquidity
                    if self.language == 'zh':
                        details.append(f"较弱的流动性 {current_ratio:.1f}")
                    else:
                        details.append(f"Weak liquidity ratio of {current_ratio:.1f}")
                        
        except Exception as e:
            self.logger.error(f"Error in business quality analysis: {e}")
            details.append(f"Error analyzing business quality: {e}")
        
        return {
            'score': score,
            'max_score': max_score,
            'score_percentage': (score / max_score * 100) if max_score > 0 else 0,
            'details': details,
            'category': 'Business Quality'
        }
    
    def _analyze_market_position(self, stock_info: Dict[str, Any], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market position and company characteristics
        Lynch preferred mid-cap growth companies with room to grow
        """
        score = 0
        max_score = 4
        details = []
        
        try:
            # Market cap analysis - Lynch's preferred range
            market_cap = stock_info.get('market_cap')
            if market_cap is not None:
                if 2e9 <= market_cap <= 50e9:  # $2B to $50B - Lynch's sweet spot
                    score += 2
                    if self.language == 'zh':
                        details.append(f"理想的市值范围 ${market_cap/1e9:.1f}B (林奇偏好中型股)")
                    else:
                        details.append(f"Ideal market cap of ${market_cap/1e9:.1f}B (Lynch preferred mid-caps)")
                elif 500e6 <= market_cap < 2e9:  # Small cap with growth potential
                    score += 1
                    if self.language == 'zh':
                        details.append(f"小盘股 ${market_cap/1e6:.0f}M - 潜在增长机会")
                    else:
                        details.append(f"Small cap ${market_cap/1e6:.0f}M - potential growth opportunity")
                elif market_cap > 100e9:  # Large cap - limited growth potential
                    if self.language == 'zh':
                        details.append(f"大盘股 ${market_cap/1e9:.1f}B - 增长潜力有限")
                    else:
                        details.append(f"Large cap ${market_cap/1e9:.1f}B - limited growth potential")
                else:
                    if self.language == 'zh':
                        details.append(f"微型股 ${market_cap/1e6:.0f}M - 风险较高")
                    else:
                        details.append(f"Micro cap ${market_cap/1e6:.0f}M - higher risk")
            
            # Industry and sector considerations
            sector = stock_info.get('sector', '')
            industry = stock_info.get('industry', '')
            
            # Lynch preferred certain sectors and avoided complex financial companies
            growth_sectors = ['Technology', 'Healthcare', 'Consumer Discretionary', 'Consumer Cyclical']
            stable_sectors = ['Consumer Staples', 'Industrials']
            
            if any(sector_name in sector for sector_name in growth_sectors):
                score += 1
                if self.language == 'zh':
                    details.append(f"成长型行业：{sector}")
                else:
                    details.append(f"Growth sector: {sector}")
            elif any(sector_name in sector for sector_name in stable_sectors):
                score += 1
                if self.language == 'zh':
                    details.append(f"稳定行业：{sector}")
                else:
                    details.append(f"Stable sector: {sector}")
            elif 'Financial' in sector or 'Bank' in industry:
                if self.language == 'zh':
                    details.append("金融行业 - 林奇通常避免复杂的金融公司")
                else:
                    details.append("Financial sector - Lynch typically avoided complex financial companies")
            
            # Employee data analysis with multiple field name checks
            employees = None
            # Check multiple possible field names for employee count
            possible_employee_fields = [
                'full_time_employees', 'fullTimeEmployees', 'employees', 
                'number_of_employees', 'total_employees', 'employee_count'
            ]
            
            for field in possible_employee_fields:
                employees = stock_info.get(field)
                if employees is not None:
                    break
            
            if employees and employees > 1000:  # Substantial company
                score += 1
                if self.language == 'zh':
                    details.append(f"实质性企业规模 ({employees:,} 员工)")
                else:
                    details.append(f"Substantial company size ({employees:,} employees)")
            elif employees is None:
                if self.language == 'zh':
                    details.append("员工数据不可用")
                else:
                    details.append("Employee data not available")
                    
        except Exception as e:
            self.logger.error(f"Error in market position analysis: {e}")
            details.append(f"Error analyzing market position: {e}")
        
        return {
            'score': score,
            'max_score': max_score,
            'score_percentage': (score / max_score * 100) if max_score > 0 else 0,
            'details': details,
            'category': 'Market Position'
        }
    
    def _calculate_total_score(self, garp_analysis: Dict[str, Any],
                              growth_analysis: Dict[str, Any],
                              business_quality_analysis: Dict[str, Any],
                              market_position_analysis: Dict[str, Any]) -> Tuple[float, float]:
        """Calculate total score from all analyses"""
        total_score = (
            garp_analysis.get('score', 0) +
            growth_analysis.get('score', 0) +
            business_quality_analysis.get('score', 0) +
            market_position_analysis.get('score', 0)
        )
        
        max_score = (
            garp_analysis.get('max_score', 0) +
            growth_analysis.get('max_score', 0) +
            business_quality_analysis.get('max_score', 0) +
            market_position_analysis.get('max_score', 0)
        )
        
        return total_score, max_score
    
    def _generate_investment_signal(self, total_score: float, max_score: float,
                                   garp_analysis: Dict[str, Any],
                                   growth_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate investment signal based on Lynch's criteria
        """
        score_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Base confidence on score
        confidence = min(score_percentage, 95)  # Cap at 95%
        
        reasoning_parts = []
        
        # Check for Lynch's key criteria
        peg_ratio = garp_analysis.get('metrics', {}).get('peg_ratio')
        garp_score = garp_analysis.get('score_percentage', 0)
        growth_score = growth_analysis.get('score_percentage', 0)
        
        # Determine signal based on Lynch's methodology
        if score_percentage >= 70:  # Strong overall score
            if peg_ratio and peg_ratio < 1.0:  # Lynch's favorite criterion
                signal = "bullish"
                confidence = min(confidence + 15, 95)
                if self.language == 'zh':
                    reasoning_parts.append(f"符合林奇的GARP标准：PEG比率 {peg_ratio:.2f} < 1.0")
                else:
                    reasoning_parts.append(f"Meets Lynch's GARP criteria: PEG ratio {peg_ratio:.2f} < 1.0")
            elif garp_score >= 60:  # Good GARP metrics
                signal = "bullish"
                if self.language == 'zh':
                    reasoning_parts.append("强劲的增长与合理价格指标")
                else:
                    reasoning_parts.append("Strong growth at reasonable price metrics")
            else:
                signal = "neutral"
                if self.language == 'zh':
                    reasoning_parts.append("整体质量良好但GARP指标混合")
                else:
                    reasoning_parts.append("Good overall quality but mixed GARP metrics")
                
        elif score_percentage >= 50:  # Decent score
            if peg_ratio and peg_ratio < 0.75:  # Excellent PEG compensates
                signal = "bullish"
                if self.language == 'zh':
                    reasoning_parts.append(f"优秀的PEG比率 {peg_ratio:.2f} 弥补了其他弱点")
                else:
                    reasoning_parts.append(f"Excellent PEG ratio {peg_ratio:.2f} compensates for other weaknesses")
            elif growth_score >= 60:  # Strong growth story
                signal = "neutral"
                if self.language == 'zh':
                    reasoning_parts.append("强劲的增长但需要更好的估值")
                else:
                    reasoning_parts.append("Strong growth but needs better valuation")
            else:
                signal = "neutral"
                if self.language == 'zh':
                    reasoning_parts.append("混合信号需要进一步分析")
                else:
                    reasoning_parts.append("Mixed signals require further analysis")
                
        else:  # Weak score
            signal = "bearish"
            if self.language == 'zh':
                reasoning_parts.append("不符合林奇的投资标准")
            else:
                reasoning_parts.append("Does not meet Lynch's investment criteria")
        
        # Add specific reasoning
        if self.language == 'zh':
            reasoning_parts.append(f"总体质量评分: {score_percentage:.1f}%")
        else:
            reasoning_parts.append(f"Overall quality score: {score_percentage:.1f}%")
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': ". ".join(reasoning_parts)
        }
    
    def _evaluate_lynch_principles(self, garp_analysis: Dict[str, Any],
                                  growth_analysis: Dict[str, Any],
                                  business_quality_analysis: Dict[str, Any],
                                  market_position_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate how well the stock meets Lynch's key principles
        """
        principles = {
            'growth_at_reasonable_price': {
                'score': garp_analysis.get('score_percentage', 0),
                'meets_criteria': garp_analysis.get('score_percentage', 0) >= 60,
                'description': 'PEG比率 < 1.0，合理的市盈率，强劲的盈利增长' if self.language == 'zh' else 'PEG ratio <1.0, reasonable P/E, strong earnings growth'
            },
            'consistent_growth': {
                'score': growth_analysis.get('score_percentage', 0),
                'meets_criteria': growth_analysis.get('score_percentage', 0) >= 60,
                'description': '一致的收入和盈利增长，最好是加速增长' if self.language == 'zh' else 'Consistent revenue and earnings growth, preferably accelerating'
            },
            'business_quality': {
                'score': business_quality_analysis.get('score_percentage', 0),
                'meets_criteria': business_quality_analysis.get('score_percentage', 0) >= 50,
                'description': '强劲的ROE，可管理的债务，简单的商业模式' if self.language == 'zh' else 'Strong ROE, manageable debt, simple business model'
            },
            'market_position': {
                'score': market_position_analysis.get('score_percentage', 0),
                'meets_criteria': market_position_analysis.get('score_percentage', 0) >= 50,
                'description': '中型股，增长行业，有增长空间' if self.language == 'zh' else 'Mid-cap size, growth industry, room for expansion'
            }
        }
        
        # Calculate overall principle adherence
        total_principles_met = sum(1 for p in principles.values() if p['meets_criteria'])
        adherence_percentage = (total_principles_met / len(principles)) * 100
        
        if self.language == 'zh':
            overall_assessment = (
                '优秀的林奇候选股' if adherence_percentage >= 75 else
                '良好的林奇候选股' if adherence_percentage >= 50 else
                '边缘林奇候选股' if adherence_percentage >= 25 else
                '不符合林奇标准'
            )
        else:
            overall_assessment = (
                'Excellent Lynch candidate' if adherence_percentage >= 75 else
                'Good Lynch candidate' if adherence_percentage >= 50 else
                'Marginal Lynch candidate' if adherence_percentage >= 25 else
                'Does not meet Lynch criteria'
            )
        
        return {
            'individual_principles': principles,
            'total_principles_met': total_principles_met,
            'total_principles': len(principles),
            'adherence_percentage': adherence_percentage,
            'overall_assessment': overall_assessment
        }


def get_peter_lynch_analyzer(language: str = 'en') -> PeterLynchAnalyzer:
    """Factory function to get Peter Lynch analyzer instance"""
    return PeterLynchAnalyzer(language=language) 