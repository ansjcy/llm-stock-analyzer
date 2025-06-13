#!/usr/bin/env python3
"""
LLM Stock Analysis Tool - Main Application
Comprehensive stock analysis using multiple data sources and LLM-powered insights
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional, List

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
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
from src.analysis.warren_buffett import get_warren_buffett_analyzer
from src.analysis.peter_lynch import get_peter_lynch_analyzer
from src.llm.client_factory import create_llm_client, LLMClientFactory
from src.llm.token_tracker import token_tracker


console = Console()


class StockAnalyzer:
    """Main stock analysis orchestrator"""

    def __init__(self, llm_provider: Optional[str] = None, benchmark_symbols: Optional[list] = None,
                 language: str = 'en', non_llm_only: bool = False):
        self.language = language
        self.non_llm_only = non_llm_only  # Store the non_llm_only flag
        self.yahoo_api = get_yahoo_finance_api()

        # Initialize technical analyzer with benchmark symbols for correlation analysis
        self.benchmark_symbols = benchmark_symbols
        self.technical_analyzer = get_technical_analyzer(benchmark_symbols=self.benchmark_symbols)

        # Initialize Warren Buffett analyzer
        self.warren_buffett_analyzer = get_warren_buffett_analyzer(language=language)

        # Initialize Peter Lynch analyzer
        self.peter_lynch_analyzer = get_peter_lynch_analyzer(language=language)

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
            'warren_buffett_analysis': {},
            'peter_lynch_analysis': {},
            'news_analysis': {},
            'llm_insights': {},
            'recommendation': {},
            'summary': {},
            'charts': {},
            'historical_data': None  # Add historical data for frontend charts
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

                # Convert historical data to frontend-compatible format
                results['historical_data'] = self._convert_historical_data_for_frontend(historical_data_for_charts)

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

            # Step 4.5: Warren Buffett Analysis
            task45_desc = "Performing Warren Buffett value analysis..." if self.language == 'en' else "执行沃伦·巴菲特价值分析..."
            task45 = progress.add_task(task45_desc, total=1)
            warren_buffett_analysis = self.warren_buffett_analyzer.analyze_stock(ticker, stock_info, financial_data)
            results['warren_buffett_analysis'] = warren_buffett_analysis
            progress.update(task45, completed=1)

            # Step 4.6: Peter Lynch Analysis
            task46_desc = "Performing Peter Lynch growth analysis..." if self.language == 'en' else "执行彼得·林奇成长分析..."
            task46 = progress.add_task(task46_desc, total=1)
            peter_lynch_analysis = self.peter_lynch_analyzer.analyze_stock(ticker, stock_info, financial_data)
            results['peter_lynch_analysis'] = peter_lynch_analysis
            progress.update(task46, completed=1)

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

            # Step 7: Generate LLM insights (if available and not in non-LLM mode)
            if self.llm_client and not self.non_llm_only:
                # Count available analysis types for progress tracking
                available_analyses = []
                if results['technical_analysis']:
                    available_analyses.append('technical')
                available_analyses.append('fundamental')  # Always available
                if results['warren_buffett_analysis']:
                    available_analyses.append('warren_buffett')
                if results['peter_lynch_analysis']:
                    available_analyses.append('peter_lynch')
                if news_articles:
                    available_analyses.append('news')
                available_analyses.extend(['recommendation', 'summary'])  # Always generated

                total_llm_steps = len(available_analyses)
                task7_desc = f"Generating {total_llm_steps} AI insights..." if self.language == 'en' else f"生成{total_llm_steps}个AI洞察..."
                task7 = progress.add_task(task7_desc, total=total_llm_steps)

                # Enhanced technical analysis insights with comprehensive data
                if results['technical_analysis']:
                    progress.update(task7, description="Technical AI analysis..." if self.language == 'en' else "技术分析AI洞察...")
                    console.print(f"[dim]→ Generating technical analysis insights[/dim]")

                    try:
                        # Combine technical and correlation data for LLM analysis
                        enhanced_technical_data = {
                            **results['technical_analysis'],
                            'correlation_analysis': results.get('correlation_analysis', {})
                        }
                        technical_insights = self.llm_client.generate_technical_analysis(
                            ticker, enhanced_technical_data, stock_info
                        )
                        results['llm_insights']['technical'] = technical_insights
                        console.print(f"[green]✓ Technical insights generated ({len(technical_insights)} chars)[/green]")
                    except Exception as e:
                        console.print(f"[red]✗ Technical insights failed: {e}[/red]")
                        results['llm_insights']['technical'] = f"Error: {str(e)}"

                    progress.advance(task7)

                # Fundamental analysis insights
                progress.update(task7, description="Fundamental AI analysis..." if self.language == 'en' else "基本面分析AI洞察...")
                console.print(f"[dim]→ Generating fundamental analysis insights[/dim]")

                try:
                    fundamental_insights = self.llm_client.generate_fundamental_analysis(
                        ticker, stock_info, financial_data
                    )
                    results['llm_insights']['fundamental'] = fundamental_insights
                    console.print(f"[green]✓ Fundamental insights generated ({len(fundamental_insights)} chars)[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Fundamental insights failed: {e}[/red]")
                    results['llm_insights']['fundamental'] = f"Error: {str(e)}"

                progress.advance(task7)

                # Warren Buffett analysis insights
                if results['warren_buffett_analysis']:
                    progress.update(task7, description="Warren Buffett AI analysis..." if self.language == 'en' else "巴菲特分析AI洞察...")
                    console.print(f"[dim]→ Generating Warren Buffett insights[/dim]")

                    try:
                        warren_buffett_insights = self.llm_client.generate_warren_buffett_analysis(
                            ticker, results['warren_buffett_analysis'], stock_info
                        )
                        results['llm_insights']['warren_buffett'] = warren_buffett_insights
                        console.print(f"[green]✓ Warren Buffett insights generated ({len(warren_buffett_insights)} chars)[/green]")
                    except Exception as e:
                        console.print(f"[red]✗ Warren Buffett insights failed: {e}[/red]")
                        results['llm_insights']['warren_buffett'] = f"Error: {str(e)}"

                    progress.advance(task7)

                # Peter Lynch analysis insights
                if results['peter_lynch_analysis']:
                    progress.update(task7, description="Peter Lynch AI analysis..." if self.language == 'en' else "林奇分析AI洞察...")
                    console.print(f"[dim]→ Generating Peter Lynch insights[/dim]")

                    try:
                        peter_lynch_insights = self.llm_client.generate_peter_lynch_analysis(
                            ticker, results['peter_lynch_analysis'], stock_info
                        )
                        results['llm_insights']['peter_lynch'] = peter_lynch_insights
                        console.print(f"[green]✓ Peter Lynch insights generated ({len(peter_lynch_insights)} chars)[/green]")
                    except Exception as e:
                        console.print(f"[red]✗ Peter Lynch insights failed: {e}[/red]")
                        results['llm_insights']['peter_lynch'] = f"Error: {str(e)}"

                    progress.advance(task7)

                # News sentiment analysis
                if news_articles:
                    progress.update(task7, description="News AI analysis..." if self.language == 'en' else "新闻分析AI洞察...")
                    console.print(f"[dim]→ Generating news sentiment insights from {len(news_articles)} articles[/dim]")

                    try:
                        news_insights = self.llm_client.generate_news_analysis(
                            ticker, news_articles, stock_info
                        )
                        results['llm_insights']['news'] = news_insights
                        console.print(f"[green]✓ News insights generated ({len(news_insights)} chars)[/green]")
                    except Exception as e:
                        console.print(f"[red]✗ News insights failed: {e}[/red]")
                        results['llm_insights']['news'] = f"Error: {str(e)}"

                    progress.advance(task7)

                # Overall investment recommendation
                progress.update(task7, description="Investment recommendation..." if self.language == 'en' else "投资建议生成...")
                console.print(f"[dim]→ Generating investment recommendation[/dim]")

                try:
                    investment_recommendation = self.llm_client.generate_investment_recommendation(
                        ticker, stock_info,
                        results['llm_insights'].get('technical', ''),
                        results['llm_insights'].get('fundamental', ''),
                        results['llm_insights'].get('news', '')
                    )
                    results['recommendation'] = {
                        'full_analysis': investment_recommendation
                    }
                    console.print(f"[green]✓ Investment recommendation generated ({len(investment_recommendation)} chars)[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Investment recommendation failed: {e}[/red]")
                    results['recommendation'] = {
                        'full_analysis': f"Error: {str(e)}"
                    }

                progress.advance(task7)

                # Executive summary
                progress.update(task7, description="Executive summary..." if self.language == 'en' else "执行摘要生成...")
                console.print(f"[dim]→ Generating executive summary[/dim]")

                try:
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
                    console.print(f"[green]✓ Executive summary generated ({len(executive_summary)} chars)[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Executive summary failed: {e}[/red]")
                    results['summary'] = {
                        'executive_summary': f"Error: {str(e)}"
                    }

                progress.advance(task7)

        return results

    def generate_llm_insights_only(self, base_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate only LLM insights using existing base analysis data"""
        if not self.llm_client:
            raise ValueError("LLM client not available")

        # Create a copy of base results to add LLM insights
        results = base_results.copy()
        ticker = results['ticker']
        stock_info = results.get('stock_info', {})

        # Initialize LLM insights if not present
        if 'llm_insights' not in results:
            results['llm_insights'] = {}

        console.print(f"[blue]Generating LLM insights for {ticker}...[/blue]")

        # Count available analysis types for progress tracking
        available_analyses = []
        if results.get('technical_analysis'):
            available_analyses.append('technical')
        available_analyses.append('fundamental')  # Always available
        if results.get('warren_buffett_analysis'):
            available_analyses.append('warren_buffett')
        if results.get('peter_lynch_analysis'):
            available_analyses.append('peter_lynch')
        news_articles = results.get('news_analysis', {}).get('recent_articles', [])
        if news_articles:
            available_analyses.append('news')
        available_analyses.extend(['recommendation', 'summary'])  # Always generated

        total_steps = len(available_analyses)
        console.print(f"[cyan]Will generate {total_steps} LLM analysis components[/cyan]")

        # Check if we can use parallel processing
        try:
            available_keys = self.llm_client.key_manager.get_multiple_available_keys()
            use_parallel = len(available_keys) >= 2 and len(available_analyses) >= 2
        except AttributeError:
            # Simple key manager doesn't support parallel processing
            available_keys = []
            use_parallel = False

        if use_parallel:
            console.print(f"[cyan]Using parallel processing with {len(available_keys)} keys for faster analysis[/cyan]")
            return self._generate_parallel_llm_insights(results, ticker, stock_info, news_articles)
        else:
            console.print(f"[cyan]Using sequential processing (available keys: {len(available_keys) if available_keys else 'N/A - simple key manager'})[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Starting LLM analysis...", total=total_steps)

            # Enhanced technical analysis insights
            if results.get('technical_analysis'):
                progress.update(task, description="[yellow]Generating technical analysis insights...[/yellow]")
                console.print(f"[dim]→ Processing technical indicators and correlation data[/dim]")

                try:
                    enhanced_technical_data = {
                        **results['technical_analysis'],
                        'correlation_analysis': results.get('correlation_analysis', {})
                    }

                    console.print(f"[dim]→ Calling LLM for technical analysis (this may take 30-60 seconds)[/dim]")
                    technical_insights = self.llm_client.generate_technical_analysis(
                        ticker, enhanced_technical_data, stock_info
                    )
                    results['llm_insights']['technical'] = technical_insights
                    console.print(f"[green]✓ Technical analysis insights generated ({len(technical_insights)} chars)[/green]")

                except Exception as e:
                    console.print(f"[red]✗ Technical analysis failed: {e}[/red]")
                    results['llm_insights']['technical'] = f"Error generating technical analysis: {str(e)}"

                progress.advance(task)

            # Fundamental analysis insights
            progress.update(task, description="[yellow]Generating fundamental analysis insights...[/yellow]")
            console.print(f"[dim]→ Processing fundamental metrics and stock info[/dim]")

            try:
                console.print(f"[dim]→ Calling LLM for fundamental analysis (this may take 30-60 seconds)[/dim]")
                fundamental_insights = self.llm_client.generate_fundamental_analysis(
                    ticker, stock_info, results.get('fundamental_analysis', {})
                )
                results['llm_insights']['fundamental'] = fundamental_insights
                console.print(f"[green]✓ Fundamental analysis insights generated ({len(fundamental_insights)} chars)[/green]")

            except Exception as e:
                console.print(f"[red]✗ Fundamental analysis failed: {e}[/red]")
                results['llm_insights']['fundamental'] = f"Error generating fundamental analysis: {str(e)}"

            progress.advance(task)

            # Warren Buffett analysis insights
            if results.get('warren_buffett_analysis'):
                progress.update(task, description="[yellow]Generating Warren Buffett insights...[/yellow]")
                console.print(f"[dim]→ Processing Warren Buffett value analysis[/dim]")

                try:
                    console.print(f"[dim]→ Calling LLM for Warren Buffett analysis (this may take 30-60 seconds)[/dim]")
                    warren_buffett_insights = self.llm_client.generate_warren_buffett_analysis(
                        ticker, results['warren_buffett_analysis'], stock_info
                    )
                    results['llm_insights']['warren_buffett'] = warren_buffett_insights
                    console.print(f"[green]✓ Warren Buffett insights generated ({len(warren_buffett_insights)} chars)[/green]")

                except Exception as e:
                    console.print(f"[red]✗ Warren Buffett analysis failed: {e}[/red]")
                    results['llm_insights']['warren_buffett'] = f"Error generating Warren Buffett analysis: {str(e)}"

                progress.advance(task)

            # Peter Lynch analysis insights
            if results.get('peter_lynch_analysis'):
                progress.update(task, description="[yellow]Generating Peter Lynch insights...[/yellow]")
                console.print(f"[dim]→ Processing Peter Lynch growth analysis[/dim]")

                try:
                    console.print(f"[dim]→ Calling LLM for Peter Lynch analysis (this may take 30-60 seconds)[/dim]")
                    peter_lynch_insights = self.llm_client.generate_peter_lynch_analysis(
                        ticker, results['peter_lynch_analysis'], stock_info
                    )
                    results['llm_insights']['peter_lynch'] = peter_lynch_insights
                    console.print(f"[green]✓ Peter Lynch insights generated ({len(peter_lynch_insights)} chars)[/green]")

                except Exception as e:
                    console.print(f"[red]✗ Peter Lynch analysis failed: {e}[/red]")
                    results['llm_insights']['peter_lynch'] = f"Error generating Peter Lynch analysis: {str(e)}"

                progress.advance(task)

            # News sentiment analysis
            if news_articles:
                progress.update(task, description="[yellow]Generating news sentiment analysis...[/yellow]")
                console.print(f"[dim]→ Processing {len(news_articles)} news articles[/dim]")

                try:
                    console.print(f"[dim]→ Calling LLM for news sentiment analysis (this may take 30-60 seconds)[/dim]")
                    news_insights = self.llm_client.generate_news_analysis(
                        ticker, news_articles, stock_info
                    )
                    results['llm_insights']['news'] = news_insights
                    console.print(f"[green]✓ News sentiment analysis generated ({len(news_insights)} chars)[/green]")

                except Exception as e:
                    console.print(f"[red]✗ News sentiment analysis failed: {e}[/red]")
                    results['llm_insights']['news'] = f"Error generating news analysis: {str(e)}"

                progress.advance(task)

            # Overall investment recommendation
            progress.update(task, description="[yellow]Generating investment recommendation...[/yellow]")
            console.print(f"[dim]→ Synthesizing all insights for investment recommendation[/dim]")

            try:
                console.print(f"[dim]→ Calling LLM for investment recommendation (this may take 30-60 seconds)[/dim]")
                investment_recommendation = self.llm_client.generate_investment_recommendation(
                    ticker, stock_info,
                    results['llm_insights'].get('technical', ''),
                    results['llm_insights'].get('fundamental', ''),
                    results['llm_insights'].get('news', '')
                )
                results['recommendation'] = {
                    'full_analysis': investment_recommendation
                }
                console.print(f"[green]✓ Investment recommendation generated ({len(investment_recommendation)} chars)[/green]")

            except Exception as e:
                console.print(f"[red]✗ Investment recommendation failed: {e}[/red]")
                results['recommendation'] = {
                    'full_analysis': f"Error generating investment recommendation: {str(e)}"
                }

            progress.advance(task)

            # Executive summary
            progress.update(task, description="[yellow]Generating executive summary...[/yellow]")
            console.print(f"[dim]→ Creating executive summary from all analyses[/dim]")

            try:
                console.print(f"[dim]→ Calling LLM for executive summary (this may take 30-60 seconds)[/dim]")
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
                console.print(f"[green]✓ Executive summary generated ({len(executive_summary)} chars)[/green]")

            except Exception as e:
                console.print(f"[red]✗ Executive summary failed: {e}[/red]")
                results['summary'] = {
                    'executive_summary': f"Error generating executive summary: {str(e)}"
                }

            progress.advance(task)

            progress.update(task, description="[green]LLM analysis completed![/green]")

        # Update analysis date for LLM insights
        results['llm_analysis_date'] = datetime.now().isoformat()

        return results

    def _generate_parallel_llm_insights(self, results: Dict[str, Any], ticker: str, stock_info: Dict[str, Any],
                                       news_articles: List[Dict]) -> Dict[str, Any]:
        """Generate LLM insights using parallel processing with multiple API keys"""

        # Prepare analysis requests for parallel processing
        analysis_requests = []

        # Technical analysis
        if results.get('technical_analysis'):
            enhanced_technical_data = {
                **results['technical_analysis'],
                'correlation_analysis': results.get('correlation_analysis', {})
            }
            analysis_requests.append({
                'type': 'technical',
                'method': 'generate_technical_analysis',
                'args': [ticker, enhanced_technical_data, stock_info]
            })

        # Fundamental analysis
        analysis_requests.append({
            'type': 'fundamental',
            'method': 'generate_fundamental_analysis',
            'args': [ticker, stock_info, results.get('fundamental_analysis', {})]
        })

        # Warren Buffett analysis
        if results.get('warren_buffett_analysis'):
            analysis_requests.append({
                'type': 'warren_buffett',
                'method': 'generate_warren_buffett_analysis',
                'args': [ticker, results['warren_buffett_analysis'], stock_info]
            })

        # Peter Lynch analysis
        if results.get('peter_lynch_analysis'):
            analysis_requests.append({
                'type': 'peter_lynch',
                'method': 'generate_peter_lynch_analysis',
                'args': [ticker, results['peter_lynch_analysis'], stock_info]
            })

        # News analysis
        if news_articles:
            analysis_requests.append({
                'type': 'news',
                'method': 'generate_news_analysis',
                'args': [ticker, news_articles, stock_info]
            })

        console.print(f"[cyan]Starting parallel analysis for {len(analysis_requests)} components...[/cyan]")

        # Execute parallel analysis
        parallel_results = self.llm_client.generate_parallel_analysis(analysis_requests)

        # Update results with parallel analysis outputs
        for analysis_type, result in parallel_results.items():
            results['llm_insights'][analysis_type] = result
            console.print(f"[green]✓ {analysis_type.title()} analysis completed ({len(result)} chars)[/green]")

        # Generate investment recommendation (sequential, as it depends on other analyses)
        console.print(f"[yellow]Generating investment recommendation...[/yellow]")
        try:
            investment_recommendation = self.llm_client.generate_investment_recommendation(
                ticker, stock_info,
                results['llm_insights'].get('technical', ''),
                results['llm_insights'].get('fundamental', ''),
                results['llm_insights'].get('news', '')
            )
            results['recommendation'] = {
                'full_analysis': investment_recommendation
            }
            console.print(f"[green]✓ Investment recommendation generated ({len(investment_recommendation)} chars)[/green]")
        except Exception as e:
            console.print(f"[red]✗ Investment recommendation failed: {e}[/red]")
            results['recommendation'] = {
                'full_analysis': f"Error generating investment recommendation: {str(e)}"
            }

        # Generate executive summary (sequential, as it depends on recommendation)
        console.print(f"[yellow]Generating executive summary...[/yellow]")
        try:
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
            console.print(f"[green]✓ Executive summary generated ({len(executive_summary)} chars)[/green]")
        except Exception as e:
            console.print(f"[red]✗ Executive summary failed: {e}[/red]")
            results['summary'] = {
                'executive_summary': f"Error generating executive summary: {str(e)}"
            }

        # Update analysis date for LLM insights
        results['llm_analysis_date'] = datetime.now().isoformat()

        console.print(f"[green]✓ Parallel LLM analysis completed![/green]")
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

    def _convert_historical_data_for_frontend(self, historical_data: pd.DataFrame) -> list:
        """Convert pandas DataFrame to frontend-compatible format with technical indicators"""
        try:
            # Calculate technical indicators for the frontend
            prices = historical_data['Close']
            
            # Moving averages
            sma_20 = prices.rolling(window=20).mean()
            sma_50 = prices.rolling(window=50).mean()
            sma_200 = prices.rolling(window=200).mean()
            
            # RSI calculation
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD calculation
            exp1 = prices.ewm(span=12).mean()
            exp2 = prices.ewm(span=26).mean()
            macd_line = exp1 - exp2
            macd_signal = macd_line.ewm(span=9).mean()
            macd_histogram = macd_line - macd_signal
            
            # Bollinger Bands
            bb_middle = sma_20
            bb_std = prices.rolling(window=20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            
            # Convert to list of dictionaries
            data_list = []
            for idx, row in historical_data.iterrows():
                data_point = {
                    'date': idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx),
                    'timestamp': int(idx.timestamp() * 1000) if hasattr(idx, 'timestamp') else None,
                    'open': float(row['Open']) if pd.notna(row['Open']) else None,
                    'high': float(row['High']) if pd.notna(row['High']) else None,
                    'low': float(row['Low']) if pd.notna(row['Low']) else None,
                    'close': float(row['Close']) if pd.notna(row['Close']) else None,
                    'volume': int(row['Volume']) if pd.notna(row['Volume']) else None,
                }
                
                # Add technical indicators if available
                if idx in sma_20.index and pd.notna(sma_20.loc[idx]):
                    data_point['sma_20'] = float(sma_20.loc[idx])
                if idx in sma_50.index and pd.notna(sma_50.loc[idx]):
                    data_point['sma_50'] = float(sma_50.loc[idx])
                if idx in sma_200.index and pd.notna(sma_200.loc[idx]):
                    data_point['sma_200'] = float(sma_200.loc[idx])
                if idx in rsi.index and pd.notna(rsi.loc[idx]):
                    data_point['rsi'] = float(rsi.loc[idx])
                if idx in macd_line.index and pd.notna(macd_line.loc[idx]):
                    data_point['macd_line'] = float(macd_line.loc[idx])
                if idx in macd_signal.index and pd.notna(macd_signal.loc[idx]):
                    data_point['macd_signal'] = float(macd_signal.loc[idx])
                if idx in macd_histogram.index and pd.notna(macd_histogram.loc[idx]):
                    data_point['macd_histogram'] = float(macd_histogram.loc[idx])
                if idx in bb_upper.index and pd.notna(bb_upper.loc[idx]):
                    data_point['bb_upper'] = float(bb_upper.loc[idx])
                if idx in bb_middle.index and pd.notna(bb_middle.loc[idx]):
                    data_point['bb_middle'] = float(bb_middle.loc[idx])
                if idx in bb_lower.index and pd.notna(bb_lower.loc[idx]):
                    data_point['bb_lower'] = float(bb_lower.loc[idx])
                
                data_list.append(data_point)
            
            return data_list
            
        except Exception as e:
            stock_logger.error(f"Error converting historical data for frontend: {e}")
            return []

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
        
        # Enhanced beta display - check both stock info and correlation analysis
        beta_value = stock_info.get('beta')
        correlation_analysis = results.get('correlation_analysis', {})
        beta_dict = correlation_analysis.get('beta', {})
        correlation_beta = beta_dict.get('sp500_beta') if isinstance(beta_dict, dict) else None
        
        # Use correlation beta if available and valid, otherwise use stock info beta
        display_beta = correlation_beta if correlation_beta is not None else beta_value
        beta_formatted = f"{display_beta:.3f}" if isinstance(display_beta, (int, float)) else "N/A"
        basic_table.add_row(beta_label, beta_formatted)

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
                tech_summary += f"• MACD: {trend.get('macd_trend', 'N/A')} ({histogram_label}: {histogram_formatted})\n"

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

        # Warren Buffett Value Analysis
        warren_buffett_analysis = results.get('warren_buffett_analysis', {})
        if warren_buffett_analysis:
            wb_title = "Warren Buffett Value Analysis" if self.language == 'en' else "沃伦·巴菲特价值分析"
            
            # Get key metrics
            overall_signal = warren_buffett_analysis.get('overall_signal', 'neutral')
            confidence = warren_buffett_analysis.get('confidence', 0)
            score_percentage = warren_buffett_analysis.get('score_percentage', 0)
            margin_of_safety = warren_buffett_analysis.get('margin_of_safety')
            
            # Signal color mapping
            signal_color = 'green' if overall_signal == 'bullish' else 'red' if overall_signal == 'bearish' else 'yellow'
            
            # Translate signal values
            if self.language == 'zh':
                signal_trans = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '中性'}
                overall_signal_display = signal_trans.get(overall_signal, overall_signal)
                signal_label = "投资信号"
                confidence_label = "置信度"
                quality_score_label = "质量评分"
                margin_safety_label = "安全边际"
                principles_label = "巴菲特原则"
            else:
                overall_signal_display = overall_signal.upper()
                signal_label = "Investment Signal"
                confidence_label = "Confidence"
                quality_score_label = "Quality Score"
                margin_safety_label = "Margin of Safety"
                principles_label = "Buffett Principles"
            
            wb_summary = f"[bold]{wb_title}[/bold]\n"
            wb_summary += f"{signal_label}: [{signal_color}]{overall_signal_display}[/] ({confidence_label}: {confidence:.1f}%)\n"
            wb_summary += f"{quality_score_label}: {score_percentage:.1f}%\n"
            
            if margin_of_safety is not None:
                margin_color = 'green' if margin_of_safety > 0.15 else 'yellow' if margin_of_safety > 0 else 'red'
                wb_summary += f"{margin_safety_label}: [{margin_color}]{margin_of_safety:.1%}[/]\n"
            else:
                wb_summary += f"{margin_safety_label}: N/A\n"
            
            # Add Buffett principles evaluation
            buffett_principles = warren_buffett_analysis.get('buffett_principles', {})
            if buffett_principles:
                adherence_percentage = buffett_principles.get('adherence_percentage', 0)
                overall_assessment = buffett_principles.get('overall_assessment', 'N/A')
                wb_summary += f"\n[bold]{principles_label}:[/bold]\n"
                wb_summary += f"• Overall Assessment: {overall_assessment}\n"
                wb_summary += f"• Principles Met: {buffett_principles.get('total_principles_met', 0)}/{buffett_principles.get('total_principles', 5)} ({adherence_percentage:.1f}%)\n"
                
                # Show individual principle status
                individual_principles = buffett_principles.get('individual_principles', {})
                if individual_principles:
                    for principle_name, principle_data in individual_principles.items():
                        if isinstance(principle_data, dict):
                            meets_criteria = principle_data.get('meets_criteria', False)
                            score = principle_data.get('score', 0)
                            status_icon = "✅" if meets_criteria else "❌"
                            principle_display = principle_name.replace('_', ' ').title()
                            wb_summary += f"  {status_icon} {principle_display}: {score:.0f}%\n"
            
            # Add key reasoning if available
            reasoning = warren_buffett_analysis.get('investment_reasoning', '')
            if reasoning:
                wb_summary += f"\n[bold]Key Analysis:[/bold]\n{reasoning}"
            
            console.print(Panel(wb_summary, title=wb_title))

        # Peter Lynch Growth Analysis
        peter_lynch_analysis = results.get('peter_lynch_analysis', {})
        if peter_lynch_analysis:
            pl_title = "Peter Lynch Growth Analysis" if self.language == 'en' else "彼得·林奇成长分析"
            
            # Get key metrics
            overall_signal = peter_lynch_analysis.get('overall_signal', 'neutral')
            confidence = peter_lynch_analysis.get('confidence', 0)
            score_percentage = peter_lynch_analysis.get('score_percentage', 0)
            garp_analysis = peter_lynch_analysis.get('garp_analysis', {})
            garp_score = garp_analysis.get('score_percentage', 0)
            
            # Signal color mapping
            signal_color = 'green' if overall_signal == 'bullish' else 'red' if overall_signal == 'bearish' else 'yellow'
            
            # Translate signal values
            if self.language == 'zh':
                signal_trans = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '中性'}
                overall_signal_display = signal_trans.get(overall_signal, overall_signal)
                signal_label = "投资信号"
                confidence_label = "置信度"
                quality_score_label = "质量评分"
                garp_score_label = "GARP评分"
                principles_label = "林奇原则"
            else:
                overall_signal_display = overall_signal.upper()
                signal_label = "Investment Signal"
                confidence_label = "Confidence"
                quality_score_label = "Quality Score"
                garp_score_label = "GARP Score"
                principles_label = "Lynch Principles"
            
            pl_summary = f"[bold]{pl_title}[/bold]\n"
            pl_summary += f"{signal_label}: [{signal_color}]{overall_signal_display}[/] ({confidence_label}: {confidence:.1f}%)\n"
            pl_summary += f"{quality_score_label}: {score_percentage:.1f}%\n"
            pl_summary += f"{garp_score_label}: {garp_score:.1f}%\n"
            
            # Add key GARP metrics
            garp_metrics = garp_analysis.get('metrics', {})
            if garp_metrics:
                peg_ratio = garp_metrics.get('peg_ratio') or garp_metrics.get('calculated_peg')
                if peg_ratio is not None:
                    peg_color = 'green' if peg_ratio < 1.0 else 'yellow' if peg_ratio < 1.5 else 'red'
                    pl_summary += f"PEG Ratio: [{peg_color}]{peg_ratio:.2f}[/]\n"
            
            # Add Lynch principles evaluation
            lynch_principles = peter_lynch_analysis.get('lynch_principles', {})
            if lynch_principles:
                adherence_percentage = lynch_principles.get('adherence_percentage', 0)
                overall_assessment = lynch_principles.get('overall_assessment', 'N/A')
                pl_summary += f"\n[bold]{principles_label}:[/bold]\n"
                pl_summary += f"• Overall Assessment: {overall_assessment}\n"
                pl_summary += f"• Principles Met: {lynch_principles.get('total_principles_met', 0)}/{lynch_principles.get('total_principles', 4)} ({adherence_percentage:.1f}%)\n"
                
                # Show individual principle status
                individual_principles = lynch_principles.get('individual_principles', {})
                if individual_principles:
                    for principle_name, principle_data in individual_principles.items():
                        if isinstance(principle_data, dict):
                            meets_criteria = principle_data.get('meets_criteria', False)
                            score = principle_data.get('score', 0)
                            status_icon = "✅" if meets_criteria else "❌"
                            principle_display = principle_name.replace('_', ' ').title()
                            pl_summary += f"  {status_icon} {principle_display}: {score:.0f}%\n"
            
            # Add key reasoning if available
            reasoning = peter_lynch_analysis.get('investment_reasoning', '')
            if reasoning:
                pl_summary += f"\n[bold]Key Analysis:[/bold]\n{reasoning}"
            
            console.print(Panel(pl_summary, title=pl_title))

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
            
            # Handle beta display from correlation analysis
            if isinstance(beta, dict):
                sp500_beta = beta.get('sp500_beta', 'N/A')
                beta_formatted = f"{sp500_beta:.3f}" if isinstance(sp500_beta, (int, float)) else "N/A"
            else:
                beta_formatted = f"{beta:.3f}" if isinstance(beta, (int, float)) else str(beta) if beta != 'N/A' else "N/A"
            
            corr_summary += f"{beta_label}: {beta_formatted}"

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

            if 'warren_buffett' in llm_insights:
                wb_title = "Warren Buffett's Take" if self.language == 'en' else "沃伦·巴菲特观点"
                console.print(Panel(
                    Markdown(llm_insights['warren_buffett']),
                    title=f"[bold magenta]{wb_title}[/bold magenta]"
                ))

            if 'peter_lynch' in llm_insights:
                pl_title = "Peter Lynch's Take" if self.language == 'en' else "彼得·林奇观点"
                console.print(Panel(
                    Markdown(llm_insights['peter_lynch']),
                    title=f"[bold cyan]{pl_title}[/bold cyan]"
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
            # Add token usage summary to results
            results['token_usage'] = token_tracker.get_summary()

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

    def save_base_report(self, results: Dict[str, Any], format_type: str = "json"):
        """Save base analysis report (non-LLM data) to file"""
        ticker = results['ticker']
        timestamp = results['timestamp']

        # Create reports directory in public folder if it doesn't exist
        reports_dir = "./stock-analysis-viewer/public/reports"
        os.makedirs(reports_dir, exist_ok=True)

        # Create base data (exclude LLM insights, recommendation, summary)
        base_data = {
            'ticker': results['ticker'],
            'analysis_date': results['analysis_date'],
            'timestamp': results['timestamp'],
            'stock_info': results.get('stock_info', {}),
            'technical_analysis': results.get('technical_analysis', {}),
            'correlation_analysis': results.get('correlation_analysis', {}),
            'fundamental_analysis': results.get('fundamental_analysis', {}),
            'warren_buffett_analysis': results.get('warren_buffett_analysis', {}),
            'peter_lynch_analysis': results.get('peter_lynch_analysis', {}),
            'news_analysis': results.get('news_analysis', {}),
            'charts': results.get('charts', {}),
            'historical_data': results.get('historical_data', [])
        }

        if format_type == "json":
            filename_full = f"{reports_dir}/{ticker}_analysis_base_{timestamp}.json"
            with open(filename_full, 'w') as f:
                json.dump(base_data, f, indent=2, default=str)
            filename = f"reports/{ticker}_analysis_base_{timestamp}.json"
        elif format_type == "markdown":
            filename_full = f"{reports_dir}/{ticker}_analysis_base_{timestamp}.md"
            with open(filename_full, 'w') as f:
                f.write(self._generate_markdown_report(base_data))
            filename = f"reports/{ticker}_analysis_base_{timestamp}.md"
        else:
            # Default to JSON if unknown format
            filename_full = f"{reports_dir}/{ticker}_analysis_base_{timestamp}.json"
            with open(filename_full, 'w') as f:
                json.dump(base_data, f, indent=2, default=str)
            filename = f"reports/{ticker}_analysis_base_{timestamp}.json"

        save_msg = f"Base report saved to: {filename_full}" if self.language == 'en' else f"基础报告已保存至：{filename_full}"
        console.print(f"[green]{save_msg}[/green]")
        return filename

    def save_llm_report(self, results: Dict[str, Any], format_type: str = "json"):
        """Save LLM analysis report to file"""
        ticker = results['ticker']
        timestamp = results.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))

        # Create reports directory in public folder if it doesn't exist
        reports_dir = "./stock-analysis-viewer/public/reports"
        os.makedirs(reports_dir, exist_ok=True)

        # Create LLM data (only LLM insights, recommendation, summary)
        llm_data = {
            'ticker': results['ticker'],
            'analysis_date': results['analysis_date'],
            'llm_analysis_date': results.get('llm_analysis_date', datetime.now().isoformat()),
            'timestamp': timestamp,
            'llm_insights': results.get('llm_insights', {}),
            'recommendation': results.get('recommendation', {}),
            'summary': results.get('summary', {}),
            'token_usage': token_tracker.get_summary()
        }

        if format_type == "json":
            filename_full = f"{reports_dir}/{ticker}_analysis_llm_{timestamp}.json"
            with open(filename_full, 'w') as f:
                json.dump(llm_data, f, indent=2, default=str)
            filename = f"reports/{ticker}_analysis_llm_{timestamp}.json"
        elif format_type == "markdown":
            filename_full = f"{reports_dir}/{ticker}_analysis_llm_{timestamp}.md"
            with open(filename_full, 'w') as f:
                f.write(self._generate_markdown_report(llm_data))
            filename = f"reports/{ticker}_analysis_llm_{timestamp}.md"
        else:
            # Default to JSON if unknown format
            filename_full = f"{reports_dir}/{ticker}_analysis_llm_{timestamp}.json"
            with open(filename_full, 'w') as f:
                json.dump(llm_data, f, indent=2, default=str)
            filename = f"reports/{ticker}_analysis_llm_{timestamp}.json"

        save_msg = f"LLM report saved to: {filename_full}" if self.language == 'en' else f"LLM报告已保存至：{filename_full}"
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
                md_content += f"- **MACD Signal:** {trend.get('macd_trend', 'N/A')}\n"

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
            # Handle beta display from correlation analysis for markdown
            if isinstance(beta_value, dict):
                sp500_beta = beta_value.get('sp500_beta', 'N/A')
                beta_formatted = f"{sp500_beta:.3f}" if isinstance(sp500_beta, (int, float)) else "N/A"
            else:
                beta_formatted = f"{beta_value:.3f}" if isinstance(beta_value, (int, float)) else str(beta_value) if beta_value != 'N/A' else "N/A"
            
            md_content += f"""

**Diversification Score:** {correlation.get('diversification_score', 'N/A')}  
**Beta (vs S&P 500):** {beta_formatted}  
**Risk Assessment:** {correlation.get('risk_assessment', 'N/A')}

"""

        # Add Warren Buffett Analysis
        warren_buffett_analysis = results.get('warren_buffett_analysis', {})
        if warren_buffett_analysis:
            overall_signal = warren_buffett_analysis.get('overall_signal', 'neutral')
            confidence = warren_buffett_analysis.get('confidence', 0)
            score_percentage = warren_buffett_analysis.get('score_percentage', 0)
            margin_of_safety = warren_buffett_analysis.get('margin_of_safety')
            reasoning = warren_buffett_analysis.get('investment_reasoning', '')
            
            md_content += f"""## Warren Buffett Value Analysis

**Investment Signal:** {overall_signal.upper()}  
**Confidence:** {confidence:.1f}%  
**Quality Score:** {score_percentage:.1f}%  
**Margin of Safety:** {f"{margin_of_safety:.1%}" if margin_of_safety is not None else "N/A"}  

### Buffett Principles Evaluation
"""
            
            buffett_principles = warren_buffett_analysis.get('buffett_principles', {})
            if buffett_principles:
                overall_assessment = buffett_principles.get('overall_assessment', 'N/A')
                adherence_percentage = buffett_principles.get('adherence_percentage', 0)
                total_met = buffett_principles.get('total_principles_met', 0)
                total_principles = buffett_principles.get('total_principles', 5)
                
                md_content += f"""
**Overall Assessment:** {overall_assessment}  
**Principles Met:** {total_met}/{total_principles} ({adherence_percentage:.1f}%)

| Principle | Status | Score |
|-----------|--------|-------|"""
                
                individual_principles = buffett_principles.get('individual_principles', {})
                if individual_principles:
                    for principle_name, principle_data in individual_principles.items():
                        if isinstance(principle_data, dict):
                            meets_criteria = principle_data.get('meets_criteria', False)
                            score = principle_data.get('score', 0)
                            status_icon = "✅" if meets_criteria else "❌"
                            principle_display = principle_name.replace('_', ' ').title()
                            md_content += f"\n| {principle_display} | {status_icon} | {score:.0f}% |"
                            
            if reasoning:
                md_content += f"""

### Investment Analysis
{reasoning}

"""
            
            # Add detailed analysis from each component
            fundamental_analysis = warren_buffett_analysis.get('fundamental_analysis', {})
            if fundamental_analysis:
                details = fundamental_analysis.get('details', [])
                if details:
                    md_content += f"""
### Financial Strength Analysis
"""
                    for detail in details:
                        md_content += f"- {detail}\n"
            
            consistency_analysis = warren_buffett_analysis.get('consistency_analysis', {})
            if consistency_analysis:
                details = consistency_analysis.get('details', [])
                if details:
                    md_content += f"""
### Earnings Consistency Analysis
"""
                    for detail in details:
                        md_content += f"- {detail}\n"
            
            moat_analysis = warren_buffett_analysis.get('moat_analysis', {})
            if moat_analysis:
                details = moat_analysis.get('details', [])
                if details:
                    md_content += f"""
### Economic Moat Analysis
"""
                    for detail in details:
                        md_content += f"- {detail}\n"
            
            management_analysis = warren_buffett_analysis.get('management_analysis', {})
            if management_analysis:
                details = management_analysis.get('details', [])
                if details:
                    md_content += f"""
### Management Quality Analysis
"""
                    for detail in details:
                        md_content += f"- {detail}\n"
            
            intrinsic_value_analysis = warren_buffett_analysis.get('intrinsic_value_analysis', {})
            if intrinsic_value_analysis:
                per_share_value = intrinsic_value_analysis.get('per_share_value')
                method = intrinsic_value_analysis.get('method', 'N/A')
                limitations = intrinsic_value_analysis.get('limitations', [])
                
                md_content += f"""
### Intrinsic Value Analysis
**Method:** {method}  
**Estimated Intrinsic Value per Share:** {f"${per_share_value:.2f}" if per_share_value else "N/A"}

"""
                if limitations:
                    md_content += "**Limitations:**\n"
                    for limitation in limitations:
                        md_content += f"- {limitation}\n"

        # Add Peter Lynch Analysis
        peter_lynch_analysis = results.get('peter_lynch_analysis', {})
        if peter_lynch_analysis:
            overall_signal = peter_lynch_analysis.get('overall_signal', 'neutral')
            confidence = peter_lynch_analysis.get('confidence', 0)
            score_percentage = peter_lynch_analysis.get('score_percentage', 0)
            garp_analysis = peter_lynch_analysis.get('garp_analysis', {})
            garp_score = garp_analysis.get('score_percentage', 0)
            reasoning = peter_lynch_analysis.get('investment_reasoning', '')
            
            md_content += f"""## Peter Lynch Growth Analysis

**Investment Signal:** {overall_signal.upper()}  
**Confidence:** {confidence:.1f}%  
**Quality Score:** {score_percentage:.1f}%  
**GARP Score:** {garp_score:.1f}%  

### Key GARP Metrics
"""
            
            # Add key GARP metrics
            garp_metrics = garp_analysis.get('metrics', {})
            if garp_metrics:
                peg_ratio = garp_metrics.get('peg_ratio') or garp_metrics.get('calculated_peg')
                pe_ratio = garp_metrics.get('pe_ratio')
                
                md_content += f"""
| Metric | Value | Assessment |
|--------|-------|------------|"""
                
                if peg_ratio is not None:
                    peg_assessment = "Excellent" if peg_ratio < 1.0 else "Good" if peg_ratio < 1.5 else "High"
                    md_content += f"\n| PEG Ratio | {peg_ratio:.2f} | {peg_assessment} |"
                
                if pe_ratio is not None:
                    pe_assessment = "Ideal" if 10 <= pe_ratio <= 20 else "Low" if pe_ratio < 10 else "High"
                    md_content += f"\n| P/E Ratio | {pe_ratio:.1f} | {pe_assessment} |"

            # Add Lynch principles evaluation
            lynch_principles = peter_lynch_analysis.get('lynch_principles', {})
            if lynch_principles:
                overall_assessment = lynch_principles.get('overall_assessment', 'N/A')
                adherence_percentage = lynch_principles.get('adherence_percentage', 0)
                total_met = lynch_principles.get('total_principles_met', 0)
                total_principles = lynch_principles.get('total_principles', 4)
                
                md_content += f"""

### Lynch Principles Evaluation

**Overall Assessment:** {overall_assessment}  
**Principles Met:** {total_met}/{total_principles} ({adherence_percentage:.1f}%)

| Principle | Status | Score |
|-----------|--------|-------|"""
                
                individual_principles = lynch_principles.get('individual_principles', {})
                if individual_principles:
                    for principle_name, principle_data in individual_principles.items():
                        if isinstance(principle_data, dict):
                            meets_criteria = principle_data.get('meets_criteria', False)
                            score = principle_data.get('score', 0)
                            status_icon = "✅" if meets_criteria else "❌"
                            principle_display = principle_name.replace('_', ' ').title()
                            md_content += f"\n| {principle_display} | {status_icon} | {score:.0f}% |"
                            
            if reasoning:
                md_content += f"""

### Investment Analysis
{reasoning}

"""
            
            # Add detailed analysis from each component
            growth_analysis = peter_lynch_analysis.get('growth_analysis', {})
            if growth_analysis:
                details = growth_analysis.get('details', [])
                if details:
                    md_content += f"""
### Growth Consistency Analysis
"""
                    for detail in details:
                        md_content += f"- {detail}\n"
            
            business_quality_analysis = peter_lynch_analysis.get('business_quality_analysis', {})
            if business_quality_analysis:
                details = business_quality_analysis.get('details', [])
                if details:
                    md_content += f"""
### Business Quality Analysis
"""
                    for detail in details:
                        md_content += f"- {detail}\n"
            
            market_position_analysis = peter_lynch_analysis.get('market_position_analysis', {})
            if market_position_analysis:
                details = market_position_analysis.get('details', [])
                if details:
                    md_content += f"""
### Market Position Analysis
"""
                    for detail in details:
                        md_content += f"- {detail}\n"

        # Add LLM insights
        llm_insights = results.get('llm_insights', {})
        if llm_insights:
            if llm_insights.get('technical'):
                md_content += f"""### AI Technical Analysis
{llm_insights['technical']}

"""

            if llm_insights.get('fundamental'):
                md_content += f"""## Fundamental Analysis
{llm_insights['fundamental']}

"""

            if llm_insights.get('warren_buffett'):
                md_content += f"""## Warren Buffett's Take
{llm_insights['warren_buffett']}

"""

            if llm_insights.get('peter_lynch'):
                md_content += f"""## Peter Lynch's Take
{llm_insights['peter_lynch']}

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

        # Add token usage summary
        token_summary = token_tracker.get_summary()
        if token_summary['total_calls'] > 0:
            md_content += f"""## Token Usage Summary

**Total LLM API Calls:** {token_summary['total_calls']}
**Total Input Tokens:** {token_summary['total_input_tokens']:,}
**Total Output Tokens:** {token_summary['total_output_tokens']:,}
**Total Tokens:** {token_summary['total_tokens']:,}
**Estimated Cost:** ${token_summary['total_cost']:.4f}
**Analysis Duration:** {token_summary['duration_seconds']:.1f} seconds

### Usage by Provider
"""
            for provider, stats in token_summary['by_provider'].items():
                models_str = ", ".join(stats['models'])
                md_content += f"""
**{provider.upper()}:**
- Models: {models_str}
- Calls: {stats['calls']}
- Input Tokens: {stats['input_tokens']:,}
- Output Tokens: {stats['output_tokens']:,}
- Cost: ${stats['cost']:.4f}
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
            base_path = "/llm-stock-analyzer" if os.getenv('NODE_ENV') == 'production' else ""
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
            base_path = "/llm-stock-analyzer" if os.getenv('NODE_ENV') == 'production' else ""
            chart_filename = f"{base_path}/charts/{results['ticker']}_correlation_{timestamp}.png"
            return chart_filename

        except Exception as e:
            stock_logger.error(f"Error generating correlation chart: {e}")
            return None


@click.command()
@click.option('--ticker', '-t', help='Stock ticker symbol(s) - use comma to separate multiple tickers (e.g., AAPL,MSFT,GOOGL). Optional when using --llm-only mode.')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed analysis')
@click.option('--save-report', '-s', is_flag=True, help='Save report to file')
@click.option('--charts', '-c', is_flag=True, help='Generate technical analysis charts')
@click.option('--start-date', help='Start date for analysis (YYYY-MM-DD)')
@click.option('--end-date', help='End date for analysis (YYYY-MM-DD)')
@click.option('--format', 'report_format', default='markdown', type=click.Choice(['markdown', 'json']), help='Report format')
@click.option('--llm-provider', type=click.Choice(['openai', 'gemini']), help='LLM provider to use (openai or gemini)')
@click.option('--benchmarks', help='Comma-separated list of benchmark symbols for correlation analysis')
@click.option('--chinese', is_flag=True, help='Enable Chinese language support')
@click.option('--non-llm-only', is_flag=True, help='Run only non-LLM analysis (for daily runs)')
@click.option('--llm-only', is_flag=True, help='Run only LLM analysis using existing base data (for weekly runs)')
@click.option('--base-data-path', help='Path to base analysis data file (required for --llm-only mode)')
def main(ticker, detailed, save_report, charts, start_date, end_date, report_format, llm_provider, benchmarks, chinese, non_llm_only, llm_only, base_data_path):
    """LLM Stock Analysis Tool - Comprehensive AI-powered stock analysis with enhanced technical indicators"""

    # Validate mode options
    if non_llm_only and llm_only:
        console.print("[red]Error: Cannot use both --non-llm-only and --llm-only flags together[/red]")
        return

    if llm_only and not base_data_path:
        console.print("[red]Error: --base-data-path is required when using --llm-only mode[/red]")
        return

    if llm_only and not os.path.exists(base_data_path):
        console.print(f"[red]Error: Base data file not found: {base_data_path}[/red]")
        return

    # Set global language
    language = 'zh' if chinese else 'en'
    set_language(language)

    # Validate configuration
    if not config.validate_config():
        error_msg = "Configuration validation failed. Please check your .env file." if language == 'en' else "配置验证失败。请检查您的.env文件。"
        console.print(f"[red]{error_msg}[/red]")
        sys.exit(1)

    # Handle ticker validation based on mode
    if llm_only:
        # In LLM-only mode, extract ticker from base data file if not provided
        if not ticker:
            try:
                with open(base_data_path, 'r') as f:
                    base_data = json.load(f)
                    ticker = base_data.get('ticker')
                    if not ticker:
                        console.print("[red]Error: No ticker found in base data file and none provided via --ticker[/red]")
                        sys.exit(1)
                    console.print(f"[cyan]Using ticker from base data file: {ticker}[/cyan]")
            except Exception as e:
                console.print(f"[red]Error reading base data file: {e}[/red]")
                sys.exit(1)
    else:
        # In normal mode, ticker is required
        if not ticker:
            error_msg = "Error: --ticker is required for normal analysis mode." if language == 'en' else "错误：正常分析模式需要 --ticker 参数。"
            console.print(f"[red]{error_msg}[/red]")
            sys.exit(1)

    # Parse ticker symbols - support multiple tickers separated by comma
    ticker_list = [t.strip().upper() for t in ticker.split(',') if t.strip()]

    # Validate that we have at least one ticker
    if not ticker_list:
        error_msg = "No valid ticker symbols provided." if language == 'en' else "未提供有效的股票代码。"
        console.print(f"[red]{error_msg}[/red]")
        sys.exit(1)

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
        total_stocks_label = "股票总数"
    else:
        title = "LLM Stock Analysis Tool - Enhanced Edition"
        analyzing_label = "Analyzing"
        mode_label = "Mode"
        detailed_text = "Detailed" if detailed else "Summary"
        features_label = "Features"
        features_text = "25+ Technical Indicators | Strategic Combinations | Correlation Analysis"
        total_stocks_label = "Total Stocks"

    # Display ticker list
    ticker_display = ", ".join(ticker_list)
    console.print(Panel.fit(
        f"[bold blue]{title}[/bold blue]\n"
        f"{analyzing_label}: [green]{ticker_display}[/green]\n"
        f"{total_stocks_label}: {len(ticker_list)}\n"
        f"{mode_label}: {detailed_text}\n"
        f"{features_label}: {features_text}"
    ))

    try:
        if llm_only:
            # LLM-only mode: Load base data and generate LLM insights
            console.print(f"[blue]Running LLM-only analysis using base data from: {base_data_path}[/blue]")

            # Load base data
            with open(base_data_path, 'r') as f:
                base_results = json.load(f)

            # Initialize analyzer with LLM client
            analyzer = StockAnalyzer(llm_provider=llm_provider, benchmark_symbols=benchmark_symbols, language=language)

            if not analyzer.llm_client:
                console.print("[red]Error: LLM client not available for LLM-only mode[/red]")
                return

            # Generate LLM insights for the base data
            llm_results = analyzer.generate_llm_insights_only(base_results)

            # Display results
            analyzer.display_results(llm_results, detailed=detailed)

            # Save reports if requested
            if save_report:
                # Save separate LLM report
                llm_filename = analyzer.save_llm_report(llm_results, format_type=report_format)

                # Save merged complete report (base + LLM combined)
                complete_filename = analyzer.save_report(llm_results, format_type=report_format)

                # Show summary of saved files
                console.print(f"\n[bold green]✅ Reports saved successfully:[/bold green]")
                console.print(f"[green]• LLM-only report: {llm_filename}[/green]")
                console.print(f"[green]• Complete merged report: {complete_filename}[/green]")

                merge_msg = "LLM insights have been merged with base analysis data" if language == 'en' else "LLM洞察已与基础分析数据合并"
                console.print(f"[cyan]ℹ️  {merge_msg}[/cyan]")
        else:
            # Normal or non-LLM mode
            analyzer = StockAnalyzer(
                llm_provider=None if non_llm_only else llm_provider,
                benchmark_symbols=benchmark_symbols,
                language=language,
                non_llm_only=non_llm_only
            )

            # Analyze each ticker
            for i, current_ticker in enumerate(ticker_list, 1):
                # Show progress for multiple tickers
                if len(ticker_list) > 1:
                    progress_msg = f"Processing {i}/{len(ticker_list)}: {current_ticker}" if language == 'en' else f"处理 {i}/{len(ticker_list)}: {current_ticker}"
                    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
                    console.print(f"[bold cyan]{progress_msg}[/bold cyan]")
                    console.print(f"[bold cyan]{'='*60}[/bold cyan]")

                results = analyzer.analyze_stock(
                    ticker=current_ticker,
                    detailed=detailed,
                    start_date=start_date,
                    end_date=end_date,
                    generate_charts=charts
                )

                # Display results
                analyzer.display_results(results, detailed=detailed)

                # Save report if requested
                if save_report:
                    if non_llm_only:
                        analyzer.save_base_report(results, format_type=report_format)
                    else:
                        analyzer.save_report(results, format_type=report_format)
                
            # Add spacing between multiple ticker analyses
            if len(ticker_list) > 1 and i < len(ticker_list):
                console.print("\n")

        # Display token usage summary
        console.print("\n")
        token_tracker.display_summary()

        # Summary message for multiple tickers
        if len(ticker_list) > 1:
            completion_msg = f"Analysis completed for all {len(ticker_list)} stocks." if language == 'en' else f"已完成所有 {len(ticker_list)} 只股票的分析。"
            console.print(f"\n[bold green]✅ {completion_msg}[/bold green]")

    except KeyboardInterrupt:
        interrupt_msg = "Analysis interrupted by user" if language == 'en' else "用户中断分析"
        console.print(f"\n[yellow]{interrupt_msg}[/yellow]")
        sys.exit(0)
    except Exception as e:
        error_msg = f"Error during analysis: {e}" if language == 'en' else f"分析过程中出错：{e}"
        console.print(f"\n[red]{error_msg}[/red]")
        stock_logger.error(f"Analysis error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()