# 📈 Stock Analyzer - Automated Analysis Pipeline

An automated stock analysis system that generates comprehensive reports and deploys them to GitHub Pages.

## 🚀 Features

- **Automated Analysis**: Runs daily at 1:00 PM (Monday-Friday) and on every push to main
- **Comprehensive Reports**: Technical analysis, fundamentals, and LLM-powered insights
- **Chinese Language Support**: Bilingual analysis with `--chinese` flag
- **Interactive Charts**: Visual representations of stock data and trends
- **GitHub Pages Deployment**: Automatic publication of reports and charts
- **Multiple Output Formats**: JSON and HTML report generation

## 🔄 Automated Workflow

### Schedule
- **Daily**: Monday to Friday at 1:00 PM UTC (13:00)
- **On Push**: Every push to the `main` branch
- **Manual**: Can be triggered manually via GitHub Actions

### Process
1. **Environment Setup**: Python 3.10, dependencies installation
2. **Analysis Execution**: `python src/main.py --ticker AMZN --chinese --charts --save-report --format json`
3. **Data Persistence**: Commits generated reports and charts back to repository
4. **GitHub Pages Deployment**: Publishes results to `https://ansjcy.github.io/stock-analyzer/`

## 📊 Generated Content

### Reports Directory
- **JSON Reports**: Machine-readable analysis data
- **HTML Reports**: Human-readable formatted reports
- **Fundamental Analysis**: P/E ratios, financial metrics, valuation
- **Technical Analysis**: Moving averages, RSI, MACD, Bollinger Bands
- **LLM Insights**: AI-powered market analysis and recommendations

### Charts Directory
- **Price Charts**: Historical price movements with technical indicators
- **Volume Analysis**: Trading volume patterns
- **Performance Metrics**: Comparative analysis charts
- **Technical Indicators**: Visual representation of analysis signals

## 🛠️ Local Development

### Prerequisites
```bash
# Python 3.10+
# pip package manager
```

### Setup
```bash
# Clone the repository
git clone https://github.com/ansjcy/stock-analyzer.git
cd stock-analyzer

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp env.example .env
# Edit .env with your API keys
```

### Running Analysis
```bash
# Basic analysis
python src/main.py --ticker AAPL

# Full analysis with charts and Chinese support
python src/main.py --ticker AMZN --chinese --charts --save-report --format json

# Available options:
# --ticker: Stock symbol (required)
# --chinese: Enable Chinese language support
# --charts: Generate visual charts
# --save-report: Save analysis to reports directory
# --format: Output format (json, html)
```

## 📁 Project Structure

```
stock-analyzer/
├── .github/workflows/           # GitHub Actions workflows
│   └── update-data-and-deploy.yml
├── src/                         # Source code
│   ├── main.py                 # Main application entry point
│   ├── data/                   # Data fetching modules
│   ├── analysis/               # Analysis algorithms
│   ├── llm/                    # LLM integration
│   └── utils/                  # Utility functions
├── reports/                    # Generated analysis reports
├── charts/                     # Generated chart images
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `env.example`:

```bash
# LLM API Configuration (Optional - for enhanced analysis)
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://api.your-provider.com
LLM_MODEL_NAME=gpt-4

# Gemini API Configuration (Alternative)
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL_NAME=gemini-pro
```

### GitHub Secrets
For the automated workflow to function properly, configure these repository secrets:

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `LLM_API_KEY`: (Optional) For enhanced LLM analysis
- `GEMINI_API_KEY`: (Optional) Alternative LLM provider

## 🌐 GitHub Pages

The automated workflow publishes results to GitHub Pages at:
**https://ansjcy.github.io/stock-analyzer/**

### Content Structure
- **Homepage**: Overview of latest analysis
- **Reports**: Downloadable JSON and HTML reports
- **Charts**: Interactive charts and visualizations
- **Archive**: Historical analysis data

## 📈 Analysis Features

### Technical Indicators
- Moving Averages (SMA, EMA)
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume Analysis
- Support/Resistance Levels

### Fundamental Analysis
- P/E Ratio Analysis (Current, Historical, Industry Comparison)
- Financial Ratios
- Market Cap Analysis
- Earnings Growth
- Revenue Analysis
- Debt-to-Equity Ratios

### LLM-Powered Insights
- Market Sentiment Analysis
- News Impact Assessment
- Investment Recommendations
- Risk Analysis
- Comparative Analysis

## 🔄 Workflow Status

Check the status of automated runs:
- Go to the **Actions** tab in the GitHub repository
- View **Update Stock Analysis and Deploy to GitHub Pages** workflow
- Monitor success/failure of scheduled runs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Workflow Fails to Run**
- Check GitHub Actions permissions in repository settings
- Verify Python dependencies in requirements.txt
- Ensure proper secret configuration

**Missing Charts or Reports**
- Check if directories exist and are writable
- Verify API rate limits for data providers
- Review logs in the Actions tab

**GitHub Pages Not Updating**
- Confirm GitHub Pages is enabled in repository settings
- Check if Pages source is set to "GitHub Actions"
- Verify deployment artifact upload

### Support
For issues and questions:
- Create an issue in the GitHub repository
- Check existing issues for solutions
- Review the logs in GitHub Actions for error details

---

🔄 **Last Updated**: Auto-generated by GitHub Actions
📊 **Next Analysis**: Scheduled for 1:00 PM UTC (Monday-Friday) 