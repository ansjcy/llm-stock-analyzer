"""
Centralized analysis prompts for LLM stock analysis
"""

import json
from typing import Dict, Any, List


class AnalysisPrompts:
    """Centralized prompts for stock analysis"""

    @staticmethod
    def get_technical_analysis_prompt(ticker: str, technical_data: Dict[str, Any],
                                     stock_info: Dict[str, Any], language: str = 'en') -> Dict[str, str]:
        """Get enhanced technical analysis prompt with comprehensive indicators"""

        if language == 'zh':
            system_prompt = """你是一位专业的技术分析师，精通高级股票市场技术分析。
            你可以访问25+技术指标、策略组合信号、相关性分析和机构级分析工具。
            请基于包括动量、趋势、波动率、成交量、形态识别和相关性指标在内的综合技术数据，提供详细且可操作的见解。"""
        else:
            system_prompt = """You are a professional technical analyst with expertise in advanced stock market technical analysis. 
            You have access to 25+ technical indicators, strategic combination signals, correlation analysis, and institutional-quality analytics. 
            Provide detailed, actionable insights based on comprehensive technical data including momentum, trend, volatility, volume, 
            pattern recognition, and correlation metrics."""

        # Extract key strategic signals for emphasis
        strategies = technical_data.get('strategic_combinations', {})
        correlation_data = technical_data.get('correlation_analysis', {})

        # Get beta from correlation_data or fallback to stock_info
        beta_value = stock_info.get('beta')
        if not beta_value and correlation_data.get('beta'):
            beta_value = correlation_data.get('beta', {}).get('sp500_beta')
        beta_display = f"{beta_value:.3f}" if beta_value and isinstance(beta_value, (int, float)) else '无数据'
        beta_display_en = f"{beta_value:.3f}" if beta_value and isinstance(beta_value, (int, float)) else 'N/A'

        if language == 'zh':
            user_prompt = f"""
            作为专业技术分析师，请为{ticker} ({stock_info.get('name', ticker)})提供全面的技术分析。
            
            当前股票信息：
            - 当前价格：${stock_info.get('current_price', '无数据')}
            - 前收盘价：${stock_info.get('previous_close', '无数据')}
            - 日内区间：${stock_info.get('day_low', '无数据')} - ${stock_info.get('day_high', '无数据')}
            - 成交量：{stock_info.get('volume', '无数据')}
            - 市值：${stock_info.get('market_cap', '无数据')}
            
            综合技术分析数据：
            {json.dumps(technical_data, indent=2, default=str)}
            
            需要重点分析的关键策略信号：
            总体信号：{technical_data.get('overall_signal', 'neutral')} (置信度：{technical_data.get('confidence', 0):.1f}%)
            
            策略组合信号：
            - RSI+MACD策略：{strategies.get('rsi_macd_strategy', {}).get('signal', '无数据')} (评分：{strategies.get('rsi_macd_strategy', {}).get('score', 0):.1f})
            - 布林带+RSI+MACD：{strategies.get('bb_rsi_macd_strategy', {}).get('signal', '无数据')} (评分：{strategies.get('bb_rsi_macd_strategy', {}).get('score', 0):.1f})
            - 移动平均+RSI+成交量：{strategies.get('ma_rsi_volume_strategy', {}).get('signal', '无数据')} (评分：{strategies.get('ma_rsi_volume_strategy', {}).get('score', 0):.1f})
            
            市场相关性分析：
            - 短期标普500相关性: {correlation_data.get('correlations', {}).get('short_term', {}).get('^GSPC', 'N/A')}
            - 中期标普500相关性：{correlation_data.get('correlations', {}).get('medium_term', {}).get('^GSPC', 'N/A')}
            - 长期标普500相关性: {correlation_data.get('correlations', {}).get('long_term', {}).get('^GSPC', 'N/A')}
            - 贝塔系数（系统性风险）：{beta_display}
            - 多元化评分：{correlation_data.get('diversification_score', '无数据')}
            
            请提供涵盖以下内容的详细分析：
            
            1. **策略信号分析**（高优先级）：
               - 解读策略组合信号（RSI+MACD、布林带+RSI+MACD、移动平均+RSI+成交量）
               - 解释加权共识信号和置信度的重要性
               - 评估信号收敛/分歧和可靠性
            
            2. **综合动量分析**：
               - RSI分析，包括超买/超卖状态和背离
               - 随机振荡器（%K、%D）信号和交叉
               - 威廉指标动量和反转信号
               - 变化率（ROC）趋势加速度
               - 资金流量指数（MFI）的成交量加权动量
               - 商品通道指数（CCI）的周期性转折点
            
            3. **高级趋势分析**：
               - MACD信号线交叉、柱状图分析和背离
               - 移动平均分析（SMA/EMA），包括金叉/死叉信号
               - 平均方向指数（ADX）趋势强度评估
               - 一目均衡表分析（所有5条线：转换线、基准线、先行跨度A/B、滞后跨度）
               - 抛物线SAR趋势反转信号
            
            4. **波动率和风险评估**：
               - Bollinger Bands位置和挤压/扩张形态
               - 平均真实范围（ATR）波动率测量
               - 凯尔特纳通道波动率突破
               - 波动率体制分析（增加/减少/稳定）
            
            5. **成交量和智能资金分析**：
               - On-Balance Volume（OBV）积累/分配
               - 积累/分配线智能资金流动
               - Chaikin Money Flow（CMF）买卖压力
               - Volume Price Trend（VPT）成交量调整价格变动
               - Price Volume Oscillator（PVO）成交量动量
               - Ease of Movement（EOM）努力与结果分析
            
            6. **形态识别**：
               - 蜡烛图形态（十字星、锤子线、吊人线、吞没形态）
               - 缺口分析（普通、突破、持续、竭尽缺口）
               - 支撑阻力位识别
               - 图表形态含义
            
            7. **相关性和市场背景**：
               - 解读与主要指数的相关性（标普500、道琼斯、纳斯达克）
               - 贝塔系数系统性风险评估
               - 多元化收益和投资组合含义
               - 市场关系强度和稳定性
            
            8. **风险调整信号**：
               - 信号强度的风险因子调整
               - 基于波动率的仓位规模建议
               - 基于ATR和支撑阻力的止损位
            
            9. **可操作的交易建议**：
               - 具体的入场/出场点位和价格目标
               - 时间框架建议（短期/中期/长期）
               - 风险管理指导原则
               - 信号确认/失效的关键监控位
            
            10. **多时间框架视角**：
                - 短期战术信号与长期战略趋势
                - 不同时间框架间的信号汇合
                - 警告信号和潜在反转指标
            
            请使用清晰的章节标题、具体价位、百分比目标和可操作见解来格式化回应。
            优先考虑策略组合信号，因为它们代表机构级多因子分析。
            包括每个建议的置信度，并解释信号权重背后的推理。
            """
        else:
            user_prompt = f"""
            As a professional technical analyst, provide a comprehensive technical analysis for {ticker} ({stock_info.get('name', ticker)}).
            
            Current Stock Information:
            - Current Price: ${stock_info.get('current_price', 'N/A')}
            - Previous Close: ${stock_info.get('previous_close', 'N/A')}
            - Day Range: ${stock_info.get('day_low', 'N/A')} - ${stock_info.get('day_high', 'N/A')}
            - Volume: {stock_info.get('volume', 'N/A')}
            - Market Cap: ${stock_info.get('market_cap', 'N/A')}
            
            COMPREHENSIVE TECHNICAL ANALYSIS DATA:
            {json.dumps(technical_data, indent=2, default=str)}
            
            KEY STRATEGIC SIGNALS TO EMPHASIZE:
            Overall Signal: {technical_data.get('overall_signal', 'neutral')} (Confidence: {technical_data.get('confidence', 0):.1f}%)
            
            Strategic Combination Signals:
            - RSI+MACD Strategy: {strategies.get('rsi_macd_strategy', {}).get('signal', 'N/A')} (Score: {strategies.get('rsi_macd_strategy', {}).get('score', 0):.1f})
            - Bollinger+RSI+MACD: {strategies.get('bb_rsi_macd_strategy', {}).get('signal', 'N/A')} (Score: {strategies.get('bb_rsi_macd_strategy', {}).get('score', 0):.1f})
            - MA+RSI+Volume: {strategies.get('ma_rsi_volume_strategy', {}).get('signal', 'N/A')} (Score: {strategies.get('ma_rsi_volume_strategy', {}).get('score', 0):.1f})
            
            Market Correlation Analysis:
            - Short term S&P 500 Correlation: {correlation_data.get('correlations', {}).get('short_term', {}).get('^GSPC', 'N/A')}
            - Medium term S&P 500 Correlation: {correlation_data.get('correlations', {}).get('medium_term', {}).get('^GSPC', 'N/A')}
            - Long term S&P 500 Correlation: {correlation_data.get('correlations', {}).get('long_term', {}).get('^GSPC', 'N/A')}
            - Beta (Systematic Risk): {beta_display_en}
            - Diversification Score: {correlation_data.get('diversification_score', 'N/A')}
            
            Please provide a detailed analysis covering:
            
            1. **STRATEGIC SIGNAL ANALYSIS** (High Priority):
               - Interpret the strategic combination signals (RSI+MACD, BB+RSI+MACD, MA+RSI+Volume)
               - Explain the significance of the weighted consensus signal and confidence level
               - Assess signal convergence/divergence and reliability
            
            2. **COMPREHENSIVE MOMENTUM ANALYSIS**:
               - RSI analysis with overbought/oversold conditions and divergences
               - Stochastic Oscillator (%K, %D) signals and crossovers
               - Williams %R momentum and reversal signals
               - Rate of Change (ROC) trend acceleration
               - Money Flow Index (MFI) for volume-weighted momentum
               - Commodity Channel Index (CCI) for cyclical turns
            
            3. **ADVANCED TREND ANALYSIS**:
               - MACD signal line crossovers, histogram analysis, and divergences
               - Moving Average analysis (SMA/EMA) with golden/death cross signals
               - Average Directional Index (ADX) for trend strength assessment
               - Ichimoku Cloud analysis (all 5 lines: Tenkan, Kijun, Senkou A/B, Chikou)
               - Parabolic SAR trend reversal signals
            
            4. **VOLATILITY & RISK ASSESSMENT**:
               - Bollinger Bands position and squeeze/expansion patterns
               - Average True Range (ATR) for volatility measurement
               - Keltner Channels for volatility breakouts
               - Volatility regime analysis (increasing/decreasing/stable)
            
            5. **VOLUME & SMART MONEY ANALYSIS**:
               - On-Balance Volume (OBV) accumulation/distribution
               - Accumulation/Distribution Line smart money flows
               - Chaikin Money Flow (CMF) buying/selling pressure
               - Volume Price Trend (VPT) volume-adjusted price movements
               - Price Volume Oscillator (PVO) volume momentum
               - Ease of Movement (EOM) effort vs. result analysis
            
            6. **PATTERN RECOGNITION**:
               - Candlestick patterns (doji, hammer, hanging man, engulfing patterns)
               - Gap analysis (common, breakaway, runaway, exhaustion gaps)
               - Support and resistance level identification
               - Chart pattern implications
            
            7. **CORRELATION & MARKET CONTEXT**:
               - Interpret correlation with major indices (S&P 500, Dow, NASDAQ)
               - Beta analysis for systematic risk assessment
               - Diversification benefits and portfolio implications
               - Market relationship strength and stability
            
            8. **RISK-ADJUSTED SIGNALS**:
               - Risk factor adjustments to signal strength
               - Volatility-adjusted position sizing recommendations
               - Stop-loss levels based on ATR and support/resistance
            
            9. **ACTIONABLE TRADING RECOMMENDATIONS**:
               - Specific entry/exit points with price targets
               - Time horizon recommendations (short/medium/long term)
               - Risk management guidelines
               - Key levels to monitor for signal confirmation/invalidation
            
            10. **MULTI-TIMEFRAME PERSPECTIVE**:
                - Short-term tactical signals vs. long-term strategic trends
                - Confluence of signals across different timeframes
                - Warning signs and potential reversal indicators
            
            Format the response with clear section headers, specific price levels, percentage targets, and actionable insights. 
            Prioritize the strategic combination signals as they represent institutional-quality multi-factor analysis.
            Include confidence levels for each recommendation and explain the reasoning behind signal weights.
            """

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    @staticmethod
    def get_fundamental_analysis_prompt(ticker: str, stock_info: Dict[str, Any],
                                       financial_data: Dict[str, Any], language: str = 'en') -> Dict[str, str]:
        """Get fundamental analysis prompt"""

        if language == 'zh':
            system_prompt = "你是一位专业的基本面分析师，精通财务报表分析和估值。请基于数据提供全面、客观的投资见解，并在相关时结合技术信号。"

            user_prompt = f"""
            作为专业基本面分析师，请为{ticker} ({stock_info.get('name', ticker)})提供全面的基本面分析。
            
            公司信息：
            - 行业板块：{stock_info.get('sector', '无数据')}
            - 细分行业：{stock_info.get('industry', '无数据')}
            - 市值：${stock_info.get('market_cap', '无数据')}
            - 当前价格：${stock_info.get('current_price', '无数据')}
            - 员工数量：{stock_info.get('full_time_employees', '无数据')}
            
            关键财务指标：
            - 市盈率：{stock_info.get('pe_ratio', '无数据')}
            - 预期市盈率：{stock_info.get('forward_pe', '无数据')}
            - PEG比率：{stock_info.get('peg_ratio', '无数据')}
            - 市净率：{stock_info.get('price_to_book', '无数据')}
            - 市销率：{stock_info.get('price_to_sales', '无数据')}
            - 企业价值/EBITDA：{stock_info.get('enterprise_to_ebitda', '无数据')}
            - 负债权益比：{stock_info.get('debt_to_equity', '无数据')}
            - 流动比率：{stock_info.get('current_ratio', '无数据')}
            - 速动比率：{stock_info.get('quick_ratio', '无数据')}
            - 净资产收益率：{stock_info.get('return_on_equity', '无数据')}%
            - 总资产收益率：{stock_info.get('return_on_assets', '无数据')}%
            - 毛利率：{stock_info.get('gross_margins', '无数据')}%
            - 营业利润率：{stock_info.get('operating_margins', '无数据')}%
            - 净利润率：{stock_info.get('profit_margins', '无数据')}%
            - 营收增长率：{stock_info.get('revenue_growth', '无数据')}%
            - 盈利增长率：{stock_info.get('earnings_growth', '无数据')}%
            - 自由现金流：{stock_info.get('free_cash_flow', '无数据')}
            - 股息收益率：{stock_info.get('dividend_yield', '无数据')}%
            - 派息比率：{stock_info.get('payout_ratio', '无数据')}%
            - 贝塔系数：{stock_info.get('beta', '无数据')}
            
            请提供涵盖以下内容的详细分析：
            1. **估值评估**：
               - 股票是被高估、低估还是合理估值？
               - 将市盈率、PEG、市净率与行业和历史平均值比较
               - 企业价值分析和EBITDA倍数
               - 现金流贴现（DCF）考虑因素
            
            2. **财务健康状况和流动性**：
               - 资产负债表强度和债务管理
               - 流动比率和速动比率分析
               - 现金流稳定性和自由现金流产生能力
               - 营运资本管理效率
            
            3. **盈利能力指标和趋势**：
               - ROE、ROA分析和同行比较
               - 利润率分析（毛利率、营业利润率、净利润率）和趋势
               - 资产利用率和运营效率
               - 盈利质量评估
            
            4. **增长前景和可持续性**：
               - 营收和盈利增长的可持续性
               - 市场扩张机会
               - 竞争优势和护城河分析
               - 管理层执行力和资本配置
            
            5. **资本结构和股东回报**：
               - 债务水平和资本结构优化
               - 股息政策可持续性和增长潜力
               - 股票回购计划和股东价值创造
               - 利息覆盖率和财务灵活性
            
            6. **竞争地位和行业分析**：
               - 市场份额和竞争优势
               - 行业增长趋势和周期性
               - 监管环境和风险
               - 技术颠覆威胁/机遇
            
            请使用具体数据和可比分析，提供明确的买入/持有/卖出建议和目标价位。
            """
        else:
            system_prompt = "You are a professional fundamental analyst with expertise in financial statement analysis and valuation. Provide thorough, data-driven investment insights with correlation to technical signals when relevant."

            user_prompt = f"""
            As a professional fundamental analyst, provide a comprehensive fundamental analysis for {ticker} ({stock_info.get('name', ticker)}).
            
            Company Information:
            - Sector: {stock_info.get('sector', 'N/A')}
            - Industry: {stock_info.get('industry', 'N/A')}
            - Market Cap: ${stock_info.get('market_cap', 'N/A')}
            - Current Price: ${stock_info.get('current_price', 'N/A')}
            - Employee Count: {stock_info.get('full_time_employees', 'N/A')}
            
            Key Financial Metrics:
            - P/E Ratio: {stock_info.get('pe_ratio', 'N/A')}
            - Forward P/E: {stock_info.get('forward_pe', 'N/A')}
            - PEG Ratio: {stock_info.get('peg_ratio', 'N/A')}
            - Price to Book: {stock_info.get('price_to_book', 'N/A')}
            - Price to Sales: {stock_info.get('price_to_sales', 'N/A')}
            - Enterprise Value/EBITDA: {stock_info.get('enterprise_to_ebitda', 'N/A')}
            - Debt to Equity: {stock_info.get('debt_to_equity', 'N/A')}
            - Current Ratio: {stock_info.get('current_ratio', 'N/A')}
            - Quick Ratio: {stock_info.get('quick_ratio', 'N/A')}
            - ROE: {stock_info.get('return_on_equity', 'N/A')}%
            - ROA: {stock_info.get('return_on_assets', 'N/A')}%
            - Gross Margin: {stock_info.get('gross_margins', 'N/A')}%
            - Operating Margin: {stock_info.get('operating_margins', 'N/A')}%
            - Profit Margin: {stock_info.get('profit_margins', 'N/A')}%
            - Revenue Growth: {stock_info.get('revenue_growth', 'N/A')}%
            - Earnings Growth: {stock_info.get('earnings_growth', 'N/A')}%
            - Free Cash Flow: {stock_info.get('free_cash_flow', 'N/A')}
            - Dividend Yield: {stock_info.get('dividend_yield', 'N/A')}%
            - Payout Ratio: {stock_info.get('payout_ratio', 'N/A')}%
            - Beta: {stock_info.get('beta', 'N/A')}
            
            Please provide a detailed analysis covering:
            1. **VALUATION ASSESSMENT**:
               - Is the stock overvalued, undervalued, or fairly valued?
               - Compare P/E, PEG, P/B ratios to industry and historical averages
               - Enterprise value analysis and EBITDA multiples
               - Discounted Cash Flow (DCF) considerations
            
            2. **FINANCIAL HEALTH & LIQUIDITY**:
               - Balance sheet strength and debt management
               - Current and quick ratio analysis
               - Cash flow stability and free cash flow generation
               - Working capital management efficiency
            
            3. **PROFITABILITY METRICS & TRENDS**:
               - ROE, ROA analysis and peer comparison
               - Margin analysis (gross, operating, net) and trends
               - Asset utilization and operational efficiency
               - Earnings quality assessment
            
            4. **GROWTH PROSPECTS & SUSTAINABILITY**:
               - Revenue and earnings growth sustainability
               - Market expansion opportunities
               - Competitive advantages and moat analysis
               - Management execution and capital allocation
            
            5. **CAPITAL STRUCTURE & SHAREHOLDER RETURNS**:
               - Debt levels and capital structure optimization
               - Dividend policy sustainability and growth potential
               - Share buyback programs and shareholder value creation
               - Interest coverage and financial flexibility
            
            6. **COMPETITIVE POSITION & INDUSTRY ANALYSIS**:
               - Market share and competitive advantages
               - Industry growth trends and cyclicality
               - Regulatory environment and risks
               - Technological disruption threats/opportunities
            
            Provide specific data-driven insights with clear buy/hold/sell recommendation and target price ranges.
            """

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    @staticmethod
    def get_news_analysis_prompt(ticker: str, news_articles: List[Dict[str, Any]],
                                stock_info: Dict[str, Any], language: str = 'en') -> Dict[str, str]:
        """Get news analysis prompt"""

        if language == 'zh':
            system_prompt = "你是一位专业的新闻情感分析师，专门分析新闻对股价的影响。请提供客观、平衡的分析，考虑短期和长期影响。"

            articles_text = ""
            if news_articles:
                articles_text = "\n".join([f"标题: {article.get('title', '无标题')}\n发布时间: {article.get('published', '无时间')}\n摘要: {article.get('summary', '无摘要')[:500]}...\n" for article in news_articles[:10]])
            else:
                articles_text = "当前无可用新闻文章。"

            user_prompt = f"""
            作为专业新闻情感分析师，请分析影响{ticker} ({stock_info.get('name', ticker)})的最新新闻。
            
            公司信息：
            - 当前价格：${stock_info.get('current_price', '无数据')}
            - 市值：${stock_info.get('market_cap', '无数据')}
            - 行业板块：{stock_info.get('sector', '无数据')}
            
            最新新闻文章：
            {articles_text}
            
            请提供涵盖以下内容的详细分析：
            
            1. **整体情感评估**：
               - 新闻情感是正面、负面还是中性？
               - 情感强度（1-10级）
               - 市场反应预期
            
            2. **关键主题分析**：
               - 识别主要新闻主题（财报、产品发布、监管变化、管理层变动等）
               - 每个主题的重要性和潜在影响
               - 行业相关性和同行影响
            
            3. **短期影响评估**：
               - 预期的即时股价反应
               - 交易量和波动性影响
               - 技术位的潜在突破或支撑
            
            4. **长期影响分析**：
               - 对公司基本面的持续影响
               - 竞争地位变化
               - 估值影响和目标价调整
            
            5. **风险因子识别**：
               - 关键风险和不确定性
               - 监管或法律风险
               - 运营和财务风险
            
            6. **投资者情绪指标**：
               - 机构vs散户情绪
               - 分析师评级变化预期
               - 社交媒体情绪趋势
            
            请提供明确的情感评分（1-10）和具体的投资建议。
            """
        else:
            system_prompt = "You are a professional news sentiment analyst specializing in the impact of news on stock prices. Provide objective, balanced analysis considering both short-term and long-term implications."

            articles_text = ""
            if news_articles:
                articles_text = "\n".join([f"Title: {article.get('title', 'No title')}\nPublished: {article.get('published', 'No date')}\nSummary: {article.get('summary', 'No summary')[:500]}...\n" for article in news_articles[:10]])
            else:
                articles_text = "No news articles available."

            user_prompt = f"""
            As a professional news sentiment analyst, analyze the recent news affecting {ticker} ({stock_info.get('name', ticker)}).
            
            Company Information:
            - Current Price: ${stock_info.get('current_price', 'N/A')}
            - Market Cap: ${stock_info.get('market_cap', 'N/A')}
            - Sector: {stock_info.get('sector', 'N/A')}
            
            Recent News Articles:
            {articles_text}
            
            Please provide a detailed analysis covering:
            
            1. **OVERALL SENTIMENT ASSESSMENT**:
               - Is the news sentiment positive, negative, or neutral?
               - Sentiment intensity (scale 1-10)
               - Expected market reaction
            
            2. **KEY THEMES ANALYSIS**:
               - Identify major news themes (earnings, product launches, regulatory changes, management changes, etc.)
               - Importance and potential impact of each theme
               - Industry relevance and peer effects
            
            3. **SHORT-TERM IMPACT ASSESSMENT**:
               - Expected immediate stock price reaction
               - Volume and volatility implications
               - Potential technical level breaks or support
            
            4. **LONG-TERM IMPACT ANALYSIS**:
               - Lasting effects on company fundamentals
               - Competitive position changes
               - Valuation impact and price target adjustments
            
            5. **RISK FACTOR IDENTIFICATION**:
               - Key risks and uncertainties
               - Regulatory or legal risks
               - Operational and financial risks
            
            6. **INVESTOR SENTIMENT INDICATORS**:
               - Institutional vs. retail sentiment
               - Expected analyst rating changes
               - Social media sentiment trends
            
            Provide a clear sentiment score (1-10) and specific investment implications.
            """

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    @staticmethod
    def get_investment_recommendation_prompt(ticker: str, stock_info: Dict[str, Any],
                                           technical_analysis: str, fundamental_analysis: str,
                                           news_analysis: str, language: str = 'en') -> Dict[str, str]:
        """Get investment recommendation prompt"""

        if language == 'zh':
            system_prompt = "你是一位资深投资顾问，整合技术分析、基本面分析和新闻情感分析，为客户提供全面的投资建议。请基于多维度分析提供明确、可操作的投资建议。"

            user_prompt = f"""
            作为资深投资顾问，请基于综合分析为{ticker} ({stock_info.get('name', ticker)})提供投资建议。
            
            当前股票信息：
            - 当前价格：${stock_info.get('current_price', '无数据')}
            - 市值：${stock_info.get('market_cap', '无数据')}
            - 行业板块：{stock_info.get('sector', '无数据')}
            - 贝塔系数：{stock_info.get('beta', '无数据')}
            
            技术分析摘要：
            {technical_analysis}
            
            基本面分析摘要：
            {fundamental_analysis}
            
            新闻情感分析摘要：
            {news_analysis}
            
            请提供包含以下内容的综合投资建议：
            
            1. **投资建议**（明确选择）：
               - 强烈买入/买入/持有/卖出/强烈卖出
               - 建议理由和关键支撑因素
               - 风险调整后的预期回报
            
            2. **目标价位和时间框架**：
               - 6个月目标价
               - 12个月目标价
               - 上行/下行风险比率
               - 止损建议位
            
            3. **投资逻辑总结**：
               - 技术面、基本面、情感面的权重分配
               - 主要驱动因素优先级
               - 关键催化剂和风险因素
            
            4. **仓位建议**：
               - 建议的投资组合权重
               - 分批建仓策略
               - 风险管理指导
            
            5. **监控指标**：
               - 需要密切关注的关键指标
               - 改变投资观点的触发条件
               - 重要的财报和事件日期
            
            6. **风险披露**：
               - 主要投资风险
               - 情景分析（乐观/基准/悲观）
               - 适合的投资者类型
            
            请提供明确的数字目标和具体的操作建议。
            """
        else:
            system_prompt = "You are a senior investment advisor who synthesizes technical analysis, fundamental analysis, and news sentiment to provide comprehensive investment recommendations. Provide clear, actionable investment advice based on multi-dimensional analysis."

            user_prompt = f"""
            As a senior investment advisor, provide a comprehensive investment recommendation for {ticker} ({stock_info.get('name', ticker)}) based on the integrated analysis.
            
            Current Stock Information:
            - Current Price: ${stock_info.get('current_price', 'N/A')}
            - Market Cap: ${stock_info.get('market_cap', 'N/A')}
            - Sector: {stock_info.get('sector', 'N/A')}
            - Beta: {stock_info.get('beta', 'N/A')}
            
            Technical Analysis Summary:
            {technical_analysis}
            
            Fundamental Analysis Summary:
            {fundamental_analysis}
            
            News Sentiment Analysis Summary:
            {news_analysis}
            
            Please provide a comprehensive investment recommendation covering:
            
            1. **INVESTMENT RECOMMENDATION** (Clear Choice):
               - Strong Buy/Buy/Hold/Sell/Strong Sell
               - Rationale and key supporting factors
               - Risk-adjusted expected returns
            
            2. **PRICE TARGETS & TIMEFRAMES**:
               - 6-month price target
               - 12-month price target
               - Upside/downside risk ratio
               - Stop-loss recommendations
            
            3. **INVESTMENT THESIS SUMMARY**:
               - Weighting of technical, fundamental, and sentiment factors
               - Primary catalyst priorities
               - Key catalysts and risk factors
            
            4. **POSITION SIZING RECOMMENDATIONS**:
               - Suggested portfolio weight
               - Dollar-cost averaging strategy
               - Risk management guidelines
            
            5. **MONITORING METRICS**:
               - Key indicators to watch closely
               - Triggers for changing investment view
               - Important earnings and event dates
            
            6. **RISK DISCLOSURES**:
               - Primary investment risks
               - Scenario analysis (bull/base/bear cases)
               - Suitable investor types
            
            Provide specific numerical targets and concrete actionable recommendations.
            """

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    @staticmethod
    def get_summary_prompt(ticker: str, stock_info: Dict[str, Any],
                          technical_summary: str, fundamental_summary: str,
                          news_summary: str, recommendation: str, language: str = 'en') -> Dict[str, str]:
        """Get executive summary prompt"""

        if language == 'zh':
            system_prompt = """你是一位经验丰富的投资顾问，能够将复杂的股票分析综合成清晰简洁的执行摘要。
            你的摘要应该平衡技术和基本面因素，同时考虑新闻情绪和市场条件。"""

            user_prompt = f"""
            请为{ticker} ({stock_info.get('name', ticker)})提供执行摘要，基于以下分析：
            
            技术分析：
            {technical_summary}
            
            基本面分析：
            {fundamental_summary}
            
            新闻分析：
            {news_summary}
            
            投资建议：
            {recommendation}
            
            请提供一个简洁的执行摘要，包括：
            - 关键要点和机会
            - 主要风险和关注点
            - 总体投资前景
            - 具体的行动项目
            
            保持摘要在500字以内，并使用要点格式。
            """
        else:
            system_prompt = """You are an experienced investment advisor who synthesizes complex stock analysis into clear, 
            actionable executive summaries. Your summaries should balance technical and fundamental factors while considering 
            news sentiment and market conditions."""

            user_prompt = f"""
            Please provide an executive summary for {ticker} ({stock_info.get('name', ticker)}) based on the following analysis:
            
            Technical Analysis:
            {technical_summary}
            
            Fundamental Analysis:
            {fundamental_summary}
            
            News Analysis:
            {news_summary}
            
            Investment Recommendation:
            {recommendation}
            
            Please provide a concise executive summary that includes:
            - Key highlights and opportunities
            - Main risks and concerns
            - Overall investment outlook
            - Specific action items
            
            Keep the summary under 500 words and use bullet points for clarity.
            """

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    @staticmethod
    def get_warren_buffett_analysis_prompt(ticker: str, warren_buffett_data: Dict[str, Any],
                                         stock_info: Dict[str, Any], language: str = 'en') -> Dict[str, str]:
        """Get Warren Buffett style analysis prompt"""

        if language == 'zh':
            system_prompt = """你是沃伦·巴菲特，这位传奇的价值投资者。根据巴菲特的投资原则进行分析：
            - 能力圈：只投资于你理解的企业
            - 安全边际（>30%）：以相对于内在价值的显著折扣价买入
            - 经济护城河：寻找持久的竞争优势
            - 优质管理层：寻求保守的、以股东为导向的团队
            - 财务实力：偏好低负债、强劲的股本回报率
            - 长期视野：投资企业而非股票
            - 只有在基本面恶化或估值远超内在价值时才卖出

            当提供推理时，要彻底和具体：
            1. 解释最影响你决定的关键因素（积极和消极的）
            2. 强调公司如何符合或违背特定的巴菲特原则
            3. 在相关的地方提供定量证据（如具体利润率、ROE值、负债水平）
            4. 以巴菲特式的投资机会评估结束
            5. 在解释中使用沃伦·巴菲特的语调和对话风格

            例如，如果看涨："我对[具体优势]特别印象深刻，这让我想起了我们早期对喜诗糖果的投资，我们在那里看到了[类似属性]..."
            例如，如果看跌："资本回报率下降让我想起了伯克希尔的纺织业务，我们最终退出了，因为..."

            严格遵循这些准则。"""

            user_prompt = f"""基于以下数据，以沃伦·巴菲特的方式创建对{ticker}的投资分析：
            
             公司信息：
            - 公司名称：{stock_info.get('name', ticker)}
            - 行业板块：{stock_info.get('sector', '无数据')}
            - 细分行业：{stock_info.get('industry', '无数据')}
            - 市值：${stock_info.get('market_cap', '无数据')}
            - 当前价格：${stock_info.get('current_price', '无数据')}
            - 员工数量：{stock_info.get('full_time_employees', '无数据')}
            
            关键财务指标：
            - 市盈率：{stock_info.get('pe_ratio', '无数据')}
            - 预期市盈率：{stock_info.get('forward_pe', '无数据')}
            - PEG比率：{stock_info.get('peg_ratio', '无数据')}
            - 市净率：{stock_info.get('price_to_book', '无数据')}
            - 市销率：{stock_info.get('price_to_sales', '无数据')}
            - 企业价值/EBITDA：{stock_info.get('enterprise_to_ebitda', '无数据')}
            - 负债权益比：{stock_info.get('debt_to_equity', '无数据')}
            - 流动比率：{stock_info.get('current_ratio', '无数据')}
            - 速动比率：{stock_info.get('quick_ratio', '无数据')}
            - 净资产收益率：{stock_info.get('return_on_equity', '无数据')}%
            - 总资产收益率：{stock_info.get('return_on_assets', '无数据')}%
            - 毛利率：{stock_info.get('gross_margins', '无数据')}%
            - 营业利润率：{stock_info.get('operating_margins', '无数据')}%
            - 净利润率：{stock_info.get('profit_margins', '无数据')}%
            - 营收增长率：{stock_info.get('revenue_growth', '无数据')}%
            - 盈利增长率：{stock_info.get('earnings_growth', '无数据')}%
            - 自由现金流：{stock_info.get('free_cash_flow', '无数据')}
            - 股息收益率：{stock_info.get('dividend_yield', '无数据')}%
            - 派息比率：{stock_info.get('payout_ratio', '无数据')}%
            - 贝塔系数：{stock_info.get('beta', '无数据')}

            沃伦·巴菲特分析数据：
            {json.dumps(warren_buffett_data, indent=2, ensure_ascii=False, default=str)}

            请提供一个深入的巴菲特式分析，涵盖：

            1. **投资信号总结**
               - 总体投资决定：{warren_buffett_data.get('overall_signal', '中性')} (置信度：{warren_buffett_data.get('confidence', 0):.1f}%)
               - 质量评分：{warren_buffett_data.get('score_percentage', 0):.1f}%
               - 安全边际：{f"{warren_buffett_data.get('margin_of_safety', 0):.1%}" if warren_buffett_data.get('margin_of_safety') is not None else "无数据"}

            2. **巴菲特原则评估**
               - 分析公司如何符合每个核心巴菲特原则
               - 重点关注财务实力、收益一致性、经济护城河和管理质量

            3. **财务实力分析**
               - 解读ROE、负债水平、利润率和流动性
               - 比较这些指标与巴菲特的标准

            4. **经济护城河评估**
               - 评估公司的竞争优势和定价权
               - 讨论护城河的可持续性

            5. **管理质量**
               - 评估股东友好的资本配置决策
               - 分析股票回购、股息和资本效率

            6. **内在价值和安全边际**
               - 讨论内在价值计算方法和假设
               - 评估当前价格相对于计算出的内在价值

            7. **巴菲特式的最终判断**
               - 用巴菲特的声音和风格提供最终的投资论点
               - 包括具体的推理和类比他过去的投资

            请使用巴菲特标志性的智慧、清晰度和实用方法。包括具体的数字和明确的推理。"""
        else:
            system_prompt = """You are Warren Buffett, the legendary value investor. Analyze based on Buffett's investment principles:
            - Circle of Competence: Only invest in businesses you understand
            - Margin of Safety (>30%): Buy at a significant discount to intrinsic value
            - Economic Moat: Look for durable competitive advantages
            - Quality Management: Seek conservative, shareholder-oriented teams
            - Financial Strength: Favor low debt, strong returns on equity
            - Long-term Horizon: Invest in businesses, not just stocks
            - Sell only if fundamentals deteriorate or valuation far exceeds intrinsic value

            When providing your reasoning, be thorough and specific by:
            1. Explaining the key factors that influenced your decision the most (both positive and negative)
            2. Highlighting how the company aligns with or violates specific Buffett principles
            3. Providing quantitative evidence where relevant (e.g., specific margins, ROE values, debt levels)
            4. Concluding with a Buffett-style assessment of the investment opportunity
            5. Using Warren Buffett's voice and conversational style in your explanation

            For example, if bullish: "I'm particularly impressed with [specific strength], reminiscent of our early investment in See's Candies where we saw [similar attribute]..."
            For example, if bearish: "The declining returns on capital remind me of the textile operations at Berkshire that we eventually exited because..."

            Follow these guidelines strictly."""

            user_prompt = f"""Based on the following data, create an investment analysis for {ticker} as Warren Buffett would:
            
            Company Information:
            - Company Name: {stock_info.get('name', ticker)}
            - Sector: {stock_info.get('sector', 'N/A')}
            - Industry: {stock_info.get('industry', 'N/A')}
            - Market Cap: ${stock_info.get('market_cap', 'N/A')}
            - Current Price: ${stock_info.get('current_price', 'N/A')}
            - Employee Count: {stock_info.get('full_time_employees', 'N/A')}
            
            Key Financial Metrics:
            - P/E Ratio: {stock_info.get('pe_ratio', 'N/A')}
            - Forward P/E: {stock_info.get('forward_pe', 'N/A')}
            - PEG Ratio: {stock_info.get('peg_ratio', 'N/A')}
            - Price to Book: {stock_info.get('price_to_book', 'N/A')}
            - Price to Sales: {stock_info.get('price_to_sales', 'N/A')}
            - Enterprise Value/EBITDA: {stock_info.get('enterprise_to_ebitda', 'N/A')}
            - Debt to Equity: {stock_info.get('debt_to_equity', 'N/A')}
            - Current Ratio: {stock_info.get('current_ratio', 'N/A')}
            - Quick Ratio: {stock_info.get('quick_ratio', 'N/A')}
            - ROE: {stock_info.get('return_on_equity', 'N/A')}%
            - ROA: {stock_info.get('return_on_assets', 'N/A')}%
            - Gross Margin: {stock_info.get('gross_margins', 'N/A')}%
            - Operating Margin: {stock_info.get('operating_margins', 'N/A')}%
            - Profit Margin: {stock_info.get('profit_margins', 'N/A')}%
            - Revenue Growth: {stock_info.get('revenue_growth', 'N/A')}%
            - Earnings Growth: {stock_info.get('earnings_growth', 'N/A')}%
            - Free Cash Flow: {stock_info.get('free_cash_flow', 'N/A')}
            - Dividend Yield: {stock_info.get('dividend_yield', 'N/A')}%
            - Payout Ratio: {stock_info.get('payout_ratio', 'N/A')}%
            - Beta: {stock_info.get('beta', 'N/A')}

            Warren Buffett Analysis Data:
            {json.dumps(warren_buffett_data, indent=2, default=str)}

            Please provide an in-depth Buffett-style analysis covering:

            1. **Investment Signal Summary**
               - Overall investment decision: {warren_buffett_data.get('overall_signal', 'neutral')} (Confidence: {warren_buffett_data.get('confidence', 0):.1f}%)
               - Quality Score: {warren_buffett_data.get('score_percentage', 0):.1f}%
               - Margin of Safety: {f"{warren_buffett_data.get('margin_of_safety', 0):.1%}" if warren_buffett_data.get('margin_of_safety') is not None else "N/A"}

            2. **Buffett Principles Assessment**
               - Analyze how the company aligns with each core Buffett principle
               - Focus on financial strength, earnings consistency, economic moat, and management quality

            3. **Financial Strength Analysis**
               - Interpret the ROE, debt levels, margins, and liquidity ratios
               - Compare these metrics to Buffett's standards

            4. **Economic Moat Assessment**
               - Evaluate the company's competitive advantages and pricing power
               - Discuss the sustainability of the moat

            5. **Management Quality**
               - Assess shareholder-friendly capital allocation decisions
               - Analyze share buybacks, dividends, and capital efficiency

            6. **Intrinsic Value and Margin of Safety**
               - Discuss the intrinsic value calculation methodology and assumptions
               - Evaluate current price relative to calculated intrinsic value

            7. **Buffett-Style Final Verdict**
               - Provide your final investment thesis in Buffett's voice and style
               - Include specific reasoning and analogies to his past investments

            Please use Buffett's signature wisdom, clarity, and practical approach. Include specific numbers and clear reasoning."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }

    @staticmethod
    def get_peter_lynch_analysis_prompt(ticker: str, peter_lynch_data: Dict[str, Any],
                                      stock_info: Dict[str, Any], language: str = 'en') -> Dict[str, str]:
        """Get Peter Lynch style analysis prompt"""

        if language == 'zh':
            system_prompt = """你是彼得·林奇，传奇的成长型投资者和前富达麦哲伦基金经理。根据林奇的投资原则进行分析：
            - 投资你了解的公司：专注于你能理解的企业和产品
            - 合理价格增长(GARP)：PEG比率 < 1.0 是关键指标
            - 盈利增长：寻找15-30%的年盈利增长率
            - 简单的商业模式：避免复杂的金融工程或难以理解的业务
            - 中型股偏好：$2B-$50B市值范围内的公司
            - 一致的增长：稳定、可预测的收入和盈利增长
            - 强劲的基本面：良好的ROE、可管理的债务、正现金流
            - 盈利加速：寻找盈利增长加速的迹象

            当提供推理时，要详细和具体：
            1. 强调PEG比率和增长指标作为主要决策因素
            2. 解释公司如何符合或违背GARP原则
            3. 评估业务的可理解性和简单性
            4. 提供具体的增长数据和趋势分析
            5. 使用彼得·林奇的直接、实用和投资者友好的语调

            例如，如果看涨："这家公司让我想起了我在富达时发现的那些优秀的增长股。PEG比率0.8显示了以合理价格获得增长的经典机会，而连续的盈利加速表明..."
            例如，如果看跌："虽然这是一个有趣的故事，但PEG比率2.5表明投资者为增长付出了过高的价格。我更愿意等待更好的入场点或寻找..."

            严格遵循这些准则。"""

            user_prompt = f"""基于以下数据，以彼得·林奇的方式创建对{ticker}的投资分析：
            
            公司信息：
            - 公司名称：{stock_info.get('name', ticker)}
            - 行业板块：{stock_info.get('sector', '无数据')}
            - 细分行业：{stock_info.get('industry', '无数据')}
            - 市值：${stock_info.get('market_cap', '无数据')}
            - 当前价格：${stock_info.get('current_price', '无数据')}
            - 员工数量：{stock_info.get('full_time_employees', '无数据')}
            
            关键财务指标：
            - 市盈率：{stock_info.get('pe_ratio', '无数据')}
            - 预期市盈率：{stock_info.get('forward_pe', '无数据')}
            - PEG比率：{stock_info.get('peg_ratio', '无数据')}
            - 市净率：{stock_info.get('price_to_book', '无数据')}
            - 市销率：{stock_info.get('price_to_sales', '无数据')}
            - 企业价值/EBITDA：{stock_info.get('enterprise_to_ebitda', '无数据')}
            - 负债权益比：{stock_info.get('debt_to_equity', '无数据')}
            - 流动比率：{stock_info.get('current_ratio', '无数据')}
            - 速动比率：{stock_info.get('quick_ratio', '无数据')}
            - 净资产收益率：{stock_info.get('return_on_equity', '无数据')}%
            - 总资产收益率：{stock_info.get('return_on_assets', '无数据')}%
            - 毛利率：{stock_info.get('gross_margins', '无数据')}%
            - 营业利润率：{stock_info.get('operating_margins', '无数据')}%
            - 净利润率：{stock_info.get('profit_margins', '无数据')}%
            - 营收增长率：{stock_info.get('revenue_growth', '无数据')}%
            - 盈利增长率：{stock_info.get('earnings_growth', '无数据')}%
            - 自由现金流：{stock_info.get('free_cash_flow', '无数据')}
            - 股息收益率：{stock_info.get('dividend_yield', '无数据')}%
            - 派息比率：{stock_info.get('payout_ratio', '无数据')}%
            - 贝塔系数：{stock_info.get('beta', '无数据')}

            彼得·林奇分析数据：
            {json.dumps(peter_lynch_data, indent=2, ensure_ascii=False, default=str)}

            请提供一个深入的林奇式分析，涵盖：

            1. **投资信号总结**
               - 总体投资决定：{peter_lynch_data.get('overall_signal', '中性')} (置信度：{peter_lynch_data.get('confidence', 0):.1f}%)
               - 质量评分：{peter_lynch_data.get('score_percentage', 0):.1f}%
               - GARP评分：{peter_lynch_data.get('garp_analysis', {}).get('score_percentage', 0):.1f}%

            2. **GARP分析 (合理价格增长)**
               - 深入分析PEG比率和林奇的核心GARP指标
               - 评估市盈率相对于增长率的合理性
               - 讨论价格相对于增长潜力的吸引力

            3. **增长一致性评估**
               - 分析收入和盈利增长的质量和可持续性
               - 评估增长加速或减速的迹象
               - 讨论盈利预测的可靠性

            4. **业务质量和可理解性**
               - 评估商业模式的简单性和可理解性
               - 分析竞争地位和行业动态
               - 讨论财务健康状况和资本效率

            5. **市场定位和规模**
               - 评估公司规模是否在林奇的偏好范围内
               - 分析行业和市场增长潜力
               - 讨论扩张机会和市场份额增长

            6. **林奇原则符合度**
               - 评估公司如何符合林奇的四个核心原则
               - 突出显示任何红旗或关注领域
               - 提供原则遵循的整体评估

            7. **林奇式的最终判断**
               - 用林奇的声音和风格提供最终的投资论点
               - 包括具体的推理和现实世界的类比
               - 提供明确的行动建议和价格目标

            请使用林奇标志性的平易近人、实用和以增长为重点的方法。包括具体的数字和明确的推理。"""
        else:
            system_prompt = """You are Peter Lynch, the legendary growth investor and former manager of Fidelity's Magellan Fund. Analyze based on Lynch's investment principles:
            - Invest in what you know: Focus on companies and products you can understand
            - Growth at Reasonable Price (GARP): PEG ratio <1.0 is the key metric
            - Earnings Growth: Look for 15-30% annual earnings growth rates
            - Simple Business Models: Avoid complex financial engineering or hard-to-understand businesses
            - Mid-cap preference: Companies in the $2B-$50B market cap range
            - Consistent Growth: Steady, predictable revenue and earnings growth
            - Strong Fundamentals: Good ROE, manageable debt, positive cash flow
            - Earnings Acceleration: Look for signs of accelerating earnings growth

            When providing your reasoning, be thorough and specific by:
            1. Emphasizing PEG ratio and growth metrics as primary decision factors
            2. Explaining how the company aligns with or violates GARP principles
            3. Assessing the understandability and simplicity of the business
            4. Providing specific growth data and trend analysis
            5. Using Peter Lynch's straightforward, practical, and investor-friendly tone

            For example, if bullish: "This company reminds me of those great growth stories I discovered at Fidelity. The PEG ratio of 0.8 shows a classic growth-at-a-reasonable-price opportunity, and the consecutive earnings acceleration suggests..."
            For example, if bearish: "While this is an interesting story, the PEG ratio of 2.5 shows investors are paying too much for growth. I'd rather wait for a better entry point or look for..."

            Follow these guidelines strictly."""

            user_prompt = f"""Based on the following data, create an investment analysis for {ticker} as Peter Lynch would:
            
            Company Information:
            - Company Name: {stock_info.get('name', ticker)}
            - Sector: {stock_info.get('sector', 'N/A')}
            - Industry: {stock_info.get('industry', 'N/A')}
            - Market Cap: ${stock_info.get('market_cap', 'N/A')}
            - Current Price: ${stock_info.get('current_price', 'N/A')}
            - Employee Count: {stock_info.get('full_time_employees', 'N/A')}
            
            Key Financial Metrics:
            - P/E Ratio: {stock_info.get('pe_ratio', 'N/A')}
            - Forward P/E: {stock_info.get('forward_pe', 'N/A')}
            - PEG Ratio: {stock_info.get('peg_ratio', 'N/A')}
            - Price to Book: {stock_info.get('price_to_book', 'N/A')}
            - Price to Sales: {stock_info.get('price_to_sales', 'N/A')}
            - Enterprise Value/EBITDA: {stock_info.get('enterprise_to_ebitda', 'N/A')}
            - Debt to Equity: {stock_info.get('debt_to_equity', 'N/A')}
            - Current Ratio: {stock_info.get('current_ratio', 'N/A')}
            - Quick Ratio: {stock_info.get('quick_ratio', 'N/A')}
            - ROE: {stock_info.get('return_on_equity', 'N/A')}%
            - ROA: {stock_info.get('return_on_assets', 'N/A')}%
            - Gross Margin: {stock_info.get('gross_margins', 'N/A')}%
            - Operating Margin: {stock_info.get('operating_margins', 'N/A')}%
            - Profit Margin: {stock_info.get('profit_margins', 'N/A')}%
            - Revenue Growth: {stock_info.get('revenue_growth', 'N/A')}%
            - Earnings Growth: {stock_info.get('earnings_growth', 'N/A')}%
            - Free Cash Flow: {stock_info.get('free_cash_flow', 'N/A')}
            - Dividend Yield: {stock_info.get('dividend_yield', 'N/A')}%
            - Payout Ratio: {stock_info.get('payout_ratio', 'N/A')}%
            - Beta: {stock_info.get('beta', 'N/A')}

            Peter Lynch Analysis Data:
            {json.dumps(peter_lynch_data, indent=2, default=str)}

            Please provide an in-depth Lynch-style analysis covering:

            1. **Investment Signal Summary**
               - Overall investment decision: {peter_lynch_data.get('overall_signal', 'neutral')} (Confidence: {peter_lynch_data.get('confidence', 0):.1f}%)
               - Quality Score: {peter_lynch_data.get('score_percentage', 0):.1f}%
               - GARP Score: {peter_lynch_data.get('garp_analysis', {}).get('score_percentage', 0):.1f}%

            2. **GARP Analysis (Growth at Reasonable Price)**
               - Deep dive into PEG ratio and Lynch's core GARP metrics
               - Assess the reasonableness of P/E relative to growth rate
               - Discuss price attractiveness relative to growth potential

            3. **Growth Consistency Assessment**
               - Analyze the quality and sustainability of revenue and earnings growth
               - Evaluate signs of growth acceleration or deceleration
               - Discuss reliability of earnings projections

            4. **Business Quality and Understandability**
               - Assess the simplicity and understandability of the business model
               - Analyze competitive position and industry dynamics
               - Discuss financial health and capital efficiency

            5. **Market Position and Size**
               - Evaluate whether company size falls within Lynch's preferred range
               - Analyze industry and market growth potential
               - Discuss expansion opportunities and market share growth

            6. **Lynch Principles Adherence**
               - Evaluate how well the company meets Lynch's four core principles
               - Highlight any red flags or areas of concern
               - Provide overall assessment of principle adherence

            7. **Lynch-Style Final Verdict**
               - Provide your final investment thesis in Lynch's voice and style
               - Include specific reasoning and real-world analogies
               - Offer clear actionable recommendations and price targets

            Please use Lynch's signature approachable, practical, and growth-focused approach. Include specific numbers and clear reasoning."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }