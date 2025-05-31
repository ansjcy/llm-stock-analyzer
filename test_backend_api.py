#!/usr/bin/env python3
"""
Test script to verify backend API is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import StockAnalyzer
import json

def test_backend_api():
    """Test the backend API with AAPL"""
    
    print("Testing Backend API with AAPL")
    print("=" * 40)
    
    try:
        # Initialize analyzer
        analyzer = StockAnalyzer()
        
        # Test with AAPL
        result = analyzer.analyze_stock('AAPL')
        print(f'✅ API call successful')
        print(f'Keys in result: {list(result.keys())}')

        if 'technical_analysis' in result:
            tech = result['technical_analysis']
            print(f'✅ Technical analysis present')
            
            if 'correlation_analysis' in tech:
                corr = tech['correlation_analysis']
                print(f'✅ Correlation analysis present')
                print(f'Correlation analysis keys: {list(corr.keys())}')
                
                correlations = corr.get('correlations', {})
                print(f'Timeframes available: {list(correlations.keys())}')
                
                total_low_corr = 0
                for timeframe, data in correlations.items():
                    if data:
                        print(f'{timeframe}: {len(data)} correlations')
                        # Check for low correlation assets
                        low_corr = sum(1 for corr in data.values() if abs(corr) < 0.6)
                        total_low_corr += low_corr
                        print(f'  Low correlation assets (<60%): {low_corr}')
                
                print(f'\n✅ Total diversification opportunities: {total_low_corr}')
                
                # Check diversification recommendations
                div_recs = corr.get('diversification_recommendations', [])
                print(f'✅ Diversification recommendations: {len(div_recs)}')
                for i, rec in enumerate(div_recs, 1):
                    print(f'  {i}. {rec}')
                
            else:
                print('❌ No correlation_analysis in technical_analysis')
        else:
            print('❌ No technical_analysis in result')
            
        # Also check the separate correlation_analysis field
        if 'correlation_analysis' in result:
            corr_separate = result['correlation_analysis']
            print(f'\n✅ Separate correlation_analysis field present')
            print(f'Keys: {list(corr_separate.keys())}')
        
        print("\n" + "=" * 40)
        print("✅ BACKEND API TEST COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"❌ Error in backend API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backend_api() 