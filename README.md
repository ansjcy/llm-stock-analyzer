# LLM Stock Analyzer

A comprehensive stock analysis tool powered by Large Language Models (LLMs) that provides multi-dimensional investment insights combining technical analysis, fundamental analysis, and AI-powered market intelligence.

## 🚀 Features

- **🤖 Multi-LLM Support**: Compatible with OpenAI GPT, Google Gemini, Anthropic Claude, and Groq
- **📊 Comprehensive Analysis**: Technical indicators, fundamental metrics, news sentiment, and correlation analysis
- **💡 Investment Strategies**: Warren Buffett value investing and Peter Lynch growth investing methodologies
- **🔄 Workflow Automation**: Separate daily base analysis and weekly LLM insights for cost optimization
- **🎨 Interactive Visualization**: Modern React-based dashboard for exploring analysis results
- **🌍 Multi-language Support**: English and Chinese language interfaces
- **📄 Flexible Output**: JSON, Markdown, and interactive web reports with automatic merging
- **⚡ Performance Optimized**: Parallel processing, caching, and intelligent rate limiting
- **🤖 GitHub Actions**: Automated daily/weekly analysis with deployment to GitHub Pages

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#installation)
- [Configuration](#️-configuration)
- [Workflow Automation](#-workflow-automation)
- [Analysis Components](#-analysis-components)
- [Command Line Interface](#-command-line-interface)
- [Web Interface](#-web-interface)
- [API Integration](#-api-integration)
- [Output Formats](#-output-formats)
- [Performance Optimization](#-performance-optimization)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+** (for web interface)
- **At least one LLM API key** (OpenAI, Gemini, Claude, or Groq)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd llm-stock-analyzer
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Install frontend dependencies** (optional)
   ```bash
   cd stock-analysis-viewer
   npm install
   cd ..
   ```

### Basic Usage

**Analyze a stock with AI insights:**
```bash
python src/main.py --ticker AAPL --detailed --save-report
```

**Generate base analysis without AI (faster, for daily automation):**
```bash
python src/main.py --ticker AAPL --non-llm-only --save-report
```

**Generate LLM insights from existing base analysis (for weekly automation):**
```bash
python src/main.py --llm-only --base-data-path reports/AAPL_analysis_base_20240101_120000.json --save-report
```

**View results in web interface:**
```bash
cd stock-analysis-viewer
npm run dev
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# LLM API Keys (at least one required for AI analysis)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Default LLM provider
DEFAULT_LLM_PROVIDER=gemini

# Analysis configuration
TECHNICAL_ANALYSIS_PERIOD=252
SAVE_REPORTS=true
REPORTS_DIR=./stock-analysis-viewer/public/reports
```

### Multiple API Keys for Better Performance

For improved rate limiting and parallel processing:

```env
# Multiple Gemini keys for load balancing
GEMINI_API_KEYS=key1_here,key2_here,key3_here
```

## 🔄 Workflow Automation

The LLM Stock Analyzer supports efficient automation workflows that separate data collection from AI analysis, optimizing both cost and performance.

### 📅 Daily + Weekly Automation Pattern

**Recommended approach for production use:**

#### Daily Base Analysis (Monday-Friday)
```bash
# Generate base analysis without LLM (fast, cost-effective)
python src/main.py --ticker AAPL,MSFT,GOOGL --non-llm-only --save-report --format json
```

**Output:** `{TICKER}_analysis_base_{TIMESTAMP}.json`
- Technical indicators and market data
- Fundamental analysis metrics
- News sentiment analysis
- No AI insights (saves time and API costs)

#### Weekly LLM Analysis (Sunday)
```bash
# Generate AI insights from latest base analysis (enhanced mode)
python src/main.py --llm-only --base-data-path reports/AAPL_analysis_base_20240101_120000.json --save-report
```

**Output:**
- `{TICKER}_analysis_llm_{TIMESTAMP}.json` (LLM insights only)
- `{TICKER}_analysis_{TIMESTAMP}.json` (Complete merged report)

### 🚀 Batch Processing Script

For processing multiple tickers automatically:

```bash
# Process all tickers with recent base files
python scripts/weekly_llm_analysis.py --all-recent

# Process specific tickers
python scripts/weekly_llm_analysis.py --tickers AAPL,MSFT,GOOGL

# Process files from last 3 days
python scripts/weekly_llm_analysis.py --all-recent --days 3
```

### 🤖 GitHub Actions Integration

The project includes automated workflows:

- **Daily Workflow**: Generates base analysis files (Monday-Friday)
- **Weekly Workflow**: Generates LLM insights and merged reports (Sunday)
- **Legacy Workflow**: Manual trigger with multiple modes

### 📁 File Structure

```
reports/
├── AAPL_analysis_base_20240108_130000.json    # Daily base data
├── AAPL_analysis_llm_20240114_140000.json     # Weekly LLM insights
├── AAPL_analysis_20240114_140000.json         # Weekly merged complete
├── MSFT_analysis_base_20240108_130000.json
└── ...
```

### ✅ Benefits

- **Cost Optimization**: LLM analysis only runs weekly
- **Performance**: Daily base analysis is fast and reliable
- **Flexibility**: Can generate complete reports on-demand
- **Automation**: GitHub Actions handle scheduling automatically
- **Scalability**: Easy to add more tickers or adjust frequency

## 📊 Analysis Components

### 1. 📈 Technical Analysis
- **Moving Averages**: SMA, EMA with trend analysis
- **Momentum Indicators**: RSI, Stochastic, Williams %R
- **Trend Indicators**: MACD, ADX, Parabolic SAR
- **Volatility**: Bollinger Bands, ATR
- **Volume Analysis**: OBV, Volume SMA
- **Strategic Combinations**: Multi-indicator strategies with confidence scoring

### 2. 💰 Fundamental Analysis
- **Valuation Metrics**: P/E, P/B, P/S, PEG ratios
- **Financial Health**: Debt ratios, liquidity ratios
- **Profitability**: ROE, ROA, margins
- **Growth Metrics**: Revenue and earnings growth

### 3. 🎯 Investment Strategies

#### Warren Buffett Value Analysis
- **Financial Strength**: ROE, debt levels, margins, liquidity
- **Earnings Consistency**: Revenue and earnings growth patterns
- **Economic Moat**: Competitive advantages and market position
- **Management Quality**: Capital allocation and shareholder returns
- **Intrinsic Value**: DCF-based valuation with margin of safety

#### Peter Lynch Growth Analysis
- **GARP Metrics**: Growth at Reasonable Price evaluation
- **Growth Consistency**: Revenue and earnings growth patterns
- **Business Quality**: Financial health and operational efficiency
- **Market Position**: Market cap category and growth potential

### 4. 🌐 Market Intelligence
- **News Sentiment**: Recent news analysis and sentiment scoring
- **Correlation Analysis**: Market correlation and beta calculation
- **AI Insights**: LLM-powered interpretation of all metrics

## 💻 Command Line Interface

### Basic Commands

```bash
# Analyze single stock
python src/main.py --ticker AAPL

# Detailed analysis with charts
python src/main.py --ticker AAPL --detailed --charts

# Multiple stocks
python src/main.py --ticker AAPL,GOOGL,MSFT

# Specify date range
python src/main.py --ticker AAPL --start-date 2023-01-01 --end-date 2023-12-31

# Choose LLM provider
python src/main.py --ticker AAPL --llm-provider openai

# Chinese language output
python src/main.py --ticker AAPL --language zh

# Save reports in different formats
python src/main.py --ticker AAPL --save-report --format json
python src/main.py --ticker AAPL --save-report --format markdown
```

### Advanced Options

```bash
# Benchmark correlation analysis
python src/main.py --ticker AAPL --benchmark-symbols "^GSPC,^DJI,^IXIC"

# Generate base analysis only (for daily automation)
python src/main.py --ticker AAPL --non-llm-only --save-report

# Generate LLM insights from existing base analysis (enhanced mode)
python src/main.py --llm-only --base-data-path reports/AAPL_analysis_base_20240101_120000.json --save-report

# Auto-detect ticker from base file (no need to specify --ticker)
python src/main.py --llm-only --base-data-path reports/AAPL_analysis_base_20240101_120000.json --save-report
```

### Workflow-Specific Commands

```bash
# Daily automation (fast, no LLM costs)
python src/main.py --ticker AAPL,MSFT,GOOGL --non-llm-only --save-report --format json

# Weekly LLM batch processing
python scripts/weekly_llm_analysis.py --all-recent

# Manual complete analysis (traditional mode)
python src/main.py --ticker AAPL --save-report --format json
```

## 🎨 Web Interface

The project includes a modern React-based web interface for interactive analysis exploration.

### Features
- **📊 Interactive Charts**: Technical analysis with multiple timeframes and indicators
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **🌙 Dark/Light Theme**: User preference support with system detection
- **🌍 Multi-language**: English and Chinese support
- **📁 Report Management**: Browse and load historical analyses
- **🔍 Advanced Filtering**: Search and filter analysis reports
- **📈 Real-time Updates**: Live data integration capabilities

### Setup

```bash
cd stock-analysis-viewer
npm install
npm run dev
```

The interface will be available at `http://localhost:3000`.

### Production Deployment

```bash
cd stock-analysis-viewer
npm run build
npm start
```

For detailed frontend documentation, see [stock-analysis-viewer/README.md](stock-analysis-viewer/README.md).

## 🔌 API Integration

### Supported Data Sources
- **Yahoo Finance**: Primary data source for stock information and historical data
- **Financial Modeling Prep**: Alternative financial data source (optional)
- **News APIs**: NewsAPI, Finnhub for sentiment analysis

### LLM Providers
- **OpenAI**: GPT-3.5, GPT-4 models with function calling
- **Google Gemini**: Gemini Pro, Gemini Flash models with high rate limits
- **Anthropic Claude**: Claude 3 models for detailed analysis
- **Groq**: Fast inference with Llama models

### Rate Limiting & Performance
- **Intelligent Rate Limiting**: Automatic throttling based on provider limits
- **Key Rotation**: Multiple API keys for load balancing
- **Retry Logic**: Exponential backoff with jitter
- **Parallel Processing**: Concurrent analysis for multiple components

## 📄 Output Formats

### File Types

The analyzer generates different file types based on the analysis mode:

#### Base Analysis Files
```
{TICKER}_analysis_base_{TIMESTAMP}.json
```
Contains non-LLM data: technical indicators, fundamental metrics, news sentiment.

#### LLM Analysis Files
```
{TICKER}_analysis_llm_{TIMESTAMP}.json
```
Contains only LLM-generated insights and recommendations.

#### Complete Merged Files
```
{TICKER}_analysis_{TIMESTAMP}.json
```
Contains both base data and LLM insights - ready for frontend consumption.

### JSON Structure

#### Complete Analysis Report
```json
{
  "ticker": "AAPL",
  "analysis_date": "2024-01-09T10:00:00Z",
  "timestamp": "20240109_100000",
  "stock_info": {...},
  "technical_analysis": {...},
  "fundamental_analysis": {...},
  "warren_buffett_analysis": {...},
  "peter_lynch_analysis": {...},
  "news_analysis": {...},
  "llm_insights": {
    "technical_analysis": "...",
    "fundamental_analysis": "...",
    "investment_recommendation": "...",
    "summary": "..."
  },
  "recommendation": {...},
  "summary": {...}
}
```

#### Base Analysis Report (Non-LLM)
```json
{
  "ticker": "AAPL",
  "analysis_date": "2024-01-09T10:00:00Z",
  "timestamp": "20240109_100000",
  "stock_info": {...},
  "technical_analysis": {...},
  "fundamental_analysis": {...},
  "warren_buffett_analysis": {...},
  "peter_lynch_analysis": {...},
  "news_analysis": {...},
  "charts": {...},
  "historical_data": [...]
}
```

### Markdown Reports
Human-readable reports with formatted tables and analysis summaries.

### Interactive Web Reports
Rich web interface with:
- Interactive charts and visualizations
- Detailed breakdowns of all analysis components
- Support for both merged and separate file loading
- Export capabilities
- Shareable links

## ⚡ Performance Optimization

### Parallel Processing
- **Multi-key Support**: Use multiple API keys for parallel LLM analysis
- **Concurrent Data Fetching**: Simultaneous data retrieval from multiple sources
- **Asynchronous Processing**: Non-blocking operations for improved speed

### Caching Strategy
- **Financial Data Caching**: Reduce redundant API calls
- **Configurable Duration**: Customizable cache expiration
- **Intelligent Invalidation**: Smart cache refresh based on market hours

### Memory Management
- **Efficient Data Structures**: Optimized pandas operations
- **Streaming Processing**: Handle large datasets without memory issues
- **Garbage Collection**: Automatic cleanup of temporary data

## 🔧 Troubleshooting

### Common Issues

**1. API Key Errors**
```bash
# Verify API keys are configured
python -c "from src.utils.config import config; print(config.validate_config())"
```

**2. Missing Dependencies**
```bash
# Install all dependencies
pip install -r requirements.txt

# For TA-Lib (optional, for advanced technical analysis)
# macOS: brew install ta-lib
# Ubuntu: sudo apt-get install ta-lib-dev
# Then: pip install ta-lib
```

**3. Data Fetching Issues**
- Check internet connection
- Verify ticker symbols are valid (use Yahoo Finance format)
- Some data may be delayed or unavailable for certain stocks
- Try different time periods if historical data is limited

**4. LLM Analysis Timeouts**
```bash
# Increase timeout values in .env
LLM_ANALYSIS_TIMEOUT=120
LLM_TOTAL_TIMEOUT=1200

# Use multiple API keys for better rate limits
GEMINI_API_KEYS=key1,key2,key3

# Consider using faster models
GEMINI_PRIMARY_MODEL=gemini-1.5-flash
```

**5. Base File Not Found (LLM-only mode)**
```bash
# Ensure base file exists
ls -la reports/*_analysis_base_*.json

# Generate base file first if missing
python src/main.py --ticker AAPL --non-llm-only --save-report

# Use correct path format
python src/main.py --llm-only --base-data-path stock-analysis-viewer/public/reports/AAPL_analysis_base_20240101_120000.json --save-report
```

**6. Workflow Automation Issues**
```bash
# Test daily workflow locally
python src/main.py --ticker AAPL --non-llm-only --save-report --format json

# Test weekly workflow locally
python scripts/weekly_llm_analysis.py --tickers AAPL

# Check file permissions and paths
ls -la stock-analysis-viewer/public/reports/
```

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python src/main.py --ticker AAPL --detailed
```

### Performance Monitoring

Monitor token usage and API costs:
```bash
# Check token usage after analysis
python -c "from src.llm.token_tracker import token_tracker; print(token_tracker.get_summary())"
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black isort mypy

# Run tests
pytest

# Code formatting
black src/
isort src/

# Type checking
mypy src/
```

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **JavaScript/TypeScript**: Follow ESLint configuration
- **Documentation**: Update README and docstrings
- **Testing**: Add tests for new features

## 📊 Project Structure

```
llm-stock-analyzer/
├── src/                          # Python source code
│   ├── analysis/                 # Analysis modules
│   │   ├── warren_buffett.py     # Value investing analysis
│   │   ├── peter_lynch.py        # Growth investing analysis
│   │   └── technical_indicators.py # Technical analysis
│   ├── data/                     # Data fetching modules
│   │   └── yahoo_finance.py      # Yahoo Finance API
│   ├── llm/                      # LLM integration
│   │   ├── client_factory.py     # LLM client factory
│   │   ├── openai_client.py      # OpenAI integration
│   │   └── gemini_client.py      # Google Gemini integration
│   ├── utils/                    # Utility modules
│   │   ├── config.py             # Configuration management
│   │   └── logger.py             # Logging setup
│   └── main.py                   # Main application entry point
├── stock-analysis-viewer/        # React frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── types/               # TypeScript type definitions
│   │   └── app/                 # Next.js app structure
│   └── public/                  # Static assets and reports
├── requirements.txt              # Python dependencies
├── env.example                   # Environment variables template
└── README.md                    # This file
```

## 📈 Example Analysis Output

### Warren Buffett Analysis
- **Investment Signal**: BUY (Confidence: 78.5%)
- **Quality Score**: 77.3%
- **Margin of Safety**: 12.5%
- **Key Strengths**: Strong ROE (24.3%), Conservative debt, Excellent margins

### Peter Lynch Analysis
- **Investment Signal**: BUY (Confidence: 82.1%)
- **GARP Score**: 85.2%
- **PEG Ratio**: 0.85 (Excellent)
- **Growth Category**: Fast Grower

### Technical Analysis
- **Overall Signal**: BULLISH (Confidence: 72.5%)
- **RSI**: 58.3 (Neutral with upward bias)
- **MACD**: Bullish crossover
- **Moving Averages**: Price above all major MAs

## 🔗 Related Projects

- **[yfinance](https://github.com/ranaroussi/yfinance)**: Yahoo Finance data fetching
- **[pandas-ta](https://github.com/twopirllc/pandas-ta)**: Technical analysis indicators
- **[OpenAI API](https://openai.com/api/)**: GPT models for analysis
- **[Google Gemini](https://ai.google.dev/)**: Google's LLM for insights

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Warren Buffett and Peter Lynch** for their investment methodologies
- **Yahoo Finance** for providing free financial data
- **OpenAI, Google, Anthropic, Groq** for LLM APIs
- **Technical Analysis Community** for indicator implementations
- **Open Source Contributors** for various libraries used

## 📞 Support

For questions, issues, or feature requests:

1. **Check the [Issues](../../issues)** page for existing discussions
2. **Review the [Documentation](docs/)** for detailed guides
3. **Join our [Discussions](../../discussions)** for community support
4. **Contact**: Create an issue with the `question` label

## ⚠️ Disclaimer

**Important**: This tool is for educational and research purposes only. It does not constitute financial advice. The analysis provided should not be the sole basis for investment decisions. Always:

- Conduct your own research
- Consult with qualified financial professionals
- Consider your risk tolerance and investment objectives
- Understand that past performance does not guarantee future results
- Be aware that all investments carry risk of loss

The developers and contributors are not responsible for any financial losses incurred from using this tool.
