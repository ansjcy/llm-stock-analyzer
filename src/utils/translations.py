"""
Translation module for Chinese language support
Provides translations for all user-facing text in the stock analysis tool
"""

class Translations:
    """Translation class supporting English and Chinese"""
    
    def __init__(self, language='en'):
        self.language = language
        
    def get(self, key: str, **kwargs) -> str:
        """Get translated text for the given key"""
        text = self._get_translation(key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text
    
    def _get_translation(self, key: str) -> str:
        """Internal method to get translation based on current language"""
        translations = {
            'en': self._get_english_translations(),
            'zh': self._get_chinese_translations()
        }
        
        lang_dict = translations.get(self.language, translations['en'])
        return lang_dict.get(key, key)  # Return key as fallback
    
    def _get_english_translations(self) -> dict:
        """English translations (default)"""
        return {
            # Analysis headers
            'stock_analysis_report': 'Stock Analysis Report: {ticker}',
            'analysis_date': 'Analysis Date: {date}',
            'stock_overview': 'Stock Overview',
            'technical_analysis': 'Technical Analysis',
            'recent_news': 'Recent News',
            'ai_generated_insights': 'AI-Generated Insights',
            'investment_recommendation': 'Investment Recommendation',
            'executive_summary': 'Executive Summary',
            'chart_indicators_summary': 'Chart Indicators Summary',
            
            # Stock metrics
            'current_price': 'Current Price',
            'previous_close': 'Previous Close',
            'day_range': 'Day Range',
            '52_week_range': '52-Week Range',
            'market_cap': 'Market Cap',
            'volume': 'Volume',
            'pe_ratio': 'P/E Ratio',
            'beta': 'Beta',
            
            # Technical indicators
            'moving_averages': 'Moving Averages',
            'momentum_indicators': 'Momentum Indicators',
            'trend_indicators': 'Trend Indicators',
            'volatility_indicators': 'Volatility Indicators',
            'volume_indicators': 'Volume Indicators',
            'support_resistance': 'Support & Resistance',
            'correlation_analysis': 'Market Correlation Analysis',
            
            # Technical status
            'trend_bullish': 'bullish',
            'trend_bearish': 'bearish', 
            'trend_neutral': 'neutral',
            'signal_buy': 'BUY',
            'signal_sell': 'SELL',
            'signal_hold': 'HOLD',
            'oversold': 'OVERSOLD',
            'overbought': 'OVERBOUGHT',
            'high_volume': 'HIGH',
            'low_volume': 'LOW',
            'normal_volume': 'NORMAL',
            
            # Chart analysis
            'price_position': 'Price Position',
            'rsi_analysis': 'RSI Analysis',
            'macd_analysis': 'MACD Analysis',
            'volume_analysis': 'Volume Analysis',
            'current_rsi': 'Current RSI',
            'signal': 'Signal',
            'trend': 'Trend',
            'histogram': 'Histogram',
            'vs_average': 'vs Average',
            
            # News section
            'articles_found': 'Articles Found',
            'latest_headlines': 'Latest Headlines',
            'no_headlines_available': 'No headlines available',
            
            # Technical details
            'sma_trend': 'SMA Trend',
            'ema_trend': 'EMA Trend',
            'bollinger_bands': 'Bollinger Bands',
            'rsi_signal': 'RSI Signal',
            'macd_signal': 'MACD Signal',
            'stochastic': 'Stochastic',
            'williams_r': 'Williams %R',
            'cci': 'CCI',
            'atr': 'Average True Range',
            'adx': 'Average Directional Index',
            'ppo': 'Percentage Price Oscillator',
            'roc': 'Rate of Change',
            'mfi': 'Money Flow Index',
            'obv': 'On-Balance Volume',
            'vwap': 'Volume Weighted Average Price',
            'pivot_point': 'Pivot Point',
            'resistance_levels': 'Resistance Levels',
            'support_levels': 'Support Levels',
            
            # Messages
            'generating_charts': 'Generating technical analysis charts...',
            'chart_saved': 'Technical analysis chart saved: {filename}',
            'correlation_chart_saved': 'Correlation chart saved: {filename}',
            'error_generating_charts': 'Error generating charts: {error}',
            'insufficient_data': 'Insufficient historical data for technical analysis',
            'no_data_available': 'No data available',
            'analysis_complete': 'Analysis complete',
            
            # Report sections
            'fundamental_analysis': 'Fundamental Analysis',
            'news_sentiment_analysis': 'News & Sentiment Analysis',
            'diversification_score': 'Diversification Score',
            'beta_vs_sp500': 'Beta (vs S&P 500)',
            'sp500_correlation': 'S&P 500',
            'dow_jones_correlation': 'Dow Jones',
            'nasdaq_correlation': 'NASDAQ',
            
            # File operations
            'report_saved': 'Report saved to: {filename}',
            'error_saving_report': 'Error saving report: {error}',
            
            # Warren Buffett Analysis
            'warren_buffett_analysis': 'Warren Buffett Analysis',
            'fundamental_strength': 'Fundamental Strength',
            'business_consistency': 'Business Consistency',
            'economic_moat': 'Economic Moat',
            'management_quality': 'Management Quality',
            'margin_of_safety': 'Margin of Safety',
            'intrinsic_value': 'Intrinsic Value',
            'valuation_method': 'Valuation Method',
            'overall_signal': 'Overall Signal',
            'confidence_level': 'Confidence Level',
            'quality_score': 'Quality Score',
            'analysis_reliability': 'Analysis Reliability',
            'investment_reasoning': 'Investment Reasoning',
            'buffett_principles': 'Buffett\'s Investment Principles',
            'financial_strength': 'Financial Strength',
            'predictable_earnings': 'Predictable Earnings',
            'competitive_advantage': 'Competitive Advantage',
            'quality_management': 'Quality Management',
            'meets_criteria': 'Meets Criteria',
            'does_not_meet_criteria': 'Does Not Meet Criteria',
            'principles_met': 'Principles Met',
            'overall_assessment': 'Overall Assessment',
            'intrinsic_value_analysis': 'Intrinsic Value Analysis',
            'competitive_advantages': 'Competitive Advantages',
            'moat_strength': 'Moat Strength',
            'undervalued': 'Undervalued',
            'overvalued_fair_value': 'Overvalued or Fair Value',
            'no_investment_reasoning': 'No investment reasoning available',
        }
    
    def _get_chinese_translations(self) -> dict:
        """Chinese translations"""
        return {
            # Analysis headers
            'stock_analysis_report': '股票分析报告：{ticker}',
            'analysis_date': '分析日期：{date}',
            'stock_overview': '股票概览',
            'technical_analysis': '技术分析',
            'recent_news': '最新消息',
            'ai_generated_insights': 'AI生成洞察',
            'investment_recommendation': '投资建议',
            'executive_summary': '执行摘要',
            'chart_indicators_summary': '图表指标摘要',
            
            # Stock metrics
            'current_price': '当前价格',
            'previous_close': '前收盘价',
            'day_range': '日内区间',
            '52_week_range': '52周区间',
            'market_cap': '市值',
            'volume': '成交量',
            'pe_ratio': '市盈率',
            'beta': '贝塔系数',
            
            # Technical indicators
            'moving_averages': '移动平均线',
            'momentum_indicators': '动量指标',
            'trend_indicators': '趋势指标',
            'volatility_indicators': '波动率指标',
            'volume_indicators': '成交量指标',
            'support_resistance': '支撑位与阻力位',
            'correlation_analysis': '市场相关性分析',
            
            # Technical status
            'trend_bullish': '看涨',
            'trend_bearish': '看跌',
            'trend_neutral': '中性',
            'signal_buy': '买入',
            'signal_sell': '卖出',
            'signal_hold': '持有',
            'oversold': '超卖',
            'overbought': '超买',
            'high_volume': '高量',
            'low_volume': '低量',
            'normal_volume': '正常',
            
            # Chart analysis
            'price_position': '价格位置',
            'rsi_analysis': 'RSI分析',
            'macd_analysis': 'MACD分析',
            'volume_analysis': '成交量分析',
            'current_rsi': '当前RSI',
            'signal': '信号',
            'trend': '趋势',
            'histogram': '柱状图',
            'vs_average': '相对均值',
            
            # News section
            'articles_found': '找到文章',
            'latest_headlines': '最新标题',
            'no_headlines_available': '暂无标题',
            
            # Technical details
            'sma_trend': '简单移动平均趋势',
            'ema_trend': '指数移动平均趋势',
            'bollinger_bands': '布林带',
            'rsi_signal': 'RSI信号',
            'macd_signal': 'MACD信号',
            'stochastic': '随机振荡器',
            'williams_r': '威廉指标',
            'cci': '商品通道指数',
            'atr': '平均真实范围',
            'adx': '平均方向指数',
            'ppo': '价格震荡百分比',
            'roc': '变化率',
            'mfi': '资金流量指数',
            'obv': '能量潮',
            'vwap': '成交量加权平均价',
            'pivot_point': '枢轴点',
            'resistance_levels': '阻力位',
            'support_levels': '支撑位',
            
            # Messages
            'generating_charts': '正在生成技术分析图表...',
            'chart_saved': '技术分析图表已保存：{filename}',
            'correlation_chart_saved': '相关性图表已保存：{filename}',
            'error_generating_charts': '生成图表时出错：{error}',
            'insufficient_data': '历史数据不足，无法进行技术分析',
            'no_data_available': '无可用数据',
            'analysis_complete': '分析完成',
            
            # Report sections
            'fundamental_analysis': '基本面分析',
            'news_sentiment_analysis': '新闻情感分析',
            'diversification_score': '多元化评分',
            'beta_vs_sp500': '贝塔系数（相对标普500）',
            'sp500_correlation': '标普500',
            'dow_jones_correlation': '道琼斯',
            'nasdaq_correlation': '纳斯达克',
            
            # File operations
            'report_saved': '报告已保存至：{filename}',
            'error_saving_report': '保存报告时出错：{error}',
            
            # Warren Buffett Analysis
            'warren_buffett_analysis': '沃伦·巴菲特分析',
            'fundamental_strength': '基本面强度',
            'business_consistency': '业务一致性',
            'economic_moat': '经济护城河',
            'management_quality': '管理质量',
            'margin_of_safety': '安全边际',
            'intrinsic_value': '内在价值',
            'valuation_method': '估值方法',
            'overall_signal': '整体信号',
            'confidence_level': '信心水平',
            'quality_score': '质量评分',
            'analysis_reliability': '分析可靠性',
            'investment_reasoning': '投资理由',
            'buffett_principles': '巴菲特的投资原则',
            'financial_strength': '财务实力',
            'predictable_earnings': '可预测收益',
            'competitive_advantage': '竞争优势',
            'quality_management': '质量管理',
            'meets_criteria': '符合标准',
            'does_not_meet_criteria': '不符合标准',
            'principles_met': '原则符合',
            'overall_assessment': '整体评估',
            'intrinsic_value_analysis': '内在价值分析',
            'competitive_advantages': '竞争优势',
            'moat_strength': '护城河强度',
            'undervalued': '被低估',
            'overvalued_fair_value': '被高估或公平价值',
            'no_investment_reasoning': '无可用投资理由',
        }


# Global instance to be used throughout the application
translator = Translations()

def set_language(language: str):
    """Set the global language for translations"""
    global translator
    translator.language = language if language in ['en', 'zh'] else 'en'

def t(key: str, **kwargs) -> str:
    """Convenience function for getting translations"""
    return translator.get(key, **kwargs) 