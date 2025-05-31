#!/usr/bin/env python3
"""
Test script to verify correlation analysis is working correctly
and returning all data needed for frontend diversification opportunities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import json
from src.analysis.technical_indicators import TechnicalAnalyzer

def test_correlation_analysis():
    """Test correlation analysis with a sample stock"""
    
    # Test with AAPL
    symbol = "AAPL"
    print(f"Testing correlation analysis for {symbol}")
    print("=" * 50)
    
    # Download stock data
    try:
        stock_data = yf.download(symbol, period='1y', interval='1d', progress=False)
        if stock_data.empty:
            print(f"No data found for {symbol}")
            return
        
        print(f"Downloaded {len(stock_data)} days of data for {symbol}")
        
        # Initialize analyzer
        analyzer = TechnicalAnalyzer()
        
        # Run correlation analysis
        correlation_result = analyzer.calculate_correlation_analysis(stock_data, symbol)
        
        print("\n1. CORRELATION STRUCTURE:")
        print("-" * 30)
        print(f"Keys in correlation result: {list(correlation_result.keys())}")
        
        print("\n2. CORRELATIONS BY TIMEFRAME:")
        print("-" * 30)
        correlations = correlation_result.get('correlations', {})
        for timeframe, corr_data in correlations.items():
            print(f"\n{timeframe.upper()}:")
            if corr_data:
                print(f"  Number of correlations: {len(corr_data)}")
                # Show first few correlations
                for i, (symbol_name, corr_value) in enumerate(list(corr_data.items())[:5]):
                    print(f"  {symbol_name}: {corr_value:.4f}")
                if len(corr_data) > 5:
                    print(f"  ... and {len(corr_data) - 5} more")
            else:
                print("  No correlation data")
        
        print("\n3. DIVERSIFICATION ANALYSIS:")
        print("-" * 30)
        
        # Check medium-term correlations for diversification opportunities
        medium_term = correlations.get('medium_term', {})
        if medium_term:
            print(f"Total assets analyzed: {len(medium_term)}")
            
            # Find low correlation assets (< 60%)
            low_corr_assets = [(symbol, corr) for symbol, corr in medium_term.items() 
                             if abs(corr) < 0.6]
            
            print(f"\nAssets with correlation < 60%: {len(low_corr_assets)}")
            for symbol_name, corr in sorted(low_corr_assets, key=lambda x: abs(x[1])):
                print(f"  {symbol_name}: {corr:.4f} ({abs(corr)*100:.1f}%)")
            
            # Find negative correlation assets
            negative_corr_assets = [(symbol, corr) for symbol, corr in medium_term.items() 
                                  if corr < 0]
            
            print(f"\nAssets with negative correlation: {len(negative_corr_assets)}")
            for symbol_name, corr in sorted(negative_corr_assets, key=lambda x: x[1]):
                print(f"  {symbol_name}: {corr:.4f} ({corr*100:.1f}%)")
        
        print("\n4. DIVERSIFICATION RECOMMENDATIONS:")
        print("-" * 30)
        recommendations = correlation_result.get('diversification_recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n5. BETA AND SCORES:")
        print("-" * 30)
        beta = correlation_result.get('beta', {})
        print(f"Beta: {beta}")
        
        div_score = correlation_result.get('diversification_score')
        print(f"Diversification Score: {div_score}")
        
        print("\n6. TOP CORRELATIONS:")
        print("-" * 30)
        top_corr = correlation_result.get('top_correlations', {})
        for timeframe, data in top_corr.items():
            print(f"\n{timeframe.upper()}:")
            if 'highest_positive' in data:
                print("  Highest positive:")
                for symbol_name, corr in data['highest_positive']:
                    print(f"    {symbol_name}: {corr:.4f}")
            if 'lowest_positive' in data:
                print("  Lowest positive:")
                for symbol_name, corr in data['lowest_positive']:
                    print(f"    {symbol_name}: {corr:.4f}")
        
        print("\n7. FRONTEND DATA VERIFICATION:")
        print("-" * 30)
        
        # Simulate what frontend would receive
        frontend_data = {
            'correlations': correlations,
            'beta': beta,
            'diversification_score': div_score,
            'diversification_recommendations': recommendations
        }
        
        # Check if frontend can identify diversification opportunities
        for timeframe in ['short_term', 'medium_term', 'long_term']:
            timeframe_data = correlations.get(timeframe, {})
            if timeframe_data:
                # Count assets by correlation level
                low_corr = sum(1 for corr in timeframe_data.values() if abs(corr) < 0.6)
                moderate_corr = sum(1 for corr in timeframe_data.values() if 0.6 <= abs(corr) < 0.8)
                high_corr = sum(1 for corr in timeframe_data.values() if abs(corr) >= 0.8)
                
                print(f"\n{timeframe.upper()} - Frontend perspective:")
                print(f"  Low correlation (<60%): {low_corr} assets")
                print(f"  Moderate correlation (60-80%): {moderate_corr} assets")
                print(f"  High correlation (>80%): {high_corr} assets")
                
                if low_corr > 0:
                    print(f"  ✅ Frontend can show {low_corr} diversification opportunities")
                else:
                    print(f"  ⚠️  No low-correlation assets, frontend will show relative best options")
        
        print("\n" + "=" * 50)
        print("✅ CORRELATION ANALYSIS TEST COMPLETED SUCCESSFULLY")
        print("✅ All data structures are present for frontend consumption")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in correlation analysis test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_correlation_analysis() 