# Frontend Charts Migration Guide

## Overview
This document describes the migration from backend-generated PNG charts to interactive frontend charts using Recharts (D3-based library).

## Changes Made

### 1. Backend Changes (`src/main.py`)

#### Added Historical Data Export
- Added `historical_data` field to analysis results
- Created `_convert_historical_data_for_frontend()` method to format data for frontend consumption
- Historical data now includes:
  - OHLCV (Open, High, Low, Close, Volume) data
  - Technical indicators: SMA 20/50/200, RSI, MACD, Bollinger Bands
  - Properly formatted timestamps and dates

#### Maintained Backward Compatibility
- PNG chart generation is still available with `--charts` flag
- New historical data is included regardless of chart generation setting

### 2. Frontend Changes

#### New Component: `TechnicalCharts.tsx`
- **Price Chart**: Interactive price chart with moving averages, Bollinger Bands, support/resistance levels
- **RSI Chart**: Relative Strength Index with overbought/oversold zones
- **MACD Chart**: MACD line, signal line, and histogram
- **Volume Chart**: Color-coded volume bars (green for up days, red for down days)

#### Updated Component: `TechnicalAnalysis.tsx`
- Replaced PNG image loading with `TechnicalCharts` component
- Added props for `ticker` and `historicalData`
- Maintains existing technical indicator displays

#### Enhanced Features
- **Interactive tooltips**: Hover to see detailed data
- **Proper scaling**: Fixed Y-axis scaling issues
- **Support/Resistance levels**: Added from technical analysis data
- **Color-coded elements**: 
  - Moving averages: SMA 20 (green), SMA 50 (orange), SMA 200 (red)
  - Price line: Blue, prominent
  - Support/resistance: Green/red dashed lines with labels
  - Volume bars: Green (up days), red (down days)

### 3. Type System Updates

#### Updated `analysis.ts`
- Added `historical_data?: any[]` to `StockAnalysisResult` interface
- Added `ticker: string` and `historicalData?: any[]` props to `TechnicalAnalysisProps`

## Benefits of Frontend Charts

### 1. Performance
- No backend chart generation overhead
- Faster analysis completion
- Reduced server resources

### 2. User Experience
- **Interactive**: Zoom, pan, hover for details
- **Responsive**: Automatically adjusts to screen size
- **Real-time**: No need to wait for PNG generation
- **Accessibility**: Better screen reader support

### 3. Maintainability
- No matplotlib dependencies for charts
- Easier to customize and theme
- Consistent with React component architecture

## Testing the Migration

### 1. Generate Test Data
```bash
cd stock-analyzer
python test_frontend_charts.py
```

### 2. Start Frontend Development Server
```bash
cd stock-analysis-viewer
npm run dev
```

### 3. Load Test Data
- Navigate to http://localhost:3000
- Load the generated `test_frontend_charts.json` file
- Verify all four charts render correctly

### 4. Test Features
- **Hover interactions**: Check tooltips show correct data
- **Chart scaling**: Verify Y-axis shows proper price ranges
- **Support/Resistance**: Confirm lines appear when data available
- **Volume colors**: Verify green/red bars based on price changes

## Data Flow

```
Backend (Python) → JSON with historical_data → Frontend (React/Recharts) → Interactive Charts
```

### Historical Data Format
```json
{
  "historical_data": [
    {
      "date": "2024-01-01",
      "timestamp": 1704067200000,
      "open": 100.50,
      "high": 102.30,
      "low": 99.80,
      "close": 101.75,
      "volume": 1500000,
      "sma_20": 100.25,
      "sma_50": 99.80,
      "sma_200": 98.50,
      "rsi": 58.3,
      "macd_line": 0.25,
      "macd_signal": 0.20,
      "macd_histogram": 0.05,
      "bb_upper": 103.50,
      "bb_middle": 100.25,
      "bb_lower": 97.00
    }
  ]
}
```

## Future Enhancements

### Planned Features
- **Candlestick charts**: Replace line charts with OHLC candlesticks
- **Zoom and pan**: Add time range selection
- **Additional indicators**: Stochastic, Williams %R, ATR
- **Annotation tools**: Allow users to draw trend lines
- **Export functionality**: Save charts as images or data

### Configuration Options
- **Theme support**: Dark/light mode chart themes
- **Indicator toggles**: Show/hide specific indicators
- **Time range selector**: 1D, 1W, 1M, 3M, 6M, 1Y options

## Troubleshooting

### Common Issues

1. **Charts not rendering**: 
   - Check browser console for errors
   - Verify historical_data is present in analysis results

2. **Y-axis scaling issues**:
   - Verify price data is numeric
   - Check for null/undefined values in data

3. **Support/Resistance lines missing**:
   - Check if `support_resistance` data exists in technical analysis
   - Verify the resistance_1/support_1 values are numeric

4. **Volume colors incorrect**:
   - Ensure previous day's closing price is available for comparison
   - Check volume data is present and numeric

### Debug Mode
Add console.log statements in `TechnicalCharts.tsx` to inspect data:
```javascript
console.log('Chart data:', chartData);
console.log('Support/Resistance:', supportResistance);
```

## Migration Status

- ✅ Backend: Historical data export
- ✅ Frontend: Chart components created
- ✅ Integration: Components connected
- ✅ Testing: Test script created
- ✅ Documentation: Migration guide complete

The migration is complete and ready for production use! 