#!/usr/bin/env python3
"""
Enhanced Technical Analysis Demo
Showcases all the new technical indicators, correlation analysis, and strategic combinations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.technical_indicators import get_technical_analyzer
from src.data.yahoo_finance import YahooFinanceAPI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box
import json

console = Console()

def demo_enhanced_technical_analysis():
    """Comprehensive demo of enhanced technical analysis capabilities"""

    console.print("[bold cyan]🚀 Enhanced Technical Analysis Demo[/bold cyan]", style="bold")
    console.print("Showcasing advanced indicators, correlation analysis, and strategic combinations\n")

    # Initialize clients
    yahoo_client = YahooFinanceAPI()
    analyzer = get_technical_analyzer()  # Include market benchmarks

    # Test stocks
    test_symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']

    for symbol in test_symbols:
        console.print(f"\n[bold yellow]═══ {symbol} Enhanced Technical Analysis ═══[/bold yellow]")

        try:
            # Fetch data
            historical_data = yahoo_client.get_historical_data(symbol)
            if historical_data is None or historical_data.empty:
                console.print(f"[red]❌ Could not fetch historical data for {symbol}[/red]")
                continue

            # Comprehensive technical analysis
            analysis = analyzer.analyze_technical_signals(historical_data, symbol)

            if not analysis:
                console.print(f"[red]❌ Analysis failed for {symbol}[/red]")
                continue

            # Display results
            display_enhanced_analysis(symbol, analysis)

        except Exception as e:
            console.print(f"[red]❌ Error analyzing {symbol}: {e}[/red]")
            continue

def display_enhanced_analysis(symbol: str, analysis: dict):
    """Display comprehensive analysis results"""

    # Overall Signal Panel
    overall_signal = analysis.get('overall_signal', 'neutral')
    confidence = analysis.get('confidence', 0)

    signal_color = 'green' if overall_signal == 'bullish' else 'red' if overall_signal == 'bearish' else 'yellow'

    overall_panel = Panel(
        f"[bold {signal_color}]{overall_signal.upper()}[/bold {signal_color}] ({confidence}% confidence)\n"
        f"Bullish Signals: {analysis.get('bullish_signals', 0):.1f} | "
        f"Bearish Signals: {analysis.get('bearish_signals', 0):.1f}",
        title=f"[bold]📊 {symbol} Overall Signal[/bold]",
        border_style=signal_color
    )
    console.print(overall_panel)

    # Enhanced Momentum Indicators
    display_enhanced_momentum(analysis.get('momentum', {}))

    # Ichimoku Cloud Analysis
    display_ichimoku_analysis(analysis.get('ichimoku', {}))

    # Pattern Recognition
    display_pattern_analysis(analysis.get('patterns', {}))

    # Strategic Combinations
    display_strategic_combinations(analysis.get('strategic_combinations', {}))

    # Correlation Analysis
    display_correlation_analysis(analysis.get('correlation_analysis', {}))

    # Key Technical Levels
    display_technical_levels(analysis)

def display_enhanced_momentum(momentum: dict):
    """Display enhanced momentum indicators"""
    if not momentum:
        return

    table = Table(title="🎯 Enhanced Momentum Indicators", box=box.ROUNDED)
    table.add_column("Indicator", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Signal", style="green")

    # RSI
    rsi = momentum.get('rsi', 0)
    rsi_signal = momentum.get('rsi_signal', 'neutral')
    table.add_row("RSI (14)", f"{rsi:.2f}", rsi_signal)

    # Stochastic RSI
    stochrsi = momentum.get('stochrsi_k', 0)
    stochrsi_signal = momentum.get('stochrsi_signal', 'neutral')
    table.add_row("Stochastic RSI", f"{stochrsi:.2f}", stochrsi_signal)

    # Money Flow Index
    mfi = momentum.get('mfi', 0)
    mfi_signal = momentum.get('mfi_signal', 'neutral')
    table.add_row("Money Flow Index", f"{mfi:.2f}", mfi_signal)

    # CCI
    cci = momentum.get('cci', 0)
    cci_signal = momentum.get('cci_signal', 'neutral')
    table.add_row("CCI (20)", f"{cci:.2f}", cci_signal)

    # Williams %R
    williams = momentum.get('williams_r', 0)
    williams_signal = momentum.get('williams_signal', 'neutral')
    table.add_row("Williams %R", f"{williams:.2f}", williams_signal)

    console.print(table)

def display_ichimoku_analysis(ichimoku: dict):
    """Display Ichimoku Cloud analysis"""
    if not ichimoku:
        return

    table = Table(title="☁️ Ichimoku Cloud Analysis", box=box.ROUNDED)
    table.add_column("Component", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Status", style="green")

    # Tenkan-sen (Conversion Line)
    tenkan = ichimoku.get('tenkan_sen', 0)
    table.add_row("Tenkan-sen", f"{tenkan:.2f}", "Conversion Line")

    # Kijun-sen (Base Line)
    kijun = ichimoku.get('kijun_sen', 0)
    table.add_row("Kijun-sen", f"{kijun:.2f}", "Base Line")

    # Cloud Position
    price_vs_cloud = ichimoku.get('price_vs_cloud', 'unknown')
    cloud_color = ichimoku.get('cloud_color', 'neutral')
    table.add_row("Price vs Cloud", price_vs_cloud, f"Cloud: {cloud_color}")

    # TK Cross
    tk_cross = ichimoku.get('tk_cross_signal', 'neutral')
    table.add_row("TK Cross", tk_cross, "Signal Line")

    # Overall Signal
    ichimoku_signal = ichimoku.get('ichimoku_signal', 'neutral')
    signal_color = 'green' if ichimoku_signal == 'bullish' else 'red' if ichimoku_signal == 'bearish' else 'yellow'
    table.add_row("Overall Signal", ichimoku_signal, f"[{signal_color}]●[/{signal_color}]")

    console.print(table)

def display_pattern_analysis(patterns: dict):
    """Display pattern recognition results"""
    if not patterns:
        return

    table = Table(title="📈 Pattern Recognition", box=box.ROUNDED)
    table.add_column("Pattern Type", style="cyan")
    table.add_column("Detected", style="magenta")
    table.add_column("Signal", style="green")

    # Candlestick Patterns
    table.add_row("Doji", "✓" if patterns.get('doji') else "✗", "Reversal Potential")
    table.add_row("Hammer", "✓" if patterns.get('hammer') else "✗", "Bullish Reversal")
    table.add_row("Hanging Man", "✓" if patterns.get('hanging_man') else "✗", "Bearish Reversal")
    table.add_row("Bullish Engulfing", "✓" if patterns.get('bullish_engulfing') else "✗", "Strong Bullish")
    table.add_row("Bearish Engulfing", "✓" if patterns.get('bearish_engulfing') else "✗", "Strong Bearish")

    # Gap Analysis
    gaps = patterns.get('gaps', {})
    gap_signal = gaps.get('gap_signal', 'no_gap')
    gap_size = gaps.get('gap_size', 0)
    table.add_row("Price Gap", f"{gap_size:.2f}%", gap_signal)

    # Overall Pattern Signal
    pattern_signal = patterns.get('pattern_signal', 'neutral')
    signal_color = 'green' if pattern_signal == 'bullish' else 'red' if pattern_signal == 'bearish' else 'yellow'
    table.add_row("Pattern Signal", pattern_signal, f"[{signal_color}]●[/{signal_color}]")

    console.print(table)

def display_strategic_combinations(strategies: dict):
    """Display strategic combination analysis"""
    if not strategies:
        return

    console.print("\n[bold blue]🎯 Strategic Indicator Combinations[/bold blue]")

    # RSI + MACD Strategy
    rsi_macd = strategies.get('rsi_macd_strategy', {})
    if rsi_macd:
        signal = rsi_macd.get('signal', 'neutral')
        confidence = rsi_macd.get('confidence', 0)
        reasoning = rsi_macd.get('reasoning', 'No analysis')

        signal_color = 'green' if 'buy' in signal else 'red' if 'sell' in signal else 'yellow'

        rsi_macd_panel = Panel(
            f"Signal: [{signal_color}]{signal}[/{signal_color}] ({confidence}%)\n"
            f"Reasoning: {reasoning}",
            title="RSI + MACD Strategy",
            border_style="blue"
        )
        console.print(rsi_macd_panel)

    # BB + RSI + MACD Strategy
    bb_rsi_macd = strategies.get('bb_rsi_macd_strategy', {})
    if bb_rsi_macd:
        signal = bb_rsi_macd.get('signal', 'neutral')
        confidence = bb_rsi_macd.get('confidence', 0)
        reasoning = bb_rsi_macd.get('reasoning', 'No analysis')

        signal_color = 'green' if 'buy' in signal else 'red' if 'sell' in signal else 'yellow'

        bb_panel = Panel(
            f"Signal: [{signal_color}]{signal}[/{signal_color}] ({confidence}%)\n"
            f"Reasoning: {reasoning}",
            title="Bollinger Bands + RSI + MACD",
            border_style="cyan"
        )
        console.print(bb_panel)

    # MA + RSI + Volume Strategy
    ma_rsi_vol = strategies.get('ma_rsi_volume_strategy', {})
    if ma_rsi_vol:
        signal = ma_rsi_vol.get('signal', 'neutral')
        confidence = ma_rsi_vol.get('confidence', 0)
        reasoning = ma_rsi_vol.get('reasoning', 'No analysis')

        signal_color = 'green' if 'buy' in signal else 'red' if 'sell' in signal else 'yellow'

        ma_panel = Panel(
            f"Signal: [{signal_color}]{signal}[/{signal_color}] ({confidence}%)\n"
            f"Reasoning: {reasoning}",
            title="Moving Average + RSI + Volume",
            border_style="magenta"
        )
        console.print(ma_panel)

    # Overall Strategic Signal
    overall_strategic = strategies.get('overall_strategic_signal', {})
    if overall_strategic:
        signal = overall_strategic.get('signal', 'neutral')
        confidence = overall_strategic.get('confidence', 0)
        strength = overall_strategic.get('signal_strength', 0)
        strategies_count = overall_strategic.get('strategies_analyzed', 0)

        signal_color = 'green' if signal == 'bullish' else 'red' if signal == 'bearish' else 'yellow'

        overall_panel = Panel(
            f"Consensus Signal: [{signal_color}]{signal.upper()}[/{signal_color}]\n"
            f"Confidence: {confidence:.1f}% | Strength: {strength:.1f}%\n"
            f"Strategies Analyzed: {strategies_count}",
            title="🎯 Strategic Consensus",
            border_style=signal_color
        )
        console.print(overall_panel)

def display_correlation_analysis(correlation: dict):
    """Display correlation analysis results"""
    if not correlation or 'correlations' not in correlation:
        return

    console.print("\n[bold purple]📊 Market Correlation Analysis[/bold purple]")

    correlations = correlation.get('correlations', {})

    # Short-term correlations
    short_term = correlations.get('short_term', {})
    if short_term:
        table = Table(title="Short-term Correlations (20 days)", box=box.ROUNDED)
        table.add_column("Index", style="cyan")
        table.add_column("Correlation", style="magenta")
        table.add_column("Relationship", style="green")

        for index, corr in short_term.items():
            if corr > 0.7:
                relationship = "Strong Positive"
                color = "green"
            elif corr > 0.3:
                relationship = "Moderate Positive"
                color = "yellow"
            elif corr > -0.3:
                relationship = "Weak"
                color = "white"
            elif corr > -0.7:
                relationship = "Moderate Negative"
                color = "orange"
            else:
                relationship = "Strong Negative"
                color = "red"

            table.add_row(
                index.replace('^', ''),
                f"{corr:.3f}",
                f"[{color}]{relationship}[/{color}]"
            )

        console.print(table)

    # Beta analysis
    beta = correlation.get('beta', {})
    if beta:
        beta_val = beta.get('sp500_beta', 1.0)

        if beta_val > 1.2:
            beta_desc = "High Beta (More volatile than market)"
            beta_color = "red"
        elif beta_val > 0.8:
            beta_desc = "Moderate Beta (Similar to market)"
            beta_color = "yellow"
        else:
            beta_desc = "Low Beta (Less volatile than market)"
            beta_color = "green"

        beta_panel = Panel(
            f"Beta vs S&P 500: [{beta_color}]{beta_val:.3f}[/{beta_color}]\n"
            f"{beta_desc}",
            title="📈 Beta Analysis",
            border_style="purple"
        )
        console.print(beta_panel)

    # Diversification Score
    div_score = correlation.get('diversification_score', 50)
    if div_score > 70:
        div_desc = "Excellent diversification benefit"
        div_color = "green"
    elif div_score > 50:
        div_desc = "Good diversification benefit"
        div_color = "yellow"
    else:
        div_desc = "Limited diversification benefit"
        div_color = "red"

    div_panel = Panel(
        f"Diversification Score: [{div_color}]{div_score:.1f}/100[/{div_color}]\n"
        f"{div_desc}",
        title="🎯 Portfolio Diversification",
        border_style="cyan"
    )
    console.print(div_panel)

def display_technical_levels(analysis: dict):
    """Display key technical levels"""
    sr = analysis.get('support_resistance', {})
    volatility = analysis.get('volatility', {})

    if not sr and not volatility:
        return

    console.print("\n[bold green]📏 Key Technical Levels[/bold green]")

    # Support and Resistance
    if sr:
        table = Table(title="Support & Resistance Levels", box=box.ROUNDED)
        table.add_column("Level Type", style="cyan")
        table.add_column("Price", style="magenta")
        table.add_column("Distance", style="green")

        # Resistance levels
        r1 = sr.get('resistance_1', 0)
        r2 = sr.get('resistance_2', 0)
        r3 = sr.get('resistance_3', 0)
        table.add_row("Resistance 1", f"${r1:.2f}", "Primary")
        table.add_row("Resistance 2", f"${r2:.2f}", "Secondary")
        table.add_row("Resistance 3", f"${r3:.2f}", "Strong")

        # Pivot Point
        pivot = sr.get('pivot_point', 0)
        table.add_row("Pivot Point", f"${pivot:.2f}", "Central")

        # Support levels
        s1 = sr.get('support_1', 0)
        s2 = sr.get('support_2', 0)
        s3 = sr.get('support_3', 0)
        table.add_row("Support 1", f"${s1:.2f}", "Primary")
        table.add_row("Support 2", f"${s2:.2f}", "Secondary")
        table.add_row("Support 3", f"${s3:.2f}", "Strong")

        console.print(table)

    # Bollinger Bands
    if volatility:
        bb_upper = volatility.get('bb_upper', 0)
        bb_middle = volatility.get('bb_middle', 0)
        bb_lower = volatility.get('bb_lower', 0)
        bb_position = volatility.get('bb_position', 50)

        bb_table = Table(title="Bollinger Bands Analysis", box=box.ROUNDED)
        bb_table.add_column("Band", style="cyan")
        bb_table.add_column("Price", style="magenta")
        bb_table.add_column("Status", style="green")

        bb_table.add_row("Upper Band", f"${bb_upper:.2f}", "Resistance Zone")
        bb_table.add_row("Middle Band (SMA20)", f"${bb_middle:.2f}", "Moving Average")
        bb_table.add_row("Lower Band", f"${bb_lower:.2f}", "Support Zone")
        bb_table.add_row("Position", f"{bb_position:.1f}%", "Current Location")

        console.print(bb_table)

if __name__ == "__main__":
    demo_enhanced_technical_analysis()