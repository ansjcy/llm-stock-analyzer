# Stock Analysis Viewer

A modern React-based web interface for visualizing and exploring comprehensive stock analysis results from the LLM Stock Analyzer tool.

## 🚀 Features

- **📊 Interactive Charts**: Technical analysis with multiple timeframes and indicators
- **📱 Responsive Design**: Seamless experience on desktop and mobile devices
- **🌙 Dark/Light Theme**: User preference support with system detection
- **🌍 Multi-language Support**: English and Chinese interfaces
- **📁 Report Management**: Browse and load historical analysis reports
- **🔍 Advanced Filtering**: Search and filter analysis reports
- **📈 Real-time Updates**: Live data integration capabilities
- **🎨 Modern UI**: Clean, intuitive interface built with Tailwind CSS

## 🛠️ Tech Stack

- **Framework**: [Next.js 15](https://nextjs.org/) with React 19
- **Language**: TypeScript for type safety
- **Styling**: [Tailwind CSS 4.0](https://tailwindcss.com/) for modern styling
- **Charts**: [Recharts](https://recharts.org/) for interactive data visualization
- **Icons**: [Lucide React](https://lucide.dev/) for consistent iconography
- **Markdown**: [React Markdown](https://github.com/remarkjs/react-markdown) for rich text rendering

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Development](#development)
- [Components](#components)
- [Features](#features-overview)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+**
- **npm or yarn**
- **LLM Stock Analyzer** (parent project) for generating analysis data

### Installation

1. **Navigate to the frontend directory**
   ```bash
   cd stock-analysis-viewer
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 🔧 Development

### Available Scripts

```bash
# Start development server with Turbopack
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run ESLint
npm run lint

# Sync reports from parent directory
npm run sync-reports
```

### Development Workflow

1. **Generate Analysis Data**
   ```bash
   # From parent directory
   python src/main.py --ticker AAPL --detailed --save-report
   ```

2. **Sync Reports** (if needed)
   ```bash
   npm run sync-reports
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

## 🧩 Components

### Core Components

#### `StockOverview`
Displays basic stock information including price, market cap, and key metrics.

#### `TechnicalAnalysis`
Interactive technical analysis with charts and indicators:
- Moving averages (SMA 20, 50, 200)
- RSI and MACD indicators
- Bollinger Bands
- Volume analysis

#### `TechnicalCharts`
Advanced charting component using Recharts:
- Candlestick price charts
- Technical indicator overlays
- Interactive tooltips and zoom

#### `WarrenBuffettAnalysis`
Warren Buffett value investing analysis display:
- Investment signal and confidence
- Fundamental analysis breakdown
- Economic moat evaluation
- Intrinsic value calculation

#### `PeterLynchAnalysis`
Peter Lynch growth investing analysis:
- GARP (Growth at Reasonable Price) metrics
- Growth consistency evaluation
- Business quality assessment

#### `AIInsights`
LLM-generated insights display:
- Technical analysis insights
- Fundamental analysis interpretation
- News sentiment analysis
- Investment recommendations

#### `NewsSection`
Recent news and sentiment analysis:
- Article summaries
- Publication dates
- Sentiment indicators

#### `CorrelationChart`
Market correlation visualization:
- Correlation with major indices
- Beta calculation
- Diversification recommendations

### Utility Components

#### `ThemeToggle`
Dark/light theme switcher with system preference detection.

#### `HelpTooltip`
Contextual help tooltips for complex financial metrics.

#### `InsightsSummaryTable`
Comprehensive summary table of all analysis components.

## 🎨 Features Overview

### Interactive Charts

The application provides rich, interactive charts powered by Recharts:

- **Price Charts**: Candlestick and line charts with multiple timeframes
- **Technical Indicators**: RSI, MACD, Bollinger Bands overlays
- **Volume Analysis**: Volume bars with moving averages
- **Correlation Charts**: Market correlation visualization

### Report Management

- **Automatic Discovery**: Scans for analysis reports in the public/reports directory
- **Smart Grouping**: Groups base and LLM analysis files by ticker and timestamp
- **Status Indicators**: Shows completion status (base only, LLM only, or complete)
- **Easy Navigation**: Dropdown selector for quick report switching

### Responsive Design

- **Mobile-First**: Optimized for mobile devices
- **Tablet Support**: Adapted layouts for tablet screens
- **Desktop Enhancement**: Full-featured desktop experience
- **Touch-Friendly**: Large touch targets and gestures

### Theme System

- **System Detection**: Automatically detects user's system preference
- **Manual Override**: Toggle between light and dark themes
- **Persistent Storage**: Remembers user preference across sessions
- **Smooth Transitions**: Animated theme transitions

### Multi-language Support

- **English/Chinese**: Full interface translation
- **Context-Aware**: Financial terms properly localized
- **Consistent Formatting**: Number and date formatting per locale

## ⚙️ Configuration

### Environment Variables

Create a `.env.local` file for local configuration:

```env
# Base path for production deployment (optional)
NEXT_PUBLIC_BASE_PATH=/stock-analyzer

# API endpoints (if using external APIs)
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

### Next.js Configuration

The `next.config.ts` file includes:

```typescript
const nextConfig = {
  // Enable static export for GitHub Pages
  output: 'export',
  
  // Base path for deployment
  basePath: process.env.NODE_ENV === 'production' ? '/stock-analyzer' : '',
  
  // Image optimization
  images: {
    unoptimized: true
  }
}
```

### Tailwind Configuration

Custom Tailwind configuration in `tailwind.config.ts`:

```typescript
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Custom color palette
      },
      animation: {
        // Custom animations
      }
    }
  }
}
```

## 🚀 Deployment

### Static Export (Recommended)

For GitHub Pages or static hosting:

```bash
npm run build
```

This generates a static export in the `out/` directory.

### Vercel Deployment

1. **Connect Repository**: Link your GitHub repository to Vercel
2. **Configure Build**: Vercel auto-detects Next.js configuration
3. **Deploy**: Automatic deployment on push to main branch

### Docker Deployment

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Manual Server Deployment

```bash
# Build the application
npm run build

# Start production server
npm start
```

## 📊 Data Flow

### Report Loading Process

1. **Scan Reports**: Application scans `public/reports/` directory
2. **Group Files**: Groups base and LLM analysis files by ticker/timestamp
3. **Load Data**: Fetches and merges analysis data
4. **Render Components**: Displays data in appropriate components

### File Structure

```
public/reports/
├── AAPL_base_20240109_100000.json      # Base analysis
├── AAPL_llm_20240109_100000.json       # LLM insights
├── GOOGL_complete_20240109_110000.json # Legacy complete file
└── ...
```

### Data Types

The application uses comprehensive TypeScript types defined in `src/types/analysis.ts`:

- `StockAnalysisResult`: Main analysis result interface
- `TechnicalAnalysis`: Technical indicators and signals
- `WarrenBuffettAnalysis`: Value investing analysis
- `PeterLynchAnalysis`: Growth investing analysis
- `LLMInsights`: AI-generated insights

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/llm-stock-analyzer.git
   cd llm-stock-analyzer/stock-analysis-viewer
   ```

3. **Install dependencies**
   ```bash
   npm install
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

### Code Standards

- **TypeScript**: Use strict type checking
- **ESLint**: Follow the configured ESLint rules
- **Prettier**: Code formatting (integrated with ESLint)
- **Component Structure**: Use functional components with hooks
- **CSS**: Use Tailwind CSS classes, avoid custom CSS when possible

### Testing

```bash
# Run type checking
npm run type-check

# Run linting
npm run lint

# Run tests (when available)
npm test
```

## 📄 License

This project is part of the LLM Stock Analyzer and is licensed under the MIT License.

## 🙏 Acknowledgments

- **Next.js Team** for the excellent React framework
- **Tailwind CSS** for the utility-first CSS framework
- **Recharts** for beautiful and customizable charts
- **Lucide** for the comprehensive icon library
- **React Community** for the ecosystem of tools and libraries

## 📞 Support

For frontend-specific issues:

1. Check the main project [Issues](../../../issues)
2. Review the [Next.js Documentation](https://nextjs.org/docs)
3. Check [Tailwind CSS Documentation](https://tailwindcss.com/docs)
4. Review [Recharts Documentation](https://recharts.org/en-US/)

## ⚠️ Disclaimer

**Important**: This tool is for educational and research purposes only. It does not constitute financial advice. The analysis provided should not be the sole basis for investment decisions. Always:

- Conduct your own research
- Consult with qualified financial professionals
- Consider your risk tolerance and investment objectives
- Understand that past performance does not guarantee future results
- Be aware that all investments carry risk of loss

The developers and contributors are not responsible for any financial losses incurred from using this tool.
---

**Note**: This frontend application is designed to work with analysis data generated by the LLM Stock Analyzer Python tool. Make sure to generate analysis reports first before using the web interface.
