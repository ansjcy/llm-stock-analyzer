#!/usr/bin/env python3
"""
Demo script for LLM Stock Analysis Tool
Shows how to use different LLM providers including Gemini
"""

import os
from src.main import StockAnalyzer

def demo_basic_analysis():
    """Demo basic analysis without LLM"""
    print("=== Demo: Basic Analysis (No LLM Required) ===")
    analyzer = StockAnalyzer()
    results = analyzer.analyze_stock("AAPL")
    
    print(f"Stock: {results['stock_info']['name']}")
    print(f"Current Price: ${results['stock_info'].get('current_price', 'N/A')}")
    print(f"Technical Signal: {results['technical_analysis'].get('overall_signal', 'N/A').upper()}")
    print(f"Articles Found: {results['news_analysis'].get('articles_found', 0)}")
    print()

def demo_with_gemini():
    """Demo analysis with Gemini (requires API key)"""
    if not os.getenv('GEMINI_API_KEY'):
        print("=== Demo: Gemini Analysis ===")
        print("To use Gemini AI analysis:")
        print("1. Get API key from: https://aistudio.google.com/app/apikey")
        print("2. Set environment variable: export GEMINI_API_KEY='your-key-here'")
        print("3. Run: python src/main.py --ticker AAPL --llm-provider gemini")
        print()
        return
    
    print("=== Demo: Gemini AI Analysis ===")
    analyzer = StockAnalyzer(llm_provider="gemini")
    results = analyzer.analyze_stock("AAPL")
    
    if results.get('llm_insights'):
        print("✓ Gemini AI analysis completed!")
        print(f"Technical Insight: {results['llm_insights'].get('technical', 'N/A')[:100]}...")
        print(f"Investment Recommendation: {results['recommendation'].get('full_analysis', 'N/A')[:100]}...")
    else:
        print("❌ Gemini analysis failed")
    print()

def demo_with_openai():
    """Demo analysis with OpenAI (requires API key)"""
    if not os.getenv('OPENAI_API_KEY'):
        print("=== Demo: OpenAI Analysis ===")
        print("To use OpenAI analysis:")
        print("1. Get API key from: https://platform.openai.com/api-keys")
        print("2. Set environment variable: export OPENAI_API_KEY='your-key-here'")
        print("3. Run: python src/main.py --ticker AAPL --llm-provider openai")
        print()
        return
    
    print("=== Demo: OpenAI Analysis ===")
    analyzer = StockAnalyzer(llm_provider="openai")
    results = analyzer.analyze_stock("AAPL")
    
    if results.get('llm_insights'):
        print("✓ OpenAI analysis completed!")
        print(f"Technical Insight: {results['llm_insights'].get('technical', 'N/A')[:100]}...")
        print(f"Investment Recommendation: {results['recommendation'].get('full_analysis', 'N/A')[:100]}...")
    else:
        print("❌ OpenAI analysis failed")
    print()

if __name__ == "__main__":
    print("LLM Stock Analysis Tool - Demo")
    print("=" * 40)
    
    demo_basic_analysis()
    demo_with_gemini()
    demo_with_openai()
    
    print("=== Command Line Examples ===")
    print("# Basic analysis (no AI):")
    print("python src/main.py --ticker AAPL")
    print()
    print("# With Gemini AI:")
    print("python src/main.py --ticker AAPL --llm-provider gemini --detailed")
    print()
    print("# With OpenAI:")
    print("python src/main.py --ticker AAPL --llm-provider openai --detailed")
    print()
    print("# Save detailed report:")
    print("python src/main.py --ticker TSLA --llm-provider gemini --detailed --save-report") 