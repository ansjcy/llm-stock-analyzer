# LLM Stock Analysis Tool

An advanced AI-powered stock analysis platform that combines comprehensive technical analysis, fundamental analysis, sentiment analysis, and real-time news summarization using Large Language Models (LLMs).

## Recent Updates 🆕

### Gemini Model Configuration & Safety Filtering Fix
- **✅ Stable configuration with Gemini 2.0 Flash** as primary model and **Gemini 1.5 Flash** as fallback
- **🛡️ Fixed content filtering issues** with Chinese prompts by configuring proper safety settings  
- **🔧 Resolved civic integrity category error** by using only the 4 officially supported safety categories
- **📈 Enhanced model reliability** with optimized fallback system (Gemini 2.0 → Gemini 1.5)
- **🚀 Improved safety configuration** with all supported safety categories set to `BLOCK_NONE` for financial analysis
- **⚡ Reduced timeouts and retry attempts** for faster response handling

## Features

### 🔍 Multi-Dimensional Analysis
- **Technical Analysis**: Moving averages, RSI, MACD, Bollinger Bands, ADX, and more
- **Fundamental Analysis**: P/E ratios, debt-to-equity, ROE, growth metrics, financial health
- **Sentiment Analysis**: Market sentiment and news sentiment analysis
- **News Analysis**: Real-time news aggregation and AI-powered summarization
- **Investment Recommendations**: AI-generated investment suggestions with confidence levels

### 📊 Data Sources
- **Yahoo Finance**: Free historical and real-time stock data
- **Sina Finance**: Asian market data and real-time quotes
- **Financial News APIs**: Aggregated news from multiple sources
- **Technical Indicators**: Custom-calculated technical analysis indicators

### 🤖 LLM Integration
- **Multiple LLM Support**: OpenAI GPT, Google Gemini, Claude, Groq, and Ollama (local)
- **Intelligent Analysis**: Context-aware stock analysis and recommendations
- **News Summarization**: AI-powered news summarization and impact analysis
- **Investment Advice**: Confidence-rated investment suggestions
- **Provider Flexibility**: Switch between LLM providers via command line or configuration

### 🎯 Key Capabilities
- Single ticker analysis with comprehensive reports
- Real-time data fetching and analysis
- Historical trend analysis
- Risk assessment and confidence scoring
- Market news impact analysis
- Investment recommendation engine

## Quick Start

### Prerequisites
- Python 3.11+
- API keys for LLM providers (OpenAI, Gemini, etc.)

### Getting API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the generated API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm-stock-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the analysis:
```bash
python src/main.py --ticker AAPL
```

### Example Usage

```bash
# Analyze Apple stock with default LLM provider
python src/main.py --ticker AAPL

# Analyze using Google Gemini
python src/main.py --ticker AAPL --llm-provider gemini

# Analyze using OpenAI
python src/main.py --ticker AAPL --llm-provider openai

# Analyze with specific date range
python src/main.py --ticker MSFT --start-date 2024-01-01 --end-date 2024-12-31

# Generate detailed report and save
python src/main.py --ticker TSLA --detailed --save-report --llm-provider gemini

# Full analysis with all features
python src/main.py --ticker NVDA --detailed --save-report --format json --llm-provider openai
```

## Project Structure

```
llm-stock-analysis/
├── src/
│   ├── agents/               # Analysis agents
│   │   ├── technical.py     # Technical analysis agent
│   │   ├── fundamental.py   # Fundamental analysis agent
│   │   ├── sentiment.py     # Sentiment analysis agent
│   │   └── news.py         # News analysis agent
│   ├── data/                # Data fetching and processing
│   │   ├── yahoo_finance.py # Yahoo Finance API
│   │   ├── sina_finance.py  # Sina Finance API
│   │   └── news_apis.py     # News data sources
│   ├── llm/                 # LLM integration
│   │   ├── openai_client.py # OpenAI integration
│   │   ├── gemini_client.py # Google Gemini integration
│   │   ├── claude_client.py # Claude integration
│   │   ├── groq_client.py   # Groq integration
│   │   └── ollama_client.py # Local Ollama integration
│   ├── analysis/            # Analysis engines
│   │   ├── technical_indicators.py
│   │   ├── fundamental_metrics.py
│   │   └── sentiment_analyzer.py
│   ├── utils/               # Utilities
│   │   ├── config.py       # Configuration management
│   │   ├── logger.py       # Logging utilities
│   │   └── helpers.py      # Helper functions
│   └── main.py             # Main application entry point
├── reports/                 # Generated analysis reports
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Configuration

Create a `.env` file with the following variables:

```env
# LLM API Keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
CLAUDE_API_KEY=your_claude_api_key
GROQ_API_KEY=your_groq_api_key

# News API Keys (optional)
NEWS_API_KEY=your_news_api_key

# Configuration
DEFAULT_LLM_PROVIDER=openai
LOG_LEVEL=INFO
CACHE_DURATION=3600
```

## Analysis Types

### Technical Analysis
- **Trend Indicators**: EMA, SMA, MACD, ADX
- **Momentum**: RSI, Stochastic, Williams %R
- **Volatility**: Bollinger Bands, ATR
- **Volume**: OBV, Volume SMA
- **Support/Resistance**: Pivot points, key levels

### Fundamental Analysis
- **Profitability**: ROE, ROA, Net Margin, Operating Margin
- **Growth**: Revenue Growth, Earnings Growth, EPS Growth
- **Financial Health**: Current Ratio, Debt-to-Equity, Quick Ratio
- **Valuation**: P/E, P/B, P/S, PEG Ratio
- **Efficiency**: Asset Turnover, Inventory Turnover

### Sentiment Analysis
- **News Sentiment**: Analysis of recent news articles
- **Market Sentiment**: Overall market mood indicators
- **Social Media**: Trending topics and mentions
- **Analyst Opinions**: Professional analyst recommendations

## API Endpoints

The tool can be extended with a REST API:

```
GET /api/analyze/{ticker}           # Get comprehensive analysis
GET /api/technical/{ticker}         # Get technical analysis only
GET /api/fundamental/{ticker}       # Get fundamental analysis only
GET /api/news/{ticker}             # Get news analysis
GET /api/recommendation/{ticker}    # Get investment recommendation
```

## Troubleshooting

### Common Issues

#### "No LLM providers configured" message
- Make sure you have set either `OPENAI_API_KEY` or `GEMINI_API_KEY` in your `.env` file
- Verify that your API keys are valid and active
- Check that you haven't exceeded your API quota

#### "ModuleNotFoundError: No module named 'talib'"
- This is expected - we use `pandas-ta` instead of `talib` for easier installation
- If you see this error, make sure you've installed the requirements: `pip install -r requirements.txt`

#### Technical analysis errors
- Ensure you have sufficient historical data (at least 200 days for reliable indicators)
- Some indicators may return NaN for stocks with limited trading history

#### API Rate Limits
- If you encounter rate limit errors, the tool will automatically handle retries
- Consider upgrading your API plan if you frequently hit limits

### Running Without LLM (Basic Mode)
If you don't have LLM API keys configured, the tool will still provide:
- Technical analysis indicators
- Basic stock information
- News headlines (without AI analysis)

```bash
# This will work without API keys
python src/main.py --ticker AAPL
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is for educational purposes only. Not financial advice.

## Disclaimer

This tool is for educational and research purposes only. The analysis and recommendations provided should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions. 