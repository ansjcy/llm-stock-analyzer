#!/usr/bin/env python3
"""
LLM Stock Analysis Tool - Main Application
Comprehensive stock analysis using multiple data sources and LLM-powered insights
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import pandas as pd
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils.config import config
from src.utils.logger import stock_logger
from src.utils.translations import set_language, t
from src.data.yahoo_finance import get_yahoo_finance_api
from src.analysis.technical_indicators import get_technical_analyzer
from src.llm.client_factory import create_llm_client, LLMClientFactory


console = Console()


class StockAnalyzer:
    """Main stock analysis orchestrator"""

    def __init__(self, llm_provider: Optional[str] = None, benchmark_symbols: Optional[list] = None,
                 language: str = 'en'):
        self.language = language
        self.yahoo_api = get_yahoo_finance_api()

        # Initialize technical analyzer with benchmark symbols for correlation analysis
        self.benchmark_symbols = benchmark_symbols
        self.technical_analyzer = get_technical_analyzer(benchmark_symbols=self.benchmark_symbols)

        # Try to create LLM client with fallback to available providers
        self.llm_client = None
        available_providers = LLMClientFactory.get_available_providers()

        if available_providers:
            try:
                if llm_provider and LLMClientFactory.validate_provider(llm_provider):
                    self.llm_client = create_llm_client(llm_provider, language=language)
                    provider_msg = f"Using {llm_provider.upper()} for AI analysis" if language == 'en' else f"使用{llm_provider.upper()}进行AI分析"
                    console.print(f"[green]{provider_msg}[/green]")
                else:
                    # Use default provider or first available
                    provider = llm_provider or config.DEFAULT_LLM_PROVIDER
                    if not LLMClientFactory.validate_provider(provider):
                        provider = available_providers[0]
                    self.llm_client = create_llm_client(provider, language=language)
                    provider_msg = f"Using {provider.upper()} for AI analysis" if language == 'en' else f"使用{provider.upper()}进行AI分析"
                    console.print(f"[green]{provider_msg}[/green]")
            except Exception as e:
                warning_msg = f"Warning: Could not initialize LLM client: {e}" if language == 'en' else f"警告：无法初始化LLM客户端：{e}"
                continue_msg = "Analysis will continue without AI insights" if language == 'en' else "分析将在没有AI洞察的情况下继续"
                console.print(f"[yellow]{warning_msg}[/yellow]")
                console.print(f"[yellow]{continue_msg}[/yellow]")
        else:
            no_provider_msg = "No LLM providers configured. Add API keys to enable AI analysis." if language == 'en' else "未配置LLM提供商。添加API密钥以启用AI分析。"
            available_msg = "Available providers: openai, gemini" if language == 'en' else "可用提供商：openai, gemini"
            console.print(f"[yellow]{no_provider_msg}[/yellow]")
            console.print(f"[yellow]{available_msg}[/yellow]")

    def analyze_stock(self, ticker: str, detailed: bool = False,
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     generate_charts: bool = False) -> Dict[str, Any]:
        """Perform comprehensive stock analysis"""

        # Generate a single timestamp for consistent naming across all files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        results = {
            'ticker': ticker,
            'analysis_date': datetime.now().isoformat(),
            'timestamp': timestamp,  # Add timestamp to results for consistent naming
            'stock_info': {},
            'technical_analysis': {},
            'correlation_analysis': {},
            'fundamental_analysis': {},
            'news_analysis': {},
            'llm_insights': {},
            'recommendation': {},
            'summary': {},
            'charts': {}
        }

        # Store historical data for chart generation
        historical_data_for_charts = None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Step 1: Get basic stock information
            task1_desc = "Fetching stock information..." if self.language == 'en' else "获取股票信息..."
            task1 = progress.add_task(task1_desc, total=1)
            # Use comprehensive stock info to get PE ratio history
            stock_info = self.yahoo_api.get_comprehensive_stock_info(ticker)
            if not stock_info:
                error_msg = f"Error: Could not fetch data for ticker {ticker}" if self.language == 'en' else f"错误：无法获取股票代码 {ticker} 的数据"
                console.print(f"[red]{error_msg}[/red]")
                return results

            results['stock_info'] = stock_info
            progress.update(task1, completed=1)

            # Step 2: Get historical data for technical analysis
            task2_desc = "Fetching historical data..." if self.language == 'en' else "获取历史数据..."
            task2 = progress.add_task(task2_desc, total=1)
            period = "1y" if not start_date else "max"
            historical_data = self.yahoo_api.get_historical_data(ticker, period=period)
            progress.update(task2, completed=1)

            if historical_data is not None and len(historical_data) > 50:
                # Store for chart generation
                historical_data_for_charts = historical_data.copy()

                # Step 3: Perform comprehensive technical analysis
                task3_desc = "Performing comprehensive technical analysis..." if self.language == 'en' else "执行综合技术分析..."
                task3 = progress.add_task(task3_desc, total=1)
                technical_analysis = self.technical_analyzer.analyze_technical_signals(historical_data, ticker)
                results['technical_analysis'] = technical_analysis
                progress.update(task3, completed=1)

                # Correlation analysis is already included in technical analysis
                correlation_analysis = technical_analysis.get('correlation_analysis', {})
                results['correlation_analysis'] = correlation_analysis
            else:
                warning_msg = "Warning: Insufficient historical data for technical analysis" if self.language == 'en' else "警告：历史数据不足，无法进行技术分析"
                console.print(f"[yellow]{warning_msg}[/yellow]")

            # Step 4: Get financial data for fundamental analysis
            task4_desc = "Fetching financial data..." if self.language == 'en' else "获取财务数据..."
            task4 = progress.add_task(task4_desc, total=1)
            financial_data = self.yahoo_api.get_financial_data(ticker)
            results['fundamental_analysis'] = {
                'financial_statements_available': bool(financial_data),
                'key_metrics': self._extract_key_metrics(stock_info)
            }
            progress.update(task4, completed=1)

            # Step 5: Get news data
            task5_desc = "Fetching recent news..." if self.language == 'en' else "获取最新消息..."
            task5 = progress.add_task(task5_desc, total=1)
            news_articles = self.yahoo_api.search_stock_news(ticker, max_results=15)
            results['news_analysis'] = {
                'articles_found': len(news_articles),
                'recent_articles': news_articles[:5]  # Store top 5 for summary
            }
            progress.update(task5, completed=1)

            # Step 6: Generate charts if requested
            if generate_charts and historical_data_for_charts is not None:
                task6_desc = "Generating technical analysis charts..." if self.language == 'en' else "生成技术分析图表..."
                task6 = progress.add_task(task6_desc, total=1)
                chart_filename = self.generate_charts(results, historical_data_for_charts, timestamp)
                if chart_filename:
                    results['charts']['technical_analysis'] = chart_filename

                # Generate correlation chart
                correlation_chart = self.generate_correlation_chart(results, timestamp)
                if correlation_chart:
                    results['charts']['correlation'] = correlation_chart

                progress.update(task6, completed=1)

            # Step 7: Generate LLM insights (if available)
            if self.llm_client:
                task7_desc = "Generating AI insights..." if self.language == 'en' else "生成AI洞察..."
                task7 = progress.add_task(task7_desc, total=4)

                # Enhanced technical analysis insights with comprehensive data
                if results['technical_analysis']:
                    # Combine technical and correlation data for LLM analysis
                    enhanced_technical_data = {
                        **results['technical_analysis'],
                        'correlation_analysis': results.get('correlation_analysis', {})
                    }
                    technical_insights = self.llm_client.generate_technical_analysis(
                        ticker, enhanced_technical_data, stock_info
                    )
                    results['llm_insights']['technical'] = technical_insights
                    progress.advance(task7)

                # Fundamental analysis insights
                fundamental_insights = self.llm_client.generate_fundamental_analysis(
                    ticker, stock_info, financial_data
                )
                results['llm_insights']['fundamental'] = fundamental_insights
                progress.advance(task7)

                # News sentiment analysis
                if news_articles:
                    news_insights = self.llm_client.generate_news_analysis(
                        ticker, news_articles, stock_info
                    )
                    results['llm_insights']['news'] = news_insights
                    progress.advance(task7)

                # Overall investment recommendation
                investment_recommendation = self.llm_client.generate_investment_recommendation(
                    ticker, stock_info,
                    results['llm_insights'].get('technical', ''),
                    results['llm_insights'].get('fundamental', ''),
                    results['llm_insights'].get('news', '')
                )
                results['recommendation'] = {
                    'full_analysis': investment_recommendation
                }
                progress.advance(task7)

                # Executive summary
                executive_summary = self.llm_client.summarize_analysis(
                    ticker, stock_info,
                    results['llm_insights'].get('technical', ''),
                    results['llm_insights'].get('fundamental', ''),
                    results['llm_insights'].get('news', ''),
                    investment_recommendation
                )
                results['summary'] = {
                    'executive_summary': executive_summary
                }

        return results

    def _extract_key_metrics(self, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key fundamental metrics from stock info"""
        return {
            'valuation_metrics': {
                'pe_ratio': stock_info.get('pe_ratio'),
                'forward_pe': stock_info.get('forward_pe'),
                'peg_ratio': stock_info.get('peg_ratio'),
                'price_to_book': stock_info.get('price_to_book'),
                'price_to_sales': stock_info.get('price_to_sales'),
            },
            'financial_health': {
                'debt_to_equity': stock_info.get('debt_to_equity'),
                'current_ratio': stock_info.get('current_ratio'),
                'quick_ratio': stock_info.get('quick_ratio'),
            },
            'profitability': {
                'return_on_equity': stock_info.get('return_on_equity'),
                'return_on_assets': stock_info.get('return_on_assets'),
                'gross_margins': stock_info.get('gross_margins'),
                'operating_margins': stock_info.get('operating_margins'),
                'profit_margins': stock_info.get('profit_margins'),
            },
            'growth': {
                'revenue_growth': stock_info.get('revenue_growth'),
                'earnings_growth': stock_info.get('earnings_growth'),
            }
        }

    def display_results(self, results: Dict[str, Any], detailed: bool = False):
        """Display analysis results in a formatted way"""

        ticker = results['ticker']
        stock_info = results['stock_info']

        # Header
        analysis_title = t('stock_analysis_report', ticker=ticker) if self.language == 'zh' else f"Stock Analysis Report: {ticker}"
        stock_name = stock_info.get('name', 'N/A')
        analysis_date = t('analysis_date', date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')) if self.language == 'zh' else f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        console.print(Panel.fit(
            f"[bold blue]{analysis_title}[/bold blue]\n"
            f"[green]{stock_name}[/green]\n"
            f"{analysis_date}"
        ))

        # Basic Stock Information
        overview_title = t('stock_overview') if self.language == 'zh' else "Stock Overview"
        basic_table = Table(title=overview_title)
        metric_header = "指标" if self.language == 'zh' else "Metric"
        value_header = "数值" if self.language == 'zh' else "Value"
        basic_table.add_column(metric_header, style="cyan")
        basic_table.add_column(value_header, style="green")

        current_price_label = t('current_price') if self.language == 'zh' else "Current Price"
        previous_close_label = t('previous_close') if self.language == 'zh' else "Previous Close"
        day_range_label = t('day_range') if self.language == 'zh' else "Day Range"
        week_52_range_label = t('52_week_range') if self.language == 'zh' else "52-Week Range"
        market_cap_label = t('market_cap') if self.language == 'zh' else "Market Cap"
        volume_label = t('volume') if self.language == 'zh' else "Volume"
        pe_ratio_label = t('pe_ratio') if self.language == 'zh' else "P/E Ratio"
        beta_label = t('beta') if self.language == 'zh' else "Beta"

        basic_table.add_row(current_price_label, f"${stock_info.get('current_price', 'N/A')}")
        basic_table.add_row(previous_close_label, f"${stock_info.get('previous_close', 'N/A')}")
        basic_table.add_row(day_range_label, f"${stock_info.get('day_low', 'N/A')} - ${stock_info.get('day_high', 'N/A')}")
        basic_table.add_row(week_52_range_label, f"${stock_info.get('52_week_low', 'N/A')} - ${stock_info.get('52_week_high', 'N/A')}")

        # Format market cap
        market_cap_value = stock_info.get('market_cap')
        market_cap_formatted = f"${market_cap_value:,}" if isinstance(market_cap_value, (int, float)) else str(market_cap_value) if market_cap_value else "N/A"
        basic_table.add_row(market_cap_label, market_cap_formatted)

        # Format volume
        volume_value = stock_info.get('volume')
        volume_formatted = f"{volume_value:,}" if isinstance(volume_value, (int, float)) else str(volume_value) if volume_value else "N/A"
        basic_table.add_row(volume_label, volume_formatted)

        basic_table.add_row(pe_ratio_label, f"{stock_info.get('pe_ratio', 'N/A')}")
        basic_table.add_row(beta_label, f"{stock_info.get('beta', 'N/A')}")

        console.print(basic_table)

        # Enhanced Technical Analysis Summary
        tech_analysis = results.get('technical_analysis', {})
        if tech_analysis:
            # Main technical signals
            overall_signal = tech_analysis.get('overall_signal', 'neutral')
            confidence = tech_analysis.get('confidence', 0)
            signal_color = 'green' if overall_signal == 'bullish' else 'red' if overall_signal == 'bearish' else 'yellow'

            # Translate signal values
            if self.language == 'zh':
                signal_trans = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '中性'}
                overall_signal_display = signal_trans.get(overall_signal, overall_signal)
                tech_title = "增强技术分析"
                overall_signal_label = "总体信号"
                confidence_label = "置信度"
                strategic_signals_label = "策略信号"
                key_indicators_label = "关键指标"
            else:
                overall_signal_display = overall_signal.upper()
                tech_title = "Enhanced Technical Analysis"
                overall_signal_label = "Overall Signal"
                confidence_label = "Confidence"
                strategic_signals_label = "Strategic Signals"
                key_indicators_label = "Key Indicators"

            tech_summary = f"[bold]{tech_title}[/bold]\n"
            tech_summary += f"{overall_signal_label}: [{signal_color}]{overall_signal_display}[/] ({confidence_label}: {confidence:.1f}%)\n\n"

            # Strategic combination signals
            strategies = tech_analysis.get('strategic_combinations', {})
            if strategies:
                tech_summary += f"[bold]{strategic_signals_label}:[/bold]\n"
                rsi_macd = strategies.get('rsi_macd_strategy', {})
                if rsi_macd:
                    signal = rsi_macd.get('signal', 'neutral')
                    color = 'green' if signal == 'bullish' else 'red' if signal == 'bearish' else 'yellow'
                    if self.language == 'zh':
                        signal_trans = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '中性'}
                        signal_display = signal_trans.get(signal, signal)
                        score_label = "评分"
                    else:
                        signal_display = signal.upper()
                        score_label = "Score"
                    tech_summary += f"• RSI+MACD: [{color}]{signal_display}[/] ({score_label}: {rsi_macd.get('score', 0):.1f})\n"

                bb_strategy = strategies.get('bollinger_rsi_macd_strategy', {})
                if bb_strategy:
                    signal = bb_strategy.get('signal', 'neutral')
                    color = 'green' if signal == 'bullish' else 'red' if signal == 'bearish' else 'yellow'
                    if self.language == 'zh':
                        signal_display = signal_trans.get(signal, signal)
                    else:
                        signal_display = signal.upper()
                    tech_summary += f"• BB+RSI+MACD: [{color}]{signal_display}[/] ({score_label}: {bb_strategy.get('score', 0):.1f})\n"

                ma_strategy = strategies.get('ma_rsi_volume_strategy', {})
                if ma_strategy:
                    signal = ma_strategy.get('signal', 'neutral')
                    color = 'green' if signal == 'bullish' else 'red' if signal == 'bearish' else 'yellow'
                    if self.language == 'zh':
                        signal_display = signal_trans.get(signal, signal)
                        ma_label = "移动平均"
                    else:
                        signal_display = signal.upper()
                        ma_label = "MA"
                    tech_summary += f"• {ma_label}+RSI+Volume: [{color}]{signal_display}[/] ({score_label}: {ma_strategy.get('score', 0):.1f})\n"

            # Key indicators
            momentum = tech_analysis.get('momentum', {})
            if momentum:
                tech_summary += f"\n[bold]{key_indicators_label}:[/bold]\n"
                tech_summary += f"• RSI: {momentum.get('rsi', 'N/A')} ({momentum.get('rsi_signal', 'N/A')})\n"
                stoch_label = "随机振荡器" if self.language == 'zh' else "Stochastic"
                stoch_k_value = momentum.get('stoch_k', 'N/A')
                stoch_k_formatted = f"{stoch_k_value:.1f}" if isinstance(stoch_k_value, (int, float)) else str(stoch_k_value)
                tech_summary += f"• {stoch_label}: {stoch_k_formatted} ({momentum.get('stoch_signal', 'N/A')})\n"

                williams_r_value = momentum.get('williams_r', 'N/A')
                williams_r_formatted = f"{williams_r_value:.1f}" if isinstance(williams_r_value, (int, float)) else str(williams_r_value)
                tech_summary += f"• Williams %R: {williams_r_formatted}\n"

            trend = tech_analysis.get('trend', {})
            if trend:
                histogram_label = "柱状图" if self.language == 'zh' else "Histogram"
                histogram_value = trend.get('macd_histogram', 'N/A')
                histogram_formatted = f"{histogram_value:.4f}" if isinstance(histogram_value, (int, float)) else str(histogram_value)
                tech_summary += f"• MACD: {trend.get('macd_signal', 'N/A')} ({histogram_label}: {histogram_formatted})\n"

            # Get moving average trend from the moving_averages section
            moving_averages = tech_analysis.get('moving_averages', {})
            if moving_averages:
                ma_label = "移动平均线" if self.language == 'zh' else "Moving Averages"
                ma_trend = moving_averages.get('sma_trend', 'N/A')
                if self.language == 'zh' and ma_trend in ['bullish', 'bearish', 'neutral']:
                    ma_trend_trans = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '中性'}
                    ma_trend = ma_trend_trans.get(ma_trend, ma_trend)
                tech_summary += f"• {ma_label}: {ma_trend}\n"

            tech_analysis_title = t('technical_analysis') if self.language == 'zh' else "Technical Analysis"
            console.print(Panel(tech_summary, title=tech_analysis_title))

        # Correlation Analysis
        correlation = results.get('correlation_analysis', {})
        if correlation and detailed:
            corr_title = t('correlation_analysis') if self.language == 'zh' else "Market Correlation Analysis"
            corr_summary = f"[bold]{corr_title}[/bold]\n"
            correlations = correlation.get('correlations', {})
            if correlations:
                sp500_label = t('sp500_correlation') if self.language == 'zh' else "S&P 500"
                dow_label = t('dow_jones_correlation') if self.language == 'zh' else "Dow Jones"
                nasdaq_label = t('nasdaq_correlation') if self.language == 'zh' else "NASDAQ"

                gspc_corr = correlations.get('^GSPC', 'N/A')
                dji_corr = correlations.get('^DJI', 'N/A')
                ixic_corr = correlations.get('^IXIC', 'N/A')

                gspc_formatted = f"{gspc_corr:.3f}" if isinstance(gspc_corr, (int, float)) else str(gspc_corr)
                dji_formatted = f"{dji_corr:.3f}" if isinstance(dji_corr, (int, float)) else str(dji_corr)
                ixic_formatted = f"{ixic_corr:.3f}" if isinstance(ixic_corr, (int, float)) else str(ixic_corr)

                corr_summary += f"• {sp500_label}: {gspc_formatted}\n"
                corr_summary += f"• {dow_label}: {dji_formatted}\n"
                corr_summary += f"• {nasdaq_label}: {ixic_formatted}\n"

            diversification = correlation.get('diversification_score', 'N/A')
            beta = correlation.get('beta', 'N/A')
            div_label = t('diversification_score') if self.language == 'zh' else "Diversification Score"
            beta_label = t('beta_vs_sp500') if self.language == 'zh' else "Beta (vs S&P 500)"
            corr_summary += f"\n{div_label}: {diversification}\n"
            corr_summary += f"{beta_label}: {beta:.3f}" if isinstance(beta, (int, float)) else f"Beta: {beta}"

            console.print(Panel(corr_summary, title=corr_title))

        # News Summary
        news_analysis = results.get('news_analysis', {})
        if news_analysis.get('articles_found', 0) > 0:
            recent_articles = news_analysis.get('recent_articles', [])
            headlines = []
            for article in recent_articles[:3]:
                title = article.get('title', '').strip()
                if title:
                    headlines.append(f"• {title}")

            news_title = t('recent_news') if self.language == 'zh' else "Recent News"
            articles_label = t('articles_found') if self.language == 'zh' else "Articles Found"
            headlines_label = t('latest_headlines') if self.language == 'zh' else "Latest Headlines"
            no_headlines_msg = t('no_headlines_available') if self.language == 'zh' else "No headlines available"

            news_content = f"[bold]{news_title}[/bold]\n"
            news_content += f"{articles_label}: {news_analysis.get('articles_found', 0)}\n"
            if headlines:
                news_content += f"{headlines_label}:\n" + "\n".join(headlines)
            else:
                news_content += f"{headlines_label}:\n• {no_headlines_msg}"

            console.print(Panel(news_content, title=news_title))

        # LLM Insights
        llm_insights = results.get('llm_insights', {})
        if llm_insights:
            ai_insights_title = t('ai_generated_insights') if self.language == 'zh' else "AI-Generated Insights"
            console.print(Panel.fit(f"[bold blue]{ai_insights_title}[/bold blue]"))

            if 'technical' in llm_insights and detailed:
                tech_title = t('technical_analysis') if self.language == 'zh' else "Technical Analysis"
                console.print(Panel(
                    Markdown(llm_insights['technical']),
                    title=tech_title
                ))

            if 'fundamental' in llm_insights and detailed:
                fund_title = t('fundamental_analysis') if self.language == 'zh' else "Fundamental Analysis"
                console.print(Panel(
                    Markdown(llm_insights['fundamental']),
                    title=fund_title
                ))

            if 'news' in llm_insights and detailed:
                news_sentiment_title = t('news_sentiment_analysis') if self.language == 'zh' else "News & Sentiment Analysis"
                console.print(Panel(
                    Markdown(llm_insights['news']),
                    title=news_sentiment_title
                ))

        # Investment Recommendation
        recommendation = results.get('recommendation', {})
        if recommendation:
            rec_title = t('investment_recommendation') if self.language == 'zh' else "Investment Recommendation"
            no_rec_msg = "无可用建议" if self.language == 'zh' else "No recommendation available"
            console.print(Panel(
                Markdown(recommendation.get('full_analysis', no_rec_msg)),
                title=f"[bold green]{rec_title}[/bold green]"
            ))

        # Executive Summary
        summary = results.get('summary', {})
        if summary:
            exec_title = t('executive_summary') if self.language == 'zh' else "Executive Summary"
            no_summary_msg = "无可用摘要" if self.language == 'zh' else "No summary available"
            console.print(Panel(
                Markdown(summary.get('executive_summary', no_summary_msg)),
                title=f"[bold yellow]{exec_title}[/bold yellow]"
            ))

    def save_report(self, results: Dict[str, Any], format_type: str = "markdown"):
        """Save analysis report to file"""
        ticker = results['ticker']
        timestamp = results['timestamp']

        # Create reports directory in public folder if it doesn't exist
        reports_dir = "./stock-analysis-viewer/public/reports"
        os.makedirs(reports_dir, exist_ok=True)

        if format_type == "json":
            filename_full = f"{reports_dir}/{ticker}_analysis_{timestamp}.json"
            with open(filename_full, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            # Return web-accessible path for frontend usage
            filename = f"reports/{ticker}_analysis_{timestamp}.json"

        elif format_type == "markdown":
            filename_full = f"{reports_dir}/{ticker}_analysis_{timestamp}.md"
            with open(filename_full, 'w') as f:
                f.write(self._generate_markdown_report(results))
            # Return web-accessible path for frontend usage
            filename = f"reports/{ticker}_analysis_{timestamp}.md"

        save_msg = f"Report saved to: {filename_full}" if self.language == 'en' else f"报告已保存至：{filename_full}"
        console.print(f"[green]{save_msg}[/green]")
        return filename

    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown report"""
        ticker = results['ticker']
        stock_info = results['stock_info']

        md_content = f"""# Stock Analysis Report: {ticker}

**Company:** {stock_info.get('name', 'N/A')}  
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Sector:** {stock_info.get('sector', 'N/A')}  
**Industry:** {stock_info.get('industry', 'N/A')}  

## Stock Overview

| Metric | Value |
|--------|-------|
| Current Price | ${stock_info.get('current_price', 'N/A')} |
| Previous Close | ${stock_info.get('previous_close', 'N/A')} |
| Day Range | ${stock_info.get('day_low', 'N/A')} - ${stock_info.get('day_high', 'N/A')} |
| 52-Week Range | ${stock_info.get('52_week_low', 'N/A')} - ${stock_info.get('52_week_high', 'N/A')} |
| Market Cap | {f"${stock_info.get('market_cap'):,}" if isinstance(stock_info.get('market_cap'), (int, float)) else stock_info.get('market_cap', 'N/A')} |
| Volume | {f"{stock_info.get('volume'):,}" if isinstance(stock_info.get('volume'), (int, float)) else stock_info.get('volume', 'N/A')} |
| P/E Ratio | {stock_info.get('pe_ratio', 'N/A')} |
| Beta | {stock_info.get('beta', 'N/A')} |

"""

        # Add enhanced technical analysis
        tech_analysis = results.get('technical_analysis', {})
        if tech_analysis:
            confidence_value = tech_analysis.get('confidence', 'N/A')
            confidence_formatted = f"{confidence_value:.1f}" if isinstance(confidence_value, (int, float)) else str(confidence_value)

            md_content += f"""## Enhanced Technical Analysis

**Overall Signal:** {tech_analysis.get('overall_signal', 'N/A').upper()}  
**Confidence:** {confidence_formatted}%  

### Strategic Combination Signals
"""
            strategies = tech_analysis.get('strategic_combinations', {})
            if strategies:
                for strategy_name, strategy_data in strategies.items():
                    signal = strategy_data.get('signal', 'neutral')
                    score = strategy_data.get('score', 0)
                    score_formatted = f"{score:.1f}" if isinstance(score, (int, float)) else str(score)
                    md_content += f"- **{strategy_name.replace('_', ' ').title()}:** {signal.upper()} (Score: {score_formatted})\n"

            md_content += f"""
### Key Technical Indicators
"""
            # Add momentum indicators
            momentum = tech_analysis.get('momentum', {})
            if momentum:
                md_content += f"- **RSI:** {momentum.get('rsi', 'N/A')} ({momentum.get('rsi_signal', 'N/A')})\n"

                stoch_k_value = momentum.get('stoch_k', 'N/A')
                stoch_k_formatted = f"{stoch_k_value:.1f}" if isinstance(stoch_k_value, (int, float)) else str(stoch_k_value)
                md_content += f"- **Stochastic %K:** {stoch_k_formatted}\n"

                williams_r_value = momentum.get('williams_r', 'N/A')
                williams_r_formatted = f"{williams_r_value:.1f}" if isinstance(williams_r_value, (int, float)) else str(williams_r_value)
                md_content += f"- **Williams %R:** {williams_r_formatted}\n"

            # Add trend indicators
            trend = tech_analysis.get('trend', {})
            if trend:
                md_content += f"- **MACD Signal:** {trend.get('macd_signal', 'N/A')}\n"

            # Get moving average trend from the moving_averages section
            moving_averages = tech_analysis.get('moving_averages', {})
            if moving_averages:
                md_content += f"- **Moving Averages:** {moving_averages.get('sma_trend', 'N/A')}\n"

            # Add volatility indicators
            volatility = tech_analysis.get('volatility', {})
            if volatility:
                md_content += f"- **Bollinger Band Position:** {volatility.get('bb_position', 'N/A')}\n"
                atr_value = volatility.get('atr', 'N/A')
                atr_formatted = f"{atr_value:.2f}" if isinstance(atr_value, (int, float)) else str(atr_value)
                md_content += f"- **ATR:** {atr_formatted}\n"
                md_content += f"- **Volatility Regime:** {volatility.get('volatility_regime', 'N/A')}\n"

        # Add correlation analysis
        correlation = results.get('correlation_analysis', {})
        if correlation:
            md_content += f"""
## Market Correlation Analysis

| Index | Correlation |
|-------|-------------|"""
            correlations = correlation.get('correlations', {})
            for symbol, corr_value in correlations.items():
                index_name = {'%5EGSPC': 'S&P 500', '%5EDJI': 'Dow Jones', '%5EIXIC': 'NASDAQ'}.get(symbol, symbol)
                if isinstance(corr_value, (int, float)):
                    md_content += f"\n| {index_name} | {corr_value:.3f} |"
                else:
                    md_content += f"\n| {index_name} | {corr_value} |"

            beta_value = correlation.get('beta', 'N/A')
            beta_formatted = f"{beta_value:.3f}" if isinstance(beta_value, (int, float)) else str(beta_value)

            md_content += f"""

**Diversification Score:** {correlation.get('diversification_score', 'N/A')}  
**Beta (vs S&P 500):** {beta_formatted}  
**Risk Assessment:** {correlation.get('risk_assessment', 'N/A')}

"""

        # Add LLM insights
        llm_insights = results.get('llm_insights', {})
        if llm_insights.get('technical'):
            md_content += f"""### AI Technical Analysis
{llm_insights['technical']}

"""

        if llm_insights.get('fundamental'):
            md_content += f"""## Fundamental Analysis
{llm_insights['fundamental']}

"""

        if llm_insights.get('news'):
            md_content += f"""## News & Sentiment Analysis
{llm_insights['news']}

"""

        # Add recommendation
        recommendation = results.get('recommendation', {})
        if recommendation:
            md_content += f"""## Investment Recommendation
{recommendation.get('full_analysis', 'No recommendation available')}

"""

        # Add summary
        summary = results.get('summary', {})
        if summary:
            md_content += f"""## Executive Summary
{summary.get('executive_summary', 'No summary available')}

"""

        md_content += f"""
---
*This report was generated by LLM Stock Analysis Tool with Enhanced Technical Analysis on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return md_content

    def generate_charts(self, results: Dict[str, Any], historical_data: pd.DataFrame = None, timestamp: str = None):
        """Generate comprehensive charts for technical analysis"""
        try:
            ticker = results['ticker']
            tech_analysis = results.get('technical_analysis', {})

            if historical_data is None or len(historical_data) < 20:
                console.print("[yellow]Insufficient data for chart generation[/yellow]")
                return None

            # Set up the plotting style
            plt.style.use('seaborn-v0_8')
            sns.set_palette("husl")

            # Create a figure with multiple subplots
            fig, axes = plt.subplots(4, 1, figsize=(14, 16))
            fig.suptitle(f'{ticker} - Technical Analysis Dashboard', fontsize=16, fontweight='bold')

            # Prepare data
            dates = historical_data.index
            prices = historical_data['Close']
            volumes = historical_data['Volume']

            # Calculate technical indicators for plotting
            sma_20 = prices.rolling(window=20).mean()
            sma_50 = prices.rolling(window=50).mean()
            sma_200 = prices.rolling(window=200).mean()

            # RSI calculation for subplot
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            # MACD calculation
            exp1 = prices.ewm(span=12).mean()
            exp2 = prices.ewm(span=26).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line

            # 1. Price Chart with Moving Averages
            ax1 = axes[0]
            ax1.plot(dates, prices, label='Close Price', linewidth=2, color='#1f77b4')
            ax1.plot(dates, sma_20, label='SMA 20', alpha=0.8, color='#ff7f0e')
            ax1.plot(dates, sma_50, label='SMA 50', alpha=0.8, color='#2ca02c')
            ax1.plot(dates, sma_200, label='SMA 200', alpha=0.8, color='#d62728')

            # Add support/resistance levels if available
            support_resistance = tech_analysis.get('support_resistance', {})
            if support_resistance:
                current_price = prices.iloc[-1]
                resistance_1 = support_resistance.get('resistance_1')
                support_1 = support_resistance.get('support_1')

                if resistance_1:
                    ax1.axhline(y=resistance_1, color='red', linestyle='--', alpha=0.6, label=f'Resistance ${resistance_1:.2f}')
                if support_1:
                    ax1.axhline(y=support_1, color='green', linestyle='--', alpha=0.6, label=f'Support ${support_1:.2f}')

            ax1.set_title('Price Chart with Moving Averages & Support/Resistance', fontweight='bold')
            ax1.set_ylabel('Price ($)')
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)

            # 2. RSI Subplot
            ax2 = axes[1]
            ax2.plot(dates, rsi, label='RSI (14)', color='purple', linewidth=2)
            ax2.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
            ax2.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
            ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5)

            # Color fill for overbought/oversold regions
            ax2.fill_between(dates, 70, 100, alpha=0.2, color='red')
            ax2.fill_between(dates, 0, 30, alpha=0.2, color='green')

            ax2.set_title('Relative Strength Index (RSI)', fontweight='bold')
            ax2.set_ylabel('RSI')
            ax2.set_ylim(0, 100)
            ax2.legend(loc='upper left')
            ax2.grid(True, alpha=0.3)

            # 3. MACD Subplot
            ax3 = axes[2]
            ax3.plot(dates, macd_line, label='MACD Line', color='blue', linewidth=2)
            ax3.plot(dates, signal_line, label='Signal Line', color='red', linewidth=2)
            ax3.bar(dates, histogram, label='Histogram', alpha=0.6, color='gray', width=0.8)
            ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)

            ax3.set_title('MACD (Moving Average Convergence Divergence)', fontweight='bold')
            ax3.set_ylabel('MACD')
            ax3.legend(loc='upper left')
            ax3.grid(True, alpha=0.3)

            # 4. Volume Chart
            ax4 = axes[3]
            colors = ['red' if prices.iloc[i] < prices.iloc[i-1] else 'green' for i in range(1, len(prices))]
            colors.insert(0, 'gray')  # First bar color
            ax4.bar(dates, volumes, color=colors, alpha=0.6, width=0.8)

            # Add volume moving average
            volume_ma = volumes.rolling(window=20).mean()
            ax4.plot(dates, volume_ma, label='Volume MA (20)', color='orange', linewidth=2)

            ax4.set_title('Trading Volume', fontweight='bold')
            ax4.set_ylabel('Volume')
            ax4.set_xlabel('Date')
            ax4.legend(loc='upper left')
            ax4.grid(True, alpha=0.3)

            # Format x-axis for all subplots
            for ax in axes:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                ax.tick_params(axis='x', rotation=45)

            # Adjust layout
            plt.tight_layout()

            # Save the chart
            charts_dir = "./stock-analysis-viewer/public/charts"
            os.makedirs(charts_dir, exist_ok=True)
            chart_filename_full = f"{charts_dir}/{ticker}_technical_analysis_{timestamp}.png"
            plt.savefig(chart_filename_full, dpi=300, bbox_inches='tight')

            save_msg = f"Technical analysis chart saved: {chart_filename_full}" if self.language == 'en' else f"技术分析图表已保存：{chart_filename_full}"
            console.print(f"[green]{save_msg}[/green]")

            # Display chart information
            self._display_chart_summary(tech_analysis)

            # Close the plot to free memory
            plt.close()

            # Return web-accessible path for frontend usage
            # Add basePath for production deployment (GitHub Pages)
            base_path = "/stock-analyzer" if os.getenv('NODE_ENV') == 'production' else ""
            chart_filename = f"{base_path}/charts/{ticker}_technical_analysis_{timestamp}.png"
            return chart_filename

        except Exception as e:
            stock_logger.error(f"Error generating charts: {e}")
            error_msg = f"Error generating charts: {e}" if self.language == 'en' else f"生成图表时出错：{e}"
            console.print(f"[red]{error_msg}[/red]")
            return None

    def _display_chart_summary(self, tech_analysis: Dict[str, Any]):
        """Display a summary of chart indicators"""
        if self.language == 'zh':
            chart_title = "图表分析摘要"
            price_pos_label = "价格位置"
            rsi_analysis_label = "RSI分析"
            macd_analysis_label = "MACD分析"
            volume_analysis_label = "成交量分析"
            current_rsi_label = "当前RSI"
            signal_label = "信号"
            trend_label = "趋势"
            histogram_label = "柱状图"
            vs_avg_label = "相对均值"
        else:
            chart_title = "Chart Analysis Summary"
            price_pos_label = "Price Position"
            rsi_analysis_label = "RSI Analysis"
            macd_analysis_label = "MACD Analysis"
            volume_analysis_label = "Volume Analysis"
            current_rsi_label = "Current RSI"
            signal_label = "Signal"
            trend_label = "Trend"
            histogram_label = "Histogram"
            vs_avg_label = "vs Average"

        chart_summary = f"[bold]{chart_title}[/bold]\n"

        # Price vs Moving Averages
        ma_data = tech_analysis.get('moving_averages', {})
        if ma_data:
            chart_summary += f"📈 **{price_pos_label}:**\n"
            chart_summary += f"   • vs SMA 20: {ma_data.get('price_vs_sma_20', 0):.2f}%\n"
            chart_summary += f"   • vs SMA 50: {ma_data.get('price_vs_sma_50', 0):.2f}%\n"
            chart_summary += f"   • vs SMA 200: {ma_data.get('price_vs_sma_200', 0):.2f}%\n"

        # RSI Status
        momentum = tech_analysis.get('momentum', {})
        if momentum:
            rsi_value = momentum.get('rsi', 50)
            rsi_signal = momentum.get('rsi_signal', 'neutral')
            chart_summary += f"\n📊 **{rsi_analysis_label}:**\n"
            chart_summary += f"   • {current_rsi_label}: {rsi_value:.1f}\n"
            chart_summary += f"   • {signal_label}: {rsi_signal.upper()}\n"

        # MACD Status
        trend = tech_analysis.get('trend', {})
        if trend:
            macd_trend = trend.get('macd_trend', 'neutral')
            chart_summary += f"\n📉 **{macd_analysis_label}:**\n"
            chart_summary += f"   • {trend_label}: {macd_trend.upper()}\n"
            chart_summary += f"   • {histogram_label}: {trend.get('macd_histogram', 0):.4f}\n"

        # Volume Analysis
        volume = tech_analysis.get('volume', {})
        if volume:
            volume_signal = volume.get('volume_signal', 'normal')
            chart_summary += f"\n📦 **{volume_analysis_label}:**\n"
            chart_summary += f"   • {signal_label}: {volume_signal.upper()}\n"
            chart_summary += f"   • {vs_avg_label}: {volume.get('volume_ratio', 1):.2f}x\n"

        console.print(Panel(chart_summary, title=f"📊 {chart_title}"))

    def generate_correlation_chart(self, results: Dict[str, Any], timestamp: str = None):
        """Generate correlation heatmap chart"""
        try:
            correlation_data = results.get('correlation_analysis', {})
            correlations = correlation_data.get('correlations', {})

            if not correlations:
                return None

            # Prepare correlation data for heatmap
            timeframes = list(correlations.keys())
            indices = list(correlations.get(timeframes[0], {}).keys()) if timeframes else []

            if not indices:
                return None

            # Create correlation matrix
            correlation_matrix = pd.DataFrame(index=timeframes, columns=indices)
            for timeframe in timeframes:
                for index in indices:
                    correlation_matrix.loc[timeframe, index] = correlations.get(timeframe, {}).get(index, 0)

            # Convert to numeric
            correlation_matrix = correlation_matrix.astype(float)

            # Create heatmap
            plt.figure(figsize=(10, 6))
            sns.heatmap(correlation_matrix, annot=True, cmap='RdYlBu_r', center=0,
                       fmt='.3f', cbar_kws={'label': 'Correlation'})

            chart_title = f'{results["ticker"]} - 市场相关性分析' if self.language == 'zh' else f'{results["ticker"]} - Market Correlation Analysis'
            plt.title(chart_title, fontweight='bold', fontsize=14)

            xlabel = '市场指数' if self.language == 'zh' else 'Market Indices'
            ylabel = '时间框架' if self.language == 'zh' else 'Timeframes'
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.tight_layout()

            # Save chart
            # charts_dir = "./stock-analysis-viewer/public/charts"
            # os.makedirs(charts_dir, exist_ok=True)
            # chart_filename_full = f"{charts_dir}/{results['ticker']}_correlation_{timestamp}.png"
            # plt.savefig(chart_filename_full, dpi=300, bbox_inches='tight')

            # success_msg = f"Correlation chart saved: {chart_filename_full}" if self.language == 'en' else f"相关性图表已保存：{chart_filename_full}"
            # console.print(f"[green]{success_msg}[/green]")
            plt.close()

            # Return web-accessible path for frontend usage
            # Add basePath for production deployment (GitHub Pages)
            base_path = "/stock-analyzer" if os.getenv('NODE_ENV') == 'production' else ""
            chart_filename = f"{base_path}/charts/{results['ticker']}_correlation_{timestamp}.png"
            return chart_filename

        except Exception as e:
            stock_logger.error(f"Error generating correlation chart: {e}")
            return None


@click.command()
@click.option('--ticker', '-t', required=True, help='Stock ticker symbol (e.g., AAPL, MSFT)')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed analysis')
@click.option('--save-report', '-s', is_flag=True, help='Save report to file')
@click.option('--charts', '-c', is_flag=True, help='Generate technical analysis charts')
@click.option('--start-date', help='Start date for analysis (YYYY-MM-DD)')
@click.option('--end-date', help='End date for analysis (YYYY-MM-DD)')
@click.option('--format', 'report_format', default='markdown', type=click.Choice(['markdown', 'json']), help='Report format')
@click.option('--llm-provider', type=click.Choice(['openai', 'gemini']), help='LLM provider to use (openai or gemini)')
@click.option('--benchmarks', help='Comma-separated list of benchmark symbols for correlation analysis')
@click.option('--chinese', is_flag=True, help='Enable Chinese language support')
def main(ticker, detailed, save_report, charts, start_date, end_date, report_format, llm_provider, benchmarks, chinese):
    """LLM Stock Analysis Tool - Comprehensive AI-powered stock analysis with enhanced technical indicators"""

    # Set global language
    language = 'zh' if chinese else 'en'
    set_language(language)

    # Validate configuration
    if not config.validate_config():
        error_msg = "Configuration validation failed. Please check your .env file." if language == 'en' else "配置验证失败。请检查您的.env文件。"
        console.print(f"[red]{error_msg}[/red]")
        sys.exit(1)

    ticker = ticker.upper()

    # Parse benchmark symbols
    benchmark_symbols = None
    if benchmarks:
        benchmark_symbols = [s.strip() for s in benchmarks.split(',')]

    # Create panel message
    if language == 'zh':
        title = "LLM股票分析工具 - 增强版"
        analyzing_label = "分析对象"
        mode_label = "模式"
        detailed_text = "详细" if detailed else "摘要"
        features_label = "功能"
        features_text = "25+技术指标 | 策略组合 | 相关性分析"
    else:
        title = "LLM Stock Analysis Tool - Enhanced Edition"
        analyzing_label = "Analyzing"
        mode_label = "Mode"
        detailed_text = "Detailed" if detailed else "Summary"
        features_label = "Features"
        features_text = "25+ Technical Indicators | Strategic Combinations | Correlation Analysis"

    console.print(Panel.fit(
        f"[bold blue]{title}[/bold blue]\n"
        f"{analyzing_label}: [green]{ticker}[/green]\n"
        f"{mode_label}: {detailed_text}\n"
        f"{features_label}: {features_text}"
    ))

    try:
        analyzer = StockAnalyzer(llm_provider=llm_provider, benchmark_symbols=benchmark_symbols, language=language)
        results = analyzer.analyze_stock(
            ticker=ticker,
            detailed=detailed,
            start_date=start_date,
            end_date=end_date,
            generate_charts=charts
        )

        # Display results
        analyzer.display_results(results, detailed=detailed)

        # Save report if requested
        if save_report:
            analyzer.save_report(results, format_type=report_format)

    except KeyboardInterrupt:
        interrupt_msg = "Analysis interrupted by user" if language == 'en' else "用户中断分析"
        console.print(f"\n[yellow]{interrupt_msg}[/yellow]")
        sys.exit(0)
    except Exception as e:
        error_msg = f"Error during analysis: {e}" if language == 'en' else f"分析过程中出错：{e}"
        console.print(f"\n[red]{error_msg}[/red]")
        stock_logger.error(f"Analysis error for {ticker}: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()