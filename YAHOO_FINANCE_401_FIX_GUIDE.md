# Yahoo Finance 401 Error Fix Guide

## Overview
This guide provides comprehensive solutions for bypassing Yahoo Finance 401 Unauthorized errors that commonly occur when using the `yfinance` library.

## What Was Fixed

### 1. Enhanced User-Agent Rotation
- **Before**: Limited to 5 basic user agents
- **After**: 10+ realistic, recent browser user agents including Chrome, Firefox, Safari, and Edge
- **Impact**: Reduces detection as automated traffic

### 2. Browser-Like Headers
- **Added**: Complete set of browser headers (Accept, Accept-Language, Accept-Encoding, etc.)
- **Added**: Security headers (Sec-Fetch-*, DNT, etc.)
- **Added**: Random Referer header injection
- **Impact**: Requests appear more like real browser traffic

### 3. Intelligent Rate Limiting
- **Added**: Minimum 1-second delay between requests with random jitter
- **Added**: Progressive backoff for different error types
- **Added**: Special handling for 401 and 429 errors
- **Impact**: Reduces likelihood of being rate-limited or blocked

### 4. Session Management
- **Added**: Session reset after multiple failures
- **Added**: Proper session cleanup and recreation
- **Impact**: Avoids session-based blocking

### 5. Caching and Fallback System
- **Added**: Daily caching of successful requests
- **Added**: Yesterday's data as fallback when current requests fail
- **Added**: Cache directory: `cache/yahoo_finance/`
- **Impact**: Reduces API calls and provides data continuity

### 6. Enhanced Error Handling
- **Added**: Specific handling for 401, 429, and other HTTP errors
- **Added**: Alternative access methods when primary method fails
- **Added**: Increased retry attempts (5 instead of 3)
- **Impact**: Better resilience against temporary blocks

## Usage

### Basic Usage (Automatic)
The fixes are automatically applied when using the existing API:

```python
from src.data.yahoo_finance import get_yahoo_finance_api

api = get_yahoo_finance_api()
stock_info = api.get_stock_info('TSLA')  # Now with enhanced anti-blocking
```

### Testing the Fixes
Run the test script to verify the fixes work:

```bash
python test_yahoo_fix.py
```

### Environment Variables (Optional)

#### Proxy Support
If you have access to a proxy server, set:
```bash
export YAHOO_FINANCE_PROXY="http://your-proxy-server:port"
```

#### Cache Directory
The system automatically creates `cache/yahoo_finance/` for caching.

## Advanced Bypass Techniques

### 1. VPN/Proxy Rotation
If 401 errors persist, consider:
- Using a VPN service
- Rotating proxy servers
- Using residential proxies

### 2. Request Timing
- The system now implements intelligent delays
- Avoid making rapid successive requests
- Consider running analysis during off-peak hours

### 3. Alternative Data Sources
If Yahoo Finance continues to block, consider:
- Alpha Vantage API
- Financial Modeling Prep API
- IEX Cloud API
- Polygon.io API

## Troubleshooting

### Still Getting 401 Errors?

1. **Check your IP**: Your IP might be temporarily blocked
   ```bash
   curl -I "https://finance.yahoo.com"
   ```

2. **Clear cache**: Remove old cache files
   ```bash
   rm -rf cache/yahoo_finance/
   ```

3. **Use proxy**: Set the YAHOO_FINANCE_PROXY environment variable

4. **Wait and retry**: Sometimes waiting 15-30 minutes helps

### Error Types and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | IP/User-Agent blocked | Use proxy, wait, or try VPN |
| 429 Too Many Requests | Rate limit exceeded | Increase delays, reduce frequency |
| 403 Forbidden | Geographic restriction | Use VPN from different region |
| Timeout | Network issues | Check internet connection |

## Monitoring and Logging

The enhanced system provides detailed logging:
- Cache hits/misses
- Retry attempts with different user agents
- Fallback to yesterday's data
- Success/failure rates

Check logs in `logs/stock_analysis.log` for detailed information.

## Best Practices

1. **Don't abuse the API**: Respect rate limits
2. **Use caching**: Let the system cache data to reduce requests
3. **Monitor logs**: Watch for patterns in failures
4. **Have fallbacks**: Always have alternative data sources ready
5. **Update regularly**: Keep user agents and headers current

## Alternative Solutions

If the enhanced fixes don't work, consider these alternatives:

### 1. yfinance-cache
```bash
pip install yfinance-cache
```

### 2. yahooquery
```bash
pip install yahooquery
```

### 3. Direct API calls
Implement direct calls to Yahoo Finance's internal APIs (more complex but more reliable).

## Support

If you continue experiencing issues:
1. Check the logs for specific error messages
2. Try the test script to isolate the problem
3. Consider using alternative data sources
4. Update the user agents if they become outdated

## Updates

This fix was implemented on 2025-06-12. User agents and techniques may need updates as Yahoo Finance changes their blocking mechanisms.
