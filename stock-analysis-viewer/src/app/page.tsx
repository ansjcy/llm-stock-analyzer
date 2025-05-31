'use client';

import React, { useState, useEffect } from 'react';
import { StockAnalysisResult } from '@/types/analysis';
import StockOverview from '@/components/StockOverview';
import TechnicalAnalysis from '@/components/TechnicalAnalysis';
import CorrelationChart from '@/components/CorrelationChart';
import NewsSection from '@/components/NewsSection';
import AIInsights from '@/components/AIInsights';
import ExecutiveSummary from '@/components/ExecutiveSummary';
import InvestmentRecommendation from '@/components/InvestmentRecommendation';
import { Upload, FileText, TrendingUp, AlertCircle, ChevronDown, Moon, Sun } from 'lucide-react';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';

interface ReportFile {
  filename: string;
  ticker: string;
  date: string;
  time: string;
  fullPath: string;
}

function HomeContent() {
  const { theme, toggleTheme, mounted } = useTheme();
  const [analysisData, setAnalysisData] = useState<StockAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableReports, setAvailableReports] = useState<ReportFile[]>([]);
  const [selectedReport, setSelectedReport] = useState<string>('');
  const [loadingReports, setLoadingReports] = useState(true);

  // Helper function to get correct API URL with basePath
  const getApiUrl = (path: string) => {
    const basePath = process.env.NODE_ENV === 'production' ? '/stock-analyzer' : '';
    return `${basePath}${path}`;
  };

  const loadAvailableReports = async () => {
    try {
      setLoadingReports(true);
      const response = await fetch(getApiUrl('/api/reports'));
      const data = await response.json();
      
      if (data.reports) {
        setAvailableReports(data.reports);
      }
    } catch (err) {
      console.error('Error loading available reports:', err);
      setError('加载可用报告失败');
    } finally {
      setLoadingReports(false);
    }
  };

  const loadReport = async (reportPath: string) => {
    if (!reportPath) return;
    
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(reportPath);
      if (!response.ok) {
        throw new Error('Failed to load report');
      }
      
      const data: StockAnalysisResult = await response.json();
      
      // Validate the data structure
      if (!data.ticker || !data.stock_info) {
        throw new Error('Invalid analysis file format');
      }
      
      setAnalysisData(data);
    } catch (err) {
      console.error('Error loading report:', err);
      setError('加载分析报告时出错。请尝试其他报告。');
    } finally {
      setLoading(false);
    }
  };

  const handleReportSelection = (reportPath: string) => {
    setSelectedReport(reportPath);
    loadReport(reportPath);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const text = await file.text();
      const data: StockAnalysisResult = JSON.parse(text);
      
      // Validate the data structure
      if (!data.ticker || !data.stock_info) {
        throw new Error('Invalid analysis file format');
      }
      
      setAnalysisData(data);
      setSelectedReport(''); // Clear selected report when uploading custom file
    } catch (err) {
      console.error('Error parsing file:', err);
      setError('解析分析文件时出错。请确保这是股票分析工具生成的有效JSON文件。');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoData = () => {
    // Sample data for demonstration
    const demoData: StockAnalysisResult = {
      ticker: "AAPL",
      analysis_date: "2025-01-09T10:00:00Z",
      stock_info: {
        name: "Apple Inc.",
        current_price: 185.50,
        previous_close: 184.75,
        day_low: 183.20,
        day_high: 186.80,
        week_52_low: 169.21,
        week_52_high: 260.10,
        market_cap: 2850000000000,
        volume: 65432100,
        pe_ratio: 28.5,
        beta: 1.25,
        sector: "Technology",
        industry: "Consumer Electronics"
      },
      technical_analysis: {
        overall_signal: "bullish",
        confidence: 72.5,
        strategic_combinations: {
          rsi_macd_strategy: {
            signal: "bullish",
            score: 8.2
          },
          bollinger_rsi_macd_strategy: {
            signal: "neutral",
            score: 5.5
          },
          ma_rsi_volume_strategy: {
            signal: "bullish",
            score: 7.8
          }
        },
        momentum: {
          rsi: 58.3,
          rsi_signal: "neutral",
          stoch_k: 62.1,
          stoch_signal: "bullish"
        },
        trend: {
          macd_signal: "bullish",
          macd_histogram: 0.0245
        },
        moving_averages: {
          sma_trend: "bullish",
          price_vs_sma_20: 2.3,
          price_vs_sma_50: 5.7,
          price_vs_sma_200: 12.1
        }
      },
      correlation_analysis: {
        correlations: {
          "^GSPC": 0.85,
          "^DJI": 0.78,
          "^IXIC": 0.92
        },
        beta: 1.25,
        diversification_score: 65
      },
      fundamental_analysis: {},
      news_analysis: {
        articles_found: 5,
        recent_articles: [
          {
            title: "Apple Reports Strong Q4 Earnings",
            published: "2025-01-08T15:30:00Z",
            summary: "Apple Inc. reported better-than-expected quarterly earnings with strong iPhone sales and services revenue growth."
          },
          {
            title: "Apple's AI Strategy Gains Momentum",
            published: "2025-01-07T10:15:00Z",
            summary: "The company's artificial intelligence initiatives are showing promising results in early user adoption."
          }
        ]
      },
      llm_insights: {
        technical: "## Technical Analysis Summary\n\nThe technical indicators show a **bullish** outlook with high confidence (72.5%). Key findings:\n\n- **RSI at 58.3**: Neutral territory with room for upward movement\n- **MACD showing bullish crossover** with positive histogram\n- **Price above all major moving averages** indicating strong trend\n\n### Strategic Signals\n- RSI+MACD strategy is bullish (score: 8.2/10)\n- Strong volume confirmation supports the upward trend",
        fundamental: "## Fundamental Analysis\n\n**Valuation Assessment**: Moderately valued with P/E of 28.5x\n\n**Key Strengths**:\n- Strong market position in premium consumer electronics\n- Robust services revenue growth\n- Excellent brand loyalty and ecosystem\n\n**Areas to Monitor**:\n- High valuation multiples\n- Dependence on iPhone sales\n- Competitive pressure in emerging markets",
        news: "## News Sentiment Analysis\n\n**Overall Sentiment**: Positive (7.5/10)\n\n**Key Themes**:\n- Strong quarterly earnings performance\n- AI strategy showing early success\n- Services revenue diversification\n\n**Market Impact**: The recent earnings beat has reinforced investor confidence and supports the current bullish technical setup."
      },
      recommendation: {
        full_analysis: "## Investment Recommendation: BUY\n\n**Target Price**: $195-200 (6-month horizon)\n\n**Investment Thesis**:\n1. Strong technical momentum with bullish indicators\n2. Solid fundamental performance in latest quarter\n3. Positive news sentiment supporting upward trend\n\n**Risk Factors**:\n- High valuation requires continued execution\n- Market volatility could impact tech stocks\n- Competitive pressure in key markets\n\n**Position Sizing**: 3-5% of portfolio for growth-oriented investors"
      },
      summary: {
        executive_summary: "## Executive Summary\n\n**Apple Inc. (AAPL)** presents a compelling investment opportunity with strong technical momentum (72.5% confidence bullish signal), solid fundamentals, and positive market sentiment. Recent earnings beat and AI strategy progress support a price target of $195-200 over the next 6 months.\n\n**Key Investment Points**:\n- Technical indicators strongly bullish\n- Fundamental strength in core business\n- Positive news flow and market sentiment\n\n**Recommendation**: BUY with 3-5% portfolio allocation for suitable investors."
      },
      charts: {}
    };
    
    setAnalysisData(demoData);
    setSelectedReport(''); // Clear selected report when using demo data
  };

  // Load available reports on component mount
  useEffect(() => {
    loadAvailableReports();
  }, []);

  // Auto-select first report when reports are loaded
  useEffect(() => {
    if (availableReports.length > 0 && !selectedReport) {
      setSelectedReport(availableReports[0].fullPath);
      loadReport(availableReports[0].fullPath);
    }
  }, [availableReports, selectedReport]);

  // Don't render until theme is mounted to prevent hydration mismatch
  if (!mounted) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-600">加载中...</div>
      </div>
    );
  }

  if (loading || loadingReports) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">
            {loadingReports ? '正在加载可用报告...' : '正在加载分析...'}
          </p>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Theme Toggle */}
          <div className="fixed top-4 right-4 z-50">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <Moon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
              ) : (
                <Sun className="h-5 w-5 text-gray-600 dark:text-gray-300" />
              )}
            </button>
          </div>

          <div className="text-center mb-12">
            <TrendingUp className="mx-auto h-16 w-16 text-blue-600 mb-4" />
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              股票分析查看器
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              选择股票分析报告以查看全面的见解
            </p>
          </div>

          {/* Stock Selection Dropdown */}
          {availableReports.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 border border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
                <TrendingUp className="mr-2 text-blue-600" />
                选择股票报告
              </h2>
              
              <div className="relative">
                <select
                  value={selectedReport}
                  onChange={(e) => handleReportSelection(e.target.value)}
                  className="w-full p-4 text-lg border-2 border-gray-300 dark:border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none appearance-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white pr-10"
                >
                  <option value="">选择股票分析报告...</option>
                  {availableReports.map((report) => (
                    <option key={report.fullPath} value={report.fullPath}>
                      {report.ticker} - {new Date(
                        `${report.date.slice(0, 4)}-${report.date.slice(4, 6)}-${report.date.slice(6, 8)}`
                      ).toLocaleDateString('zh-CN')} ({report.time.slice(0, 2)}:${report.time.slice(2, 4)})
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" size={20} />
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
                可用报告: 已分析 {availableReports.length} 只股票
              </p>
            </div>
          )}

          {/* Manual Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 border border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <Upload className="mr-2 text-blue-600" />
              上传自定义分析报告
            </h2>
            
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-blue-400 dark:hover:border-blue-500 transition-colors">
              <FileText className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
              <p className="text-lg text-gray-600 dark:text-gray-300 mb-4">
                或上传您自己的JSON分析文件
              </p>
              <input
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg cursor-pointer hover:bg-blue-700 transition-colors inline-block"
              >
                选择文件
              </label>
            </div>

            {error && (
              <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center">
                <AlertCircle className="text-red-600 dark:text-red-400 mr-2" size={20} />
                <span className="text-red-800 dark:text-red-300">{error}</span>
              </div>
            )}
          </div>

          {/* Demo Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              如何生成分析报告
            </h2>
            <div className="space-y-4 text-gray-600 dark:text-gray-300">
              <p>
                要生成分析报告，请使用LLM股票分析工具和以下命令：
              </p>
              <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 font-mono text-sm text-gray-800 dark:text-gray-200">
                python src/main.py --ticker AAPL --detailed --save-report --format json
              </div>
              <p>
                这将在reports目录中创建一个JSON文件，该文件将自动显示在上面的下拉列表中。
              </p>
              <div className="flex space-x-4">
                <button
                  onClick={handleDemoData}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  查看演示数据（看涨）
                </button>
                <button
                  onClick={() => {
                    // Load the sample bearish data
                    fetch('/sample-analysis.json')
                      .then(response => response.json())
                      .then(data => {
                        setAnalysisData(data);
                        setSelectedReport('');
                      })
                      .catch(() => setError('无法加载示例数据'));
                  }}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  查看示例数据（看跌）
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Theme Toggle */}
        <div className="fixed top-4 right-4 z-50">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <Sun className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            )}
          </button>
        </div>

        {/* Action Bar */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 mb-6 border border-gray-200 dark:border-gray-700">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                股票分析报告 - {analysisData.ticker}
              </h1>
              {selectedReport && (
                <span className="text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full">
                  自动加载
                </span>
              )}
            </div>
            
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              {/* Stock Selector */}
              {availableReports.length > 0 && (
                <div className="relative min-w-[200px]">
                  <select
                    value={selectedReport}
                    onChange={(e) => handleReportSelection(e.target.value)}
                    className="w-full p-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none appearance-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white pr-8"
                  >
                    <option value="">切换到其他报告...</option>
                    {availableReports.map((report) => (
                      <option key={report.fullPath} value={report.fullPath}>
                        {report.ticker} - {new Date(
                          `${report.date.slice(0, 4)}-${report.date.slice(4, 6)}-${report.date.slice(6, 8)}`
                        ).toLocaleDateString('zh-CN')}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none" size={16} />
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="mb-6">
          <StockOverview 
            ticker={analysisData.ticker}
            stockInfo={analysisData.stock_info}
            analysisDate={analysisData.analysis_date}
          />
        </div>
        
        <div className="mb-6">
          <ExecutiveSummary 
            summary={analysisData.summary}
          />
        </div>
        
        <div className="mb-6">
          <InvestmentRecommendation 
            recommendation={analysisData.recommendation}
          />
        </div>
        
        <div className="mb-6">
          <TechnicalAnalysis 
            technicalAnalysis={analysisData.technical_analysis}
            charts={analysisData.charts}
          />
        </div>
        
        <div className="mb-6">
          <CorrelationChart 
            correlationAnalysis={analysisData.correlation_analysis}
          />
        </div>
        
        <div className="mb-6">
          <NewsSection 
            newsAnalysis={analysisData.news_analysis}
          />
        </div>
        
        <AIInsights 
          llmInsights={analysisData.llm_insights}
        />
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <ThemeProvider>
      <HomeContent />
    </ThemeProvider>
  );
}
