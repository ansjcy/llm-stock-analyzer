"""
Technical analysis indicators for stock analysis
Enhanced with comprehensive indicators, correlation analysis, and strategic combinations
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
import pandas_ta as ta
from scipy import stats
import yfinance as yf
import warnings

from src.utils.logger import stock_logger


def safe_float(value, default=0.0):
    """Safely convert a value to float, handling NaN cases"""
    try:
        if pd.isna(value) or np.isnan(value):
            return default
        return float(value)
    except (ValueError, TypeError, OverflowError):
        return default


class TechnicalAnalyzer:
    """Enhanced technical analysis indicators calculator with correlation analysis"""
    
    def __init__(self, benchmark_symbols: List[str] = None):
        self.benchmark_symbols = benchmark_symbols or [
            '^GSPC',  # S&P 500
            '^DJI',   # Dow Jones
            '^IXIC',  # NASDAQ
            '^RUT',   # Russell 2000 (Small Cap)
            'EFA',    # MSCI EAFE (International Developed Markets)
            'EEM',    # MSCI Emerging Markets
            'VTI',    # Total Stock Market
            'QQQ',    # NASDAQ 100 Tech Heavy
            'XLF',    # Financial Sector
            'XLE',    # Energy Sector  
            'XLK',    # Technology Sector
            'XLV',    # Healthcare Sector
            'XLI',    # Industrial Sector
            'XLP',    # Consumer Staples
            'XLY',    # Consumer Discretionary
            'XLU',    # Utilities
            'XLRE',   # Real Estate
            'XLB',    # Materials
            'GLD',    # Gold
            'TLT',    # 20+ Year Treasury Bonds
            'HYG',    # High Yield Corporate Bonds
            'VNQ'     # Real Estate Investment Trusts
        ]
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate various moving averages with trend strength analysis"""
        try:
            df_ta = df.copy()
            df_ta.ta.sma(length=20, append=True)
            df_ta.ta.sma(length=50, append=True)
            df_ta.ta.sma(length=200, append=True)
            
            # Exponential Moving Averages
            df_ta.ta.ema(length=8, append=True)
            df_ta.ta.ema(length=21, append=True)
            df_ta.ta.ema(length=55, append=True)
            
            current_price = safe_float(df['Close'].iloc[-1])
            sma_20 = safe_float(df_ta[f'SMA_20'].iloc[-1])
            sma_50 = safe_float(df_ta[f'SMA_50'].iloc[-1])
            sma_200 = safe_float(df_ta[f'SMA_200'].iloc[-1])
            
            # Calculate MA crossover signals
            golden_cross = False
            death_cross = False
            if len(df_ta) >= 2:
                sma_50_prev = safe_float(df_ta[f'SMA_50'].iloc[-2])
                sma_200_prev = safe_float(df_ta[f'SMA_200'].iloc[-2])
                
                golden_cross = sma_50 > sma_200 and sma_50_prev <= sma_200_prev
                death_cross = sma_50 < sma_200 and sma_50_prev >= sma_200_prev
            
            return {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'ema_8': safe_float(df_ta[f'EMA_8'].iloc[-1]),
                'ema_21': safe_float(df_ta[f'EMA_21'].iloc[-1]),
                'ema_55': safe_float(df_ta[f'EMA_55'].iloc[-1]),
                'price_vs_sma_20': (current_price / sma_20 - 1) * 100 if sma_20 > 0 else 0,
                'price_vs_sma_50': (current_price / sma_50 - 1) * 100 if sma_50 > 0 else 0,
                'price_vs_sma_200': (current_price / sma_200 - 1) * 100 if sma_200 > 0 else 0,
                'sma_trend': 'bullish' if sma_20 > sma_50 > sma_200 else 'bearish' if sma_20 < sma_50 < sma_200 else 'neutral',
                'golden_cross': golden_cross,
                'death_cross': death_cross
            }
        except Exception as e:
            stock_logger.error(f"Error calculating moving averages: {e}")
            return {}
    
    def calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced momentum indicators including StochRSI and MFI"""
        try:
            df_ta = df.copy()
            
            # RSI
            df_ta.ta.rsi(length=14, append=True)
            
            # Stochastic RSI
            try:
                df_ta.ta.stochrsi(length=14, rsi_length=14, k=3, d=3, append=True)
            except:
                pass
            
            # Stochastic Oscillator
            df_ta.ta.stoch(k=14, d=3, append=True)
            
            # Williams %R
            df_ta.ta.willr(length=14, append=True)
            
            # Rate of Change
            df_ta.ta.roc(length=10, append=True)
            
            # Money Flow Index
            try:
                # Suppress warnings about dtype compatibility in pandas-ta
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", FutureWarning)
                    df_ta.ta.mfi(length=14, append=True)
            except:
                pass
            
            # Commodity Channel Index
            try:
                df_ta.ta.cci(length=20, append=True)
            except:
                pass
            
            rsi_val = safe_float(df_ta['RSI_14'].iloc[-1])
            stoch_k = safe_float(df_ta['STOCHk_14_3_3'].iloc[-1])
            willr_val = safe_float(df_ta['WILLR_14'].iloc[-1])
            roc_val = safe_float(df_ta['ROC_10'].iloc[-1])
            
            # Get dynamic column names for additional indicators
            stochrsi_k_cols = [col for col in df_ta.columns if 'STOCHRSIk' in col]
            mfi_cols = [col for col in df_ta.columns if 'MFI' in col]
            cci_cols = [col for col in df_ta.columns if 'CCI' in col]
            
            stochrsi_k = safe_float(df_ta[stochrsi_k_cols[0]].iloc[-1]) if stochrsi_k_cols else 50
            mfi_val = safe_float(df_ta[mfi_cols[0]].iloc[-1]) if mfi_cols else 50
            cci_val = safe_float(df_ta[cci_cols[0]].iloc[-1]) if cci_cols else 0
            
            return {
                'rsi': rsi_val,
                'rsi_signal': 'overbought' if rsi_val > 70 else 'oversold' if rsi_val < 30 else 'neutral',
                'stochrsi_k': stochrsi_k,
                'stochrsi_signal': 'overbought' if stochrsi_k > 80 else 'oversold' if stochrsi_k < 20 else 'neutral',
                'stoch_k': stoch_k,
                'stoch_d': safe_float(df_ta['STOCHd_14_3_3'].iloc[-1]),
                'stoch_signal': 'overbought' if stoch_k > 80 else 'oversold' if stoch_k < 20 else 'neutral',
                'williams_r': willr_val,
                'williams_signal': 'overbought' if willr_val > -20 else 'oversold' if willr_val < -80 else 'neutral',
                'roc': roc_val,
                'roc_signal': 'bullish' if roc_val > 0 else 'bearish',
                'mfi': mfi_val,
                'mfi_signal': 'overbought' if mfi_val > 80 else 'oversold' if mfi_val < 20 else 'neutral',
                'cci': cci_val,
                'cci_signal': 'overbought' if cci_val > 100 else 'oversold' if cci_val < -100 else 'neutral'
            }
        except Exception as e:
            stock_logger.error(f"Error calculating momentum indicators: {e}")
            return {}

    def calculate_ichimoku_cloud(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate Ichimoku Cloud indicators"""
        try:
            df_ta = df.copy()
            df_ta.ta.ichimoku(append=True)
            
            # Get dynamic column names
            tenkan_cols = [col for col in df_ta.columns if 'ISA' in col or 'Tenkan' in col]
            kijun_cols = [col for col in df_ta.columns if 'ISB' in col or 'Kijun' in col]
            senkou_a_cols = [col for col in df_ta.columns if 'ITS' in col or 'SenkouA' in col]
            senkou_b_cols = [col for col in df_ta.columns if 'IKS' in col or 'SenkouB' in col]
            chikou_cols = [col for col in df_ta.columns if 'ICS' in col or 'Chikou' in col]
            
            current_price = safe_float(df['Close'].iloc[-1])
            tenkan_sen = safe_float(df_ta[tenkan_cols[0]].iloc[-1]) if tenkan_cols else current_price
            kijun_sen = safe_float(df_ta[kijun_cols[0]].iloc[-1]) if kijun_cols else current_price
            senkou_a = safe_float(df_ta[senkou_a_cols[0]].iloc[-1]) if senkou_a_cols else current_price
            senkou_b = safe_float(df_ta[senkou_b_cols[0]].iloc[-1]) if senkou_b_cols else current_price
            chikou_span = safe_float(df_ta[chikou_cols[0]].iloc[-1]) if chikou_cols else current_price
            
            # Determine cloud color and position
            cloud_color = 'bullish' if senkou_a > senkou_b else 'bearish'
            price_vs_cloud = 'above' if current_price > max(senkou_a, senkou_b) else 'below' if current_price < min(senkou_a, senkou_b) else 'inside'
            
            # Signal generation
            tk_cross = 'bullish' if tenkan_sen > kijun_sen else 'bearish'
            
            return {
                'tenkan_sen': tenkan_sen,
                'kijun_sen': kijun_sen,
                'senkou_span_a': senkou_a,
                'senkou_span_b': senkou_b,
                'chikou_span': chikou_span,
                'cloud_color': cloud_color,
                'price_vs_cloud': price_vs_cloud,
                'tk_cross_signal': tk_cross,
                'ichimoku_signal': 'bullish' if price_vs_cloud == 'above' and cloud_color == 'bullish' and tk_cross == 'bullish' else 'bearish' if price_vs_cloud == 'below' and cloud_color == 'bearish' and tk_cross == 'bearish' else 'neutral'
            }
        except Exception as e:
            stock_logger.error(f"Error calculating Ichimoku indicators: {e}")
            return {}

    def calculate_pattern_recognition(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Advanced pattern recognition including candlestick patterns"""
        try:
            patterns = {}
            
            if len(df) < 2:
                return {'error': 'insufficient_data'}
            
            # Basic candlestick patterns
            body_size = abs(df['Close'] - df['Open'])
            candle_range = df['High'] - df['Low']
            
            # Doji pattern
            doji = (body_size / candle_range < 0.1).iloc[-1] if len(df) > 0 else False
            
            # Hammer and Hanging Man
            lower_shadow = df['Open'].combine(df['Close'], min) - df['Low']
            upper_shadow = df['High'] - df['Open'].combine(df['Close'], max)
            body = abs(df['Close'] - df['Open'])
            
            hammer = ((lower_shadow > 2 * body) & (upper_shadow < body)).iloc[-1] if len(df) > 0 else False
            hanging_man = ((lower_shadow > 2 * body) & (upper_shadow < body) & (df['Close'] < df['Open'])).iloc[-1] if len(df) > 0 else False
            
            # Engulfing patterns
            bullish_engulfing = False
            bearish_engulfing = False
            
            if len(df) >= 2:
                prev_candle_bearish = df['Close'].iloc[-2] < df['Open'].iloc[-2]
                curr_candle_bullish = df['Close'].iloc[-1] > df['Open'].iloc[-1]
                curr_body_larger = abs(df['Close'].iloc[-1] - df['Open'].iloc[-1]) > abs(df['Close'].iloc[-2] - df['Open'].iloc[-2])
                
                bullish_engulfing = prev_candle_bearish and curr_candle_bullish and curr_body_larger
                
                prev_candle_bullish = df['Close'].iloc[-2] > df['Open'].iloc[-2]
                curr_candle_bearish = df['Close'].iloc[-1] < df['Open'].iloc[-1]
                
                bearish_engulfing = prev_candle_bullish and curr_candle_bearish and curr_body_larger
            
            # Gap analysis
            gaps = self._detect_gaps(df)
            
            patterns.update({
                'doji': doji,
                'hammer': hammer,
                'hanging_man': hanging_man,
                'bullish_engulfing': bullish_engulfing,
                'bearish_engulfing': bearish_engulfing,
                'pattern_signal': 'bullish' if bullish_engulfing or hammer else 'bearish' if bearish_engulfing or hanging_man else 'neutral',
                'gaps': gaps
            })
            
            return patterns
            
        except Exception as e:
            stock_logger.error(f"Error in pattern recognition: {e}")
            return {}

    def _detect_gaps(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect price gaps"""
        try:
            if len(df) < 2:
                return {'gap_up': False, 'gap_down': False, 'gap_size': 0}
            
            prev_close = df['Close'].iloc[-2]
            curr_open = df['Open'].iloc[-1]
            
            gap_size = ((curr_open - prev_close) / prev_close) * 100
            gap_up = gap_size > 2  # 2% gap up
            gap_down = gap_size < -2  # 2% gap down
            
            return {
                'gap_up': gap_up,
                'gap_down': gap_down,
                'gap_size': safe_float(gap_size),
                'gap_signal': 'bullish_gap' if gap_up else 'bearish_gap' if gap_down else 'no_gap'
            }
        except Exception:
            return {'gap_up': False, 'gap_down': False, 'gap_size': 0, 'gap_signal': 'no_gap'}

    def calculate_correlation_analysis(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Multi-timeframe correlation analysis with market indices"""
        try:
            correlations = {}
            
            if len(df) < 50:  # Need sufficient data
                return {'error': 'insufficient_data_for_correlation'}
            
            # Calculate stock returns first and normalize timezone
            stock_returns = df['Close'].pct_change().dropna()
            # Properly normalize timezone - remove timezone info to make timezone-naive
            if stock_returns.index.tz is not None:
                stock_returns.index = stock_returns.index.tz_localize(None)
            
            # Get benchmark data
            benchmark_data = {}
            for benchmark in self.benchmark_symbols:
                try:
                    benchmark_df = yf.download(benchmark, period='1y', interval='1d', progress=False)
                    if not benchmark_df.empty:
                        # Handle new yfinance column structure - columns are now tuples
                        if isinstance(benchmark_df.columns, pd.MultiIndex):
                            # Multi-level columns: ('Close', '^GSPC')
                            close_col = [col for col in benchmark_df.columns if col[0] == 'Close'][0]
                            benchmark_returns = benchmark_df[close_col].pct_change().dropna()
                        else:
                            # Single-level columns: 'Close'
                            benchmark_returns = benchmark_df['Close'].pct_change().dropna()
                        
                        # Ensure benchmark data is also timezone-naive
                        if benchmark_returns.index.tz is not None:
                            benchmark_returns.index = benchmark_returns.index.tz_localize(None)
                        
                        if len(benchmark_returns) > 10:  # Ensure we have sufficient data
                            benchmark_data[benchmark] = benchmark_returns
                except Exception as e:
                    stock_logger.warning(f"Could not fetch {benchmark} data: {e}")
            
            # Calculate correlations for different timeframes
            timeframes = {
                'short_term': min(20, len(stock_returns)),
                'medium_term': min(50, len(stock_returns)),
                'long_term': min(200, len(stock_returns))
            }
            
            for timeframe, periods in timeframes.items():
                timeframe_correlations = {}
                recent_stock_returns = stock_returns.tail(periods)
                
                for benchmark, benchmark_returns in benchmark_data.items():
                    try:
                        # Align dates - ensure both series have the same index
                        aligned_data = pd.concat([recent_stock_returns, benchmark_returns], axis=1, join='inner')
                        
                        # Debug logging to help identify alignment issues
                        stock_logger.debug(f"Correlation analysis for {benchmark} ({timeframe}): "
                                         f"stock_returns={len(recent_stock_returns)}, "
                                         f"benchmark_returns={len(benchmark_returns)}, "
                                         f"aligned={len(aligned_data)}")
                        
                        if len(aligned_data) > 10:
                            # Calculate correlation between the two aligned series
                            correlation = aligned_data.iloc[:, 0].corr(aligned_data.iloc[:, 1])
                            if not pd.isna(correlation):
                                timeframe_correlations[benchmark] = safe_float(correlation)
                                stock_logger.debug(f"Calculated correlation for {benchmark} ({timeframe}): {correlation}")
                        else:
                            stock_logger.warning(f"Insufficient aligned data for {benchmark} ({timeframe}): {len(aligned_data)} points")
                    except Exception as e:
                        stock_logger.warning(f"Error calculating correlation with {benchmark} for {timeframe}: {e}")
                
                correlations[timeframe] = timeframe_correlations
            
            # Calculate beta (systematic risk)
            beta_values = {}
            if '^GSPC' in benchmark_data:
                try:
                    sp500_returns = benchmark_data['^GSPC']
                    aligned_data = pd.concat([stock_returns, sp500_returns], axis=1, join='inner')
                    if len(aligned_data) > 30:
                        covariance = aligned_data.iloc[:, 0].cov(aligned_data.iloc[:, 1])
                        market_variance = aligned_data.iloc[:, 1].var()
                        if market_variance != 0 and not pd.isna(covariance) and not pd.isna(market_variance):
                            beta = covariance / market_variance
                            beta_values['sp500_beta'] = safe_float(beta)
                            stock_logger.debug(f"Calculated beta: {beta}")
                except Exception as e:
                    stock_logger.warning(f"Error calculating beta: {e}")
            
            return {
                'correlations': correlations,
                'beta': beta_values,
                'correlation_signal': self._interpret_correlations(correlations),
                'diversification_score': self._calculate_diversification_score(correlations),
                'correlation_summary': self._generate_correlation_summary(correlations),
                'top_correlations': self._get_top_correlations(correlations),
                'diversification_recommendations': self._get_diversification_recommendations(correlations)
            }
            
        except Exception as e:
            stock_logger.error(f"Error calculating correlations: {e}")
            return {
                'correlations': {'short_term': {}, 'medium_term': {}, 'long_term': {}},
                'beta': {},
                'correlation_signal': 'unknown',
                'diversification_score': 50.0
            }

    def _interpret_correlations(self, correlations: Dict) -> str:
        """Interpret correlation patterns"""
        try:
            if not correlations or 'short_term' not in correlations:
                return 'unknown'
            
            short_term = correlations['short_term']
            if not short_term:
                return 'unknown'
            
            avg_correlation = np.mean(list(short_term.values()))
            
            if avg_correlation > 0.7:
                return 'high_market_correlation'
            elif avg_correlation > 0.3:
                return 'moderate_market_correlation'
            elif avg_correlation > -0.3:
                return 'low_market_correlation'
            else:
                return 'negative_market_correlation'
        except Exception:
            return 'unknown'

    def _calculate_diversification_score(self, correlations: Dict) -> float:
        """Calculate diversification benefit score"""
        try:
            if not correlations or 'medium_term' not in correlations:
                return 50.0
            
            medium_term = correlations['medium_term']
            if not medium_term:
                return 50.0
            
            avg_correlation = abs(np.mean(list(medium_term.values())))
            # Higher correlation = lower diversification benefit
            diversification_score = (1 - avg_correlation) * 100
            return max(0, min(100, safe_float(diversification_score)))
        except Exception:
            return 50.0

    def _generate_correlation_summary(self, correlations: Dict) -> Dict[str, Any]:
        """Generate a summary of correlations by index category"""
        try:
            # Define index categories
            categories = {
                'broad_market': ['^GSPC', '^DJI', '^IXIC', 'VTI', 'QQQ'],
                'small_cap': ['^RUT'],
                'international': ['EFA', 'EEM'],
                'sectors': ['XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLRE', 'XLB'],
                'fixed_income': ['TLT', 'HYG'],
                'alternatives': ['GLD', 'VNQ']
            }
            
            summary = {}
            for timeframe, corr_data in correlations.items():
                timeframe_summary = {}
                for category, symbols in categories.items():
                    category_correlations = []
                    for symbol in symbols:
                        if symbol in corr_data:
                            category_correlations.append(corr_data[symbol])
                    
                    if category_correlations:
                        timeframe_summary[category] = {
                            'avg_correlation': np.mean(category_correlations),
                            'max_correlation': np.max(category_correlations),
                            'min_correlation': np.min(category_correlations),
                            'count': len(category_correlations)
                        }
                
                summary[timeframe] = timeframe_summary
            
            return summary
        except Exception as e:
            stock_logger.warning(f"Error generating correlation summary: {e}")
            return {}

    def _get_top_correlations(self, correlations: Dict) -> Dict[str, Any]:
        """Get top positive and negative correlations for each timeframe"""
        try:
            top_correlations = {}
            
            for timeframe, corr_data in correlations.items():
                if not corr_data:
                    continue
                
                # Sort by correlation value
                sorted_corr = sorted(corr_data.items(), key=lambda x: x[1], reverse=True)
                
                top_correlations[timeframe] = {
                    'highest_positive': sorted_corr[:3] if len(sorted_corr) >= 3 else sorted_corr,
                    'lowest_positive': sorted_corr[-3:] if len(sorted_corr) >= 3 else sorted_corr[-len(sorted_corr):]
                }
            
            return top_correlations
        except Exception as e:
            stock_logger.warning(f"Error getting top correlations: {e}")
            return {}

    def _get_diversification_recommendations(self, correlations: Dict) -> List[str]:
        """Generate diversification recommendations based on correlation patterns"""
        try:
            recommendations = []
            
            if 'medium_term' not in correlations or not correlations['medium_term']:
                return ['Insufficient data for recommendations']
            
            medium_term = correlations['medium_term']
            
            # Check for low correlation assets
            low_corr_assets = []
            negative_corr_assets = []
            
            for symbol, corr in medium_term.items():
                if corr < 0.3:
                    low_corr_assets.append(symbol)
                if corr < 0:
                    negative_corr_assets.append(symbol)
            
            # Generate recommendations
            if negative_corr_assets:
                recommendations.append(f"Consider adding {', '.join(negative_corr_assets)} for negative correlation benefits")
            
            if low_corr_assets:
                recommendations.append(f"Low correlation assets for diversification: {', '.join(low_corr_assets)}")
            
            # Check international exposure
            international_symbols = ['EFA', 'EEM']
            international_corr = [medium_term.get(symbol, 1.0) for symbol in international_symbols if symbol in medium_term]
            
            if international_corr and np.mean(international_corr) < 0.7:
                recommendations.append("International markets show good diversification potential")
            
            # Check fixed income
            fixed_income_symbols = ['TLT', 'HYG']
            fixed_income_corr = [medium_term.get(symbol, 1.0) for symbol in fixed_income_symbols if symbol in medium_term]
            
            if fixed_income_corr and np.mean(fixed_income_corr) < 0.5:
                recommendations.append("Fixed income assets provide good portfolio balance")
            
            # Check alternatives
            alternatives = ['GLD', 'VNQ']
            alt_corr = [medium_term.get(symbol, 1.0) for symbol in alternatives if symbol in medium_term]
            
            if alt_corr and np.mean(alt_corr) < 0.6:
                recommendations.append("Alternative investments (Gold, REITs) offer diversification benefits")
            
            if not recommendations:
                recommendations.append("Consider exploring assets with lower correlation to improve diversification")
            
            return recommendations
        except Exception as e:
            stock_logger.warning(f"Error generating diversification recommendations: {e}")
            return ['Error generating recommendations']

    def calculate_strategic_combinations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Strategic combination analysis using multiple indicators"""
        try:
            # Get individual analyses
            ma_signals = self.calculate_moving_averages(df)
            momentum_signals = self.calculate_momentum_indicators(df)
            trend_signals = self.calculate_trend_indicators(df)
            volatility_signals = self.calculate_volatility_indicators(df)
            volume_signals = self.calculate_volume_indicators(df)
            
            # RSI + MACD Combination Strategy
            rsi_macd_combo = self._analyze_rsi_macd_combination(momentum_signals, trend_signals)
            
            # Bollinger Bands + RSI + MACD Strategy
            bb_rsi_macd_combo = self._analyze_bb_rsi_macd_combination(volatility_signals, momentum_signals, trend_signals)
            
            # Moving Average + RSI + Volume Integration
            ma_rsi_volume_combo = self._analyze_ma_rsi_volume_combination(ma_signals, momentum_signals, volume_signals)
            
            return {
                'rsi_macd_strategy': rsi_macd_combo,
                'bb_rsi_macd_strategy': bb_rsi_macd_combo,
                'ma_rsi_volume_strategy': ma_rsi_volume_combo,
                'overall_strategic_signal': self._generate_overall_strategic_signal({
                    'rsi_macd': rsi_macd_combo,
                    'bb_rsi_macd': bb_rsi_macd_combo,
                    'ma_rsi_volume': ma_rsi_volume_combo
                })
            }
        except Exception as e:
            stock_logger.error(f"Error in strategic combinations: {e}")
            return {}

    def _analyze_rsi_macd_combination(self, momentum: Dict, trend: Dict) -> Dict[str, Any]:
        """RSI + MACD combination strategy"""
        try:
            rsi = momentum.get('rsi', 50)
            macd_trend = trend.get('macd_trend', 'neutral')
            
            # Strong buy signal
            if rsi < 30 and macd_trend == 'bullish':
                confidence = 85
                return {'signal': 'strong_buy', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'RSI oversold with bullish MACD crossover'}
            
            # Strong sell signal
            elif rsi > 70 and macd_trend == 'bearish':
                confidence = 85
                return {'signal': 'strong_sell', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'RSI overbought with bearish MACD crossover'}
            
            # Moderate signals
            elif rsi < 40 and macd_trend == 'bullish':
                confidence = 65
                return {'signal': 'buy', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'RSI favorable with bullish MACD'}
            
            elif rsi > 60 and macd_trend == 'bearish':
                confidence = 65
                return {'signal': 'sell', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'RSI unfavorable with bearish MACD'}
            
            else:
                confidence = 40
                return {'signal': 'neutral', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'Mixed or neutral RSI/MACD signals'}
                
        except Exception:
            return {'signal': 'neutral', 'confidence': 0, 'score': 0, 'reasoning': 'Error in analysis'}

    def _analyze_bb_rsi_macd_combination(self, volatility: Dict, momentum: Dict, trend: Dict) -> Dict[str, Any]:
        """Bollinger Bands + RSI + MACD combination strategy"""
        try:
            bb_signal = volatility.get('bb_signal', 'neutral')
            rsi = momentum.get('rsi', 50)
            macd_trend = trend.get('macd_trend', 'neutral')
            
            # Mean reversion signals
            if bb_signal == 'oversold' and rsi < 30 and macd_trend != 'bearish':
                confidence = 75
                return {'signal': 'mean_reversion_buy', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'Oversold on both BB and RSI'}
            
            elif bb_signal == 'overbought' and rsi > 70 and macd_trend != 'bullish':
                confidence = 75
                return {'signal': 'mean_reversion_sell', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'Overbought on both BB and RSI'}
            
            else:
                confidence = 45
                return {'signal': 'neutral', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'No clear BB/RSI/MACD convergence'}
                
        except Exception:
            return {'signal': 'neutral', 'confidence': 0, 'score': 0, 'reasoning': 'Error in analysis'}

    def _analyze_ma_rsi_volume_combination(self, ma: Dict, momentum: Dict, volume: Dict) -> Dict[str, Any]:
        """Moving Average + RSI + Volume combination strategy"""
        try:
            sma_trend = ma.get('sma_trend', 'neutral')
            golden_cross = ma.get('golden_cross', False)
            death_cross = ma.get('death_cross', False)
            rsi = momentum.get('rsi', 50)
            volume_signal = volume.get('volume_signal', 'normal')
            
            # Strong trend confirmation with volume
            if golden_cross and rsi > 40 and volume_signal == 'high':
                confidence = 90
                return {'signal': 'strong_trend_buy', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'Golden cross with volume confirmation'}
            
            elif death_cross and rsi < 60 and volume_signal == 'high':
                confidence = 90
                return {'signal': 'strong_trend_sell', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'Death cross with volume confirmation'}
            
            # Trend with RSI confirmation
            elif sma_trend == 'bullish' and rsi < 70 and volume_signal != 'low':
                confidence = 70
                return {'signal': 'trend_buy', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'Bullish trend with favorable RSI and volume'}
            
            elif sma_trend == 'bearish' and rsi > 30 and volume_signal != 'low':
                confidence = 70
                return {'signal': 'trend_sell', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'Bearish trend with unfavorable RSI and volume'}
            
            else:
                confidence = 50
                return {'signal': 'neutral', 'confidence': confidence, 'score': confidence/10, 'reasoning': 'No clear MA/RSI/Volume alignment'}
                
        except Exception:
            return {'signal': 'neutral', 'confidence': 0, 'score': 0, 'reasoning': 'Error in analysis'}

    def _generate_overall_strategic_signal(self, strategies: Dict) -> Dict[str, Any]:
        """Generate overall strategic signal from all combination strategies"""
        try:
            signals = []
            confidences = []
            
            for strategy_name, strategy_data in strategies.items():
                if isinstance(strategy_data, dict) and 'signal' in strategy_data:
                    signal = strategy_data['signal']
                    confidence = strategy_data.get('confidence', 50)
                    
                    # Convert signals to numeric scores
                    if 'buy' in signal:
                        signals.append(1 * (confidence / 100))
                    elif 'sell' in signal:
                        signals.append(-1 * (confidence / 100))
                    else:
                        signals.append(0)
                    
                    confidences.append(confidence)
            
            if not signals:
                return {'signal': 'neutral', 'confidence': 0, 'score': 0, 'reasoning': 'No valid strategy signals'}
            
            # Calculate weighted average signal
            avg_signal = np.mean(signals)
            avg_confidence = np.mean(confidences)
            
            # Determine final signal
            if avg_signal > 0.3:
                final_signal = 'bullish'
            elif avg_signal < -0.3:
                final_signal = 'bearish'
            else:
                final_signal = 'neutral'
            
            return {
                'signal': final_signal,
                'confidence': safe_float(avg_confidence),
                'score': safe_float(avg_confidence/10),
                'signal_strength': safe_float(abs(avg_signal) * 100),
                'strategies_analyzed': len(signals),
                'reasoning': f'Consensus from {len(signals)} strategic combinations'
            }
            
        except Exception:
            return {'signal': 'neutral', 'confidence': 0, 'score': 0, 'reasoning': 'Error in strategic analysis'}

    def calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend indicators (MACD, ADX)"""
        try:
            df_ta = df.copy()
            
            # MACD
            df_ta.ta.macd(fast=12, slow=26, signal=9, append=True)
            
            # ADX (Average Directional Index)
            df_ta.ta.adx(length=14, append=True)
            
            # Parabolic SAR
            df_ta.ta.psar(af=0.02, max_af=0.2, append=True)
            
            macd_val = safe_float(df_ta['MACD_12_26_9'].iloc[-1])
            macd_signal = safe_float(df_ta['MACDs_12_26_9'].iloc[-1])
            adx_val = safe_float(df_ta['ADX_14'].iloc[-1])
            plus_di = safe_float(df_ta['DMP_14'].iloc[-1])
            minus_di = safe_float(df_ta['DMN_14'].iloc[-1])
            
            return {
                'macd': macd_val,
                'macd_signal': macd_signal,
                'macd_histogram': safe_float(df_ta['MACDh_12_26_9'].iloc[-1]),
                'macd_trend': 'bullish' if macd_val > macd_signal else 'bearish',
                'adx': adx_val,
                'adx_strength': 'strong' if adx_val > 25 else 'weak',
                'plus_di': plus_di,
                'minus_di': minus_di,
                'di_trend': 'bullish' if plus_di > minus_di else 'bearish',
                'sar': safe_float(df_ta['PSARl_0.02_0.2'].iloc[-1] or df_ta['PSARs_0.02_0.2'].iloc[-1]),
                'sar_signal': 'bullish' if df['Close'].iloc[-1] > safe_float(df_ta['PSARl_0.02_0.2'].iloc[-1] or df_ta['PSARs_0.02_0.2'].iloc[-1]) else 'bearish'
            }
        except Exception as e:
            stock_logger.error(f"Error calculating trend indicators: {e}")
            return {}
    
    def calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volatility indicators (Bollinger Bands, ATR)"""
        try:
            df_ta = df.copy()
            
            # Bollinger Bands
            df_ta.ta.bbands(length=20, std=2, append=True)
            
            # Average True Range
            df_ta.ta.atr(length=14, append=True)
            
            current_price = safe_float(df['Close'].iloc[-1])
            
            # Handle different possible column names for pandas-ta
            atr_cols = [col for col in df_ta.columns if 'ATR' in col]
            bb_upper_cols = [col for col in df_ta.columns if 'BBU' in col or 'BB_U' in col]
            bb_middle_cols = [col for col in df_ta.columns if 'BBM' in col or 'BB_M' in col]
            bb_lower_cols = [col for col in df_ta.columns if 'BBL' in col or 'BB_L' in col]
            bb_width_cols = [col for col in df_ta.columns if 'BBB' in col or 'BB_W' in col]
            
            # Use the first available column or default values
            atr_val = safe_float(df_ta[atr_cols[0]].iloc[-1]) if atr_cols else 0
            bb_upper = safe_float(df_ta[bb_upper_cols[0]].iloc[-1]) if bb_upper_cols else current_price * 1.02
            bb_middle = safe_float(df_ta[bb_middle_cols[0]].iloc[-1]) if bb_middle_cols else current_price
            bb_lower = safe_float(df_ta[bb_lower_cols[0]].iloc[-1]) if bb_lower_cols else current_price * 0.98
            bb_width = safe_float(df_ta[bb_width_cols[0]].iloc[-1]) if bb_width_cols else bb_upper - bb_lower
            
            bb_position = ((current_price - bb_lower) / (bb_upper - bb_lower)) * 100 if bb_upper > bb_lower else 50
            
            return {
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'bb_position': safe_float(bb_position),
                'bb_signal': 'overbought' if bb_position > 80 else 'oversold' if bb_position < 20 else 'neutral',
                'atr': atr_val,
                'atr_percent': (atr_val / current_price) * 100 if current_price > 0 else 0,
                'volatility': 'high' if (atr_val / current_price) * 100 > 3 else 'low',
                'stddev': bb_width  # Bollinger Band width as volatility measure
            }
        except Exception as e:
            stock_logger.error(f"Error calculating volatility indicators: {e}")
            return {
                'bb_upper': 0, 'bb_middle': 0, 'bb_lower': 0, 'bb_position': 50,
                'bb_signal': 'neutral', 'atr': 0, 'atr_percent': 0,
                'volatility': 'unknown', 'stddev': 0
            }
    
    def calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate volume indicators"""
        try:
            df_ta = df.copy()
            
            # On Balance Volume
            df_ta.ta.obv(append=True)
            
            # Volume SMA - use volume column specifically
            vol_sma = df['Volume'].rolling(window=20).mean()
            
            # Accumulation/Distribution Line
            df_ta.ta.ad(append=True)
            
            # Chaikin Money Flow
            df_ta.ta.cmf(length=20, append=True)
            
            current_volume = safe_float(df['Volume'].iloc[-1])
            avg_volume = safe_float(vol_sma.iloc[-1])
            
            # Find columns dynamically
            obv_cols = [col for col in df_ta.columns if 'OBV' in col]
            ad_cols = [col for col in df_ta.columns if col.startswith('AD') and '_' not in col]
            cmf_cols = [col for col in df_ta.columns if 'CMF' in col]
            
            return {
                'obv': safe_float(df_ta[obv_cols[0]].iloc[-1]) if obv_cols else 0,
                'obv_trend': 'bullish' if obv_cols and len(df_ta[obv_cols[0]]) > 1 and df_ta[obv_cols[0]].iloc[-1] > df_ta[obv_cols[0]].iloc[-2] else 'bearish',
                'volume_sma': avg_volume,
                'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1,
                'volume_signal': 'high' if current_volume > avg_volume * 1.5 else 'low' if current_volume < avg_volume * 0.5 else 'normal',
                'ad_line': safe_float(df_ta[ad_cols[0]].iloc[-1]) if ad_cols else 0,
                'cmf': safe_float(df_ta[cmf_cols[0]].iloc[-1]) if cmf_cols else 0,
                'cmf_signal': 'bullish' if cmf_cols and df_ta[cmf_cols[0]].iloc[-1] > 0.1 else 'bearish' if cmf_cols and df_ta[cmf_cols[0]].iloc[-1] < -0.1 else 'neutral'
            }
        except Exception as e:
            stock_logger.error(f"Error calculating volume indicators: {e}")
            return {
                'obv': 0, 'obv_trend': 'neutral', 'volume_sma': 0, 'volume_ratio': 1,
                'volume_signal': 'normal', 'ad_line': 0, 'cmf': 0, 'cmf_signal': 'neutral'
            }
    
    def calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate support and resistance levels"""
        try:
            high = df['High'].values
            low = df['Low'].values
            close = df['Close'].values
            
            # Pivot Points
            last_high = safe_float(high[-2])  # Previous day's high
            last_low = safe_float(low[-2])    # Previous day's low
            last_close = safe_float(close[-2]) # Previous day's close
            
            pivot = (last_high + last_low + last_close) / 3
            
            # Support and Resistance levels
            r1 = 2 * pivot - last_low
            r2 = pivot + (last_high - last_low)
            r3 = last_high + 2 * (pivot - last_low)
            
            s1 = 2 * pivot - last_high
            s2 = pivot - (last_high - last_low)
            s3 = last_low - 2 * (last_high - pivot)
            
            current_price = safe_float(close[-1])
            
            # Find nearest support and resistance
            resistance_levels = [r1, r2, r3]
            support_levels = [s1, s2, s3]
            
            nearest_resistance = min([r for r in resistance_levels if r > current_price], default=r1)
            nearest_support = max([s for s in support_levels if s < current_price], default=s1)
            
            return {
                'pivot_point': safe_float(pivot),
                'resistance_1': safe_float(r1),
                'resistance_2': safe_float(r2),
                'resistance_3': safe_float(r3),
                'support_1': safe_float(s1),
                'support_2': safe_float(s2),
                'support_3': safe_float(s3),
                'nearest_resistance': safe_float(nearest_resistance),
                'nearest_support': safe_float(nearest_support),
                'distance_to_resistance': ((nearest_resistance - current_price) / current_price) * 100,
                'distance_to_support': ((current_price - nearest_support) / current_price) * 100
            }
        except Exception as e:
            stock_logger.error(f"Error calculating support/resistance: {e}")
            return {}
    
    def analyze_technical_signals(self, df: pd.DataFrame, symbol: str = None) -> Dict[str, Any]:
        """Comprehensive technical analysis combining all indicators"""
        try:
            # Calculate all indicator groups
            ma_signals = self.calculate_moving_averages(df)
            momentum_signals = self.calculate_momentum_indicators(df)
            trend_signals = self.calculate_trend_indicators(df)
            volatility_signals = self.calculate_volatility_indicators(df)
            volume_signals = self.calculate_volume_indicators(df)
            ichimoku_signals = self.calculate_ichimoku_cloud(df)
            pattern_signals = self.calculate_pattern_recognition(df)
            support_resistance = self.calculate_support_resistance(df)
            strategic_combinations = self.calculate_strategic_combinations(df)
            
            # Correlation analysis if symbol provided
            correlation_analysis = {}
            if symbol:
                correlation_analysis = self.calculate_correlation_analysis(df, symbol)
            
            # Enhanced signal scoring with strategic combinations
            bullish_signals = 0
            bearish_signals = 0
            total_signals = 0
            
            # Weight different signal types
            signal_weights = {
                'ma_trend': 2,  # Moving averages get higher weight
                'rsi_signal': 1,
                'macd_trend': 2,
                'adx_di_combination': 1.5,
                'bb_signal': 1,
                'ichimoku_signal': 1.5,
                'strategic_overall': 3  # Strategic combinations get highest weight
            }
            
            # Calculate weighted signals
            for signal_name, weight in signal_weights.items():
                if signal_name == 'ma_trend':
                    if ma_signals.get('sma_trend') == 'bullish':
                        bullish_signals += weight
                    elif ma_signals.get('sma_trend') == 'bearish':
                        bearish_signals += weight
                
                elif signal_name == 'rsi_signal':
                    rsi_signal = momentum_signals.get('rsi_signal')
                    if rsi_signal == 'oversold':
                        bullish_signals += weight
                    elif rsi_signal == 'overbought':
                        bearish_signals += weight
                
                elif signal_name == 'macd_trend':
                    if trend_signals.get('macd_trend') == 'bullish':
                        bullish_signals += weight
                    elif trend_signals.get('macd_trend') == 'bearish':
                        bearish_signals += weight
                
                elif signal_name == 'adx_di_combination':
                    if (trend_signals.get('di_trend') == 'bullish' and 
                        trend_signals.get('adx_strength') == 'strong'):
                        bullish_signals += weight
                    elif (trend_signals.get('di_trend') == 'bearish' and 
                          trend_signals.get('adx_strength') == 'strong'):
                        bearish_signals += weight
                
                elif signal_name == 'bb_signal':
                    bb_signal = volatility_signals.get('bb_signal')
                    if bb_signal == 'oversold':
                        bullish_signals += weight
                    elif bb_signal == 'overbought':
                        bearish_signals += weight
                
                elif signal_name == 'ichimoku_signal':
                    ichimoku_signal = ichimoku_signals.get('ichimoku_signal')
                    if ichimoku_signal == 'bullish':
                        bullish_signals += weight
                    elif ichimoku_signal == 'bearish':
                        bearish_signals += weight
                
                elif signal_name == 'strategic_overall':
                    strategic_signal = strategic_combinations.get('overall_strategic_signal', {}).get('signal')
                    if strategic_signal == 'bullish':
                        bullish_signals += weight
                    elif strategic_signal == 'bearish':
                        bearish_signals += weight
                
                total_signals += weight
            
            # Overall signal determination
            if bullish_signals > bearish_signals:
                overall_signal = 'bullish'
                confidence = (bullish_signals / total_signals) * 100
            elif bearish_signals > bullish_signals:
                overall_signal = 'bearish'
                confidence = (bearish_signals / total_signals) * 100
            else:
                overall_signal = 'neutral'
                confidence = 50
            
            return {
                'overall_signal': overall_signal,
                'confidence': round(confidence, 1),
                'bullish_signals': round(bullish_signals, 1),
                'bearish_signals': round(bearish_signals, 1),
                'total_weighted_signals': round(total_signals, 1),
                'moving_averages': ma_signals,
                'momentum': momentum_signals,
                'trend': trend_signals,
                'volatility': volatility_signals,
                'volume': volume_signals,
                'ichimoku': ichimoku_signals,
                'patterns': pattern_signals,
                'support_resistance': support_resistance,
                'strategic_combinations': strategic_combinations,
                'correlation_analysis': correlation_analysis
            }
            
        except Exception as e:
            stock_logger.error(f"Error in comprehensive technical analysis: {e}")
            return {}


def get_technical_analyzer(benchmark_symbols: List[str] = None) -> TechnicalAnalyzer:
    """Get enhanced TechnicalAnalyzer instance with correlation capabilities"""
    return TechnicalAnalyzer(benchmark_symbols) 