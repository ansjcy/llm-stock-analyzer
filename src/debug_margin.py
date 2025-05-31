from src.analysis.warren_buffett import get_warren_buffett_analyzer
from src.data.yahoo_finance import get_yahoo_finance_api

# Test with AVGO
yahoo_api = get_yahoo_finance_api()
analyzer = get_warren_buffett_analyzer()

stock_info = yahoo_api.get_stock_info('AVGO')
financial_data = yahoo_api.get_financial_data('AVGO')

print('=== KEY VALUES FOR INTRINSIC VALUE CALCULATION ===')
market_cap = stock_info.get('market_cap')
shares_outstanding = stock_info.get('shares_outstanding')
total_revenue = stock_info.get('total_revenue')
profit_margins = stock_info.get('profit_margins')
current_price = stock_info.get('current_price') or stock_info.get('regular_market_price')

print(f'Market cap: {market_cap}')
print(f'Shares outstanding: {shares_outstanding}')
print(f'Total revenue: {total_revenue}')
print(f'Profit margins: {profit_margins}')
print(f'Current price: {current_price}')

print('\n=== INTRINSIC VALUE CALCULATION ===')
intrinsic_result = analyzer._calculate_intrinsic_value(stock_info, financial_data)
print(f'Intrinsic value result: {intrinsic_result}')

if intrinsic_result.get('intrinsic_value'):
    print('\n=== MARGIN OF SAFETY CALCULATION ===')
    margin = analyzer._calculate_margin_of_safety(stock_info, intrinsic_result.get('intrinsic_value'))
    print(f'Margin of safety: {margin}')
    
    if margin is not None:
        print(f'Margin of safety percentage: {margin:.2%}')
else:
    print('\n❌ Intrinsic value calculation failed - cannot calculate margin of safety')

print('\n=== CHECKING REQUIRED VALUES ===')
print(f'Has market_cap: {market_cap is not None}')
print(f'Has shares_outstanding: {shares_outstanding is not None}')
print(f'Has total_revenue: {total_revenue is not None}')
print(f'All required for intrinsic value: {all([market_cap, shares_outstanding, total_revenue])}')

# Let's also check what keys are available in stock_info
print('\n=== RELEVANT STOCK INFO KEYS ===')
relevant_keys = ['market_cap', 'shares_outstanding', 'total_revenue', 'profit_margins', 'current_price', 'regular_market_price']
for key in relevant_keys:
    value = stock_info.get(key)
    print(f'{key}: {value}') 