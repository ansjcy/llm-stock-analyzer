'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { StockAnalysisResult } from '@/types/analysis';
import StockOverview from '@/components/StockOverview';
import TechnicalAnalysis from '@/components/TechnicalAnalysis';
import CorrelationChart from '@/components/CorrelationChart';
import NewsSection from '@/components/NewsSection';
import InsightsSummaryTable from '@/components/InsightsSummaryTable';
import { Upload, FileText, TrendingUp, AlertCircle, ChevronDown } from 'lucide-react';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';

interface ReportFileInfo {
  filename: string;
  fullPath: string;
  date: string;
  time: string;
}

interface ReportGroup {
  ticker: string;
  date: string;
  time: string;
  baseFile?: ReportFileInfo;
  llmFile?: ReportFileInfo;
  legacyFile?: ReportFileInfo;
  hasComplete: boolean;
}

function HomeContent() {
  const { mounted } = useTheme();
  const [analysisData, setAnalysisData] = useState<StockAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableReports, setAvailableReports] = useState<ReportGroup[]>([]);
  const [selectedReport, setSelectedReport] = useState<string>('');
  const [loadingReports, setLoadingReports] = useState(true);

  // Helper function to get correct API URL with basePath
  const getApiUrl = (path: string) => {
    const basePath = process.env.NODE_ENV === 'production' ? '/stock-analyzer' : '';
    return `${basePath}${path}`;
  };

  const loadAvailableReports = useCallback(async () => {
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
  }, []);

  const loadReport = async (reportGroup: any) => {
    if (!reportGroup) return;

    setLoading(true);
    setError(null);

    try {
      let data: StockAnalysisResult;

      if (reportGroup.legacyFile) {
        // Handle legacy complete files
        const response = await fetch(reportGroup.legacyFile.fullPath);
        if (!response.ok) {
          throw new Error('Failed to load legacy report');
        }
        data = await response.json();
      } else {
        // Handle new split files - merge base and LLM data
        let baseData: any = {};
        let llmData: any = {};

        // Load base data
        if (reportGroup.baseFile) {
          const baseResponse = await fetch(reportGroup.baseFile.fullPath);
          if (!baseResponse.ok) {
            throw new Error('Failed to load base report');
          }
          baseData = await baseResponse.json();
        }

        // Load LLM data if available
        if (reportGroup.llmFile) {
          const llmResponse = await fetch(reportGroup.llmFile.fullPath);
          if (!llmResponse.ok) {
            console.warn('Failed to load LLM report, continuing with base data only');
          } else {
            llmData = await llmResponse.json();
          }
        }

        // Merge the data
        data = {
          ...baseData,
          llm_insights: llmData.llm_insights || {},
          recommendation: llmData.recommendation || {},
          summary: llmData.summary || {},
          llm_analysis_date: llmData.llm_analysis_date
        };
      }

      // Validate the data structure
      if (!data.ticker || !data.stock_info) {
        throw new Error('Invalid analysis file format');
      }

      setAnalysisData(data);
      // Store the loaded report group in sessionStorage for restoration
      sessionStorage.setItem('currentSelectedReport', JSON.stringify(reportGroup));
    } catch (err) {
      console.error('Error loading report:', err);
      setError('加载分析报告时出错。请尝试其他报告。');
    } finally {
      setLoading(false);
    }
  };

  const handleReportSelection = (reportIndex: string) => {
    if (!reportIndex) return;

    const index = parseInt(reportIndex);
    const reportGroup = availableReports[index];

    if (reportGroup) {
      setSelectedReport(reportIndex);
      loadReport(reportGroup);
    }
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
      // Clear current selected report from sessionStorage since we're using custom file
      sessionStorage.removeItem('currentSelectedReport');
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
      warren_buffett_analysis: {
        ticker: "AAPL",
        analysis_date: "2025-01-09T10:00:00Z",
        overall_signal: "buy",
        confidence: 78.5,
        total_score: 17,
        max_possible_score: 22,
        score_percentage: 77.3,
        margin_of_safety: 12.5,
        fundamental_analysis: {
          score: 6,
          max_score: 8,
          score_percentage: 75.0,
          details: [
            "强劲的股本回报率24.3%（>15%）",
            "保守的债务水平（0.31）",
            "优秀的营业利润率（29.8%）",
            "强劲的流动性（流动比率：1.1）"
          ],
          metrics: {
            return_on_equity: 0.243,
            debt_to_equity: 0.31,
            operating_margin: 0.298,
            current_ratio: 1.1
          }
        },
        consistency_analysis: {
          score: 4,
          max_score: 4,
          score_percentage: 100.0,
          details: [
            "5年以上持续正收益",
            "强劲的收益增长趋势（15.2%）",
            "低收益波动性",
            "可预测的商业模式"
          ],
          revenue_growth_consistency: 0.92,
          earnings_growth_consistency: 0.88,
          fcf_growth_consistency: 0.85
        },
        moat_analysis: {
          score: 4,
          max_score: 6,
          score_percentage: 66.7,
          details: [
            "强大的品牌价值和生态系统",
            "客户高转换成本",
            "溢价定价能力"
          ],
          competitive_advantages: [
            "生态系统锁定效应",
            "高端品牌定位",
            "垂直整合供应链",
            "强大的研发能力"
          ],
          moat_strength: "宽阔"
        },
        management_analysis: {
          score: 3,
          max_score: 4,
          score_percentage: 75.0,
          details: [
            "优秀的资本配置策略",
            "通过回购和分红实现强劲股东回报",
            "谨慎投资增长计划"
          ],
          capital_allocation_score: 8.5,
          shareholder_returns_score: 9.2
        },
        intrinsic_value_analysis: {
          intrinsic_value: 195.5,
          current_price: 185.5,
          margin_of_safety: 12.5,
          valuation_method: "带终值的DCF模型",
          dcf_details: {
            free_cash_flow: 95000000000,
            growth_rate: 0.08,
            terminal_value: 2800000000000,
            discount_rate: 0.09
          },
          reasoning: [
            "强劲的自由现金流生成支持高内在价值",
            "保守的年增长假设8%",
            "9%的折现率考虑了公司风险状况",
            "当前价格提供了充足的安全边际"
          ]
        },
        investment_reasoning: [
          "苹果公司展现出卓越的基本面实力，拥有强劲的股本回报率和利润率",
          "业务在收益和收入增长方面表现出卓越的一致性",
          "公司通过其生态系统拥有宽阔的经济护城河",
          "管理层在股东价值创造方面有着良好的记录",
          "当前估值为长期投资者提供了合理的安全边际"
        ],
        buffett_principles: {
          individual_principles: {
            financial_strength: {
              score: 85.0,
              meets_criteria: true,
              description: "强劲的股本回报率29.8%，保守的债务水平，优秀的营业利润率，以及强劲的流动性状况"
            },
            predictable_earnings: {
              score: 90.0,
              meets_criteria: true,
              description: "5年以上持续正收益，强劲的增长趋势和低波动性"
            },
            competitive_advantage: {
              score: 80.0,
              meets_criteria: true,
              description: "通过生态系统锁定、高端品牌定位和高转换成本形成宽阔的经济护城河"
            },
            quality_management: {
              score: 85.0,
              meets_criteria: true,
              description: "优秀的资本配置策略，强劲的股东回报和谨慎的增长投资"
            },
            margin_of_safety: {
              score: 75.0,
              meets_criteria: true,
              description: "当前价格提供合理的安全边际，相对内在价值有12.5%的折价"
            }
          },
          total_principles_met: 5,
          total_principles: 5,
          adherence_percentage: 100.0,
          overall_assessment: "优秀的巴菲特候选股"
        }
      },
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
        news: "## News Sentiment Analysis\n\n**Overall Sentiment**: Positive (7.5/10)\n\n**Key Themes**:\n- Strong quarterly earnings performance\n- AI strategy showing early success\n- Services revenue diversification\n\n**Market Impact**: The recent earnings beat has reinforced investor confidence and supports the current bullish technical setup.",
        warren_buffett: "## 沃伦·巴菲特投资分析\n\n**投资评级**: 买入 (信心度: 78.5%)\n\n### 核心投资亮点\n\n**1. 卓越的基本面实力**\n- 股本回报率高达24.3%，远超巴菲特15%的标准\n- 营业利润率29.8%，显示出强大的定价能力\n- 保守的债务水平，财务结构稳健\n\n**2. 业务一致性与可预测性**\n- 连续多年实现正收益增长\n- 收益波动性低，商业模式可预测\n- 强劲的现金流生成能力\n\n**3. 宽阔的经济护城河**\n- 生态系统锁定效应创造高转换成本\n- 高端品牌定位带来溢价定价能力\n- 垂直整合供应链提供竞争优势\n\n**4. 优秀的管理质量**\n- 通过股票回购和分红回报股东\n- 谨慎的资本配置策略\n- 强劲的自由现金流生成\n\n### 估值分析\n\n**内在价值**: $195.5 (当前价格: $185.5)\n**安全边际**: 12.5%\n**估值方法**: 带终值的DCF模型\n\n基于保守的8%年增长假设和9%的折现率，当前价格为长期投资者提供了合理的安全边际。\n\n### 巴菲特原则符合度\n\n✅ **财务实力** (85分): 强劲的ROE、低债务、优秀利润率\n✅ **可预测收益** (90分): 持续正收益，增长趋势稳定\n✅ **竞争优势** (80分): 宽阔的经济护城河\n✅ **管理质量** (85分): 股东友好的资本配置\n✅ **安全边际** (75分): 当前价格提供合理折价\n\n**总体评估**: 优秀的巴菲特候选股 (5/5项原则符合)\n\n### 投资建议\n\n苹果公司完全符合沃伦·巴菲特的价值投资标准。公司展现出卓越的基本面实力、可预测的业务模式、宽阔的经济护城河以及优秀的管理团队。当前估值为长期价值投资者提供了有吸引力的投资机会。\n\n**建议仓位**: 适合作为核心持仓，建议配置3-5%的投资组合比重。"
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
    // Clear current selected report from sessionStorage since we're using demo data
    sessionStorage.removeItem('currentSelectedReport');
  };

  // Load available reports on component mount
  useEffect(() => {
    loadAvailableReports();
  }, [loadAvailableReports]);

  // Handle restoration from detail pages - separate useEffect to ensure reports are loaded first
  useEffect(() => {
    // Check if returning from a detail page and reports are available
    const shouldReturnToAnalysis = sessionStorage.getItem('returnToAnalysis');

    if (shouldReturnToAnalysis && availableReports.length > 0) {
      console.log('Returning from detail page, attempting to restore selection');
      // Clear the flag
      sessionStorage.removeItem('returnToAnalysis');

      // Try to restore the previous selected report
      const previousSelectedReport = sessionStorage.getItem('previousSelectedReport');
      console.log('Previous selected report:', previousSelectedReport);

      if (previousSelectedReport) {
        try {
          const reportGroup = JSON.parse(previousSelectedReport);
          const index = availableReports.findIndex(report =>
            report.ticker === reportGroup.ticker &&
            report.date === reportGroup.date &&
            report.time === reportGroup.time
          );

          if (index >= 0) {
            console.log('Restoring previous selection:', index);

            // Use setTimeout to ensure the state update happens after current render cycle
            setTimeout(() => {
              console.log('Setting selectedReport to:', index.toString());
              setSelectedReport(index.toString());
              loadReport(availableReports[index]);
            }, 100);

            // Clean up the previous selection storage
            sessionStorage.removeItem('previousSelectedReport');
            return;
          }
        } catch (e) {
          console.error('Error parsing previous selected report:', e);
        }
      }

      // If no valid previous selection, don't auto-select, keep current state
      console.log('No valid previous selection found');
      return;
    }
  }, [availableReports]);

  // Auto-select first report when reports are loaded (only on fresh load)
  useEffect(() => {
    if (availableReports.length > 0 && !selectedReport && !analysisData && !sessionStorage.getItem('returnToAnalysis')) {
      setSelectedReport('0');
      loadReport(availableReports[0]);
    }
  }, [availableReports, selectedReport, analysisData]);

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
          <ThemeToggle />

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
                  {availableReports.map((report, index) => {
                    const dateStr = `${report.date.slice(0, 4)}-${report.date.slice(4, 6)}-${report.date.slice(6, 8)}`;
                    const timeStr = `${report.time.slice(0, 2)}:${report.time.slice(2, 4)}`;

                    // Determine status indicator
                    let statusIndicator = '';
                    if (report.legacyFile) {
                      statusIndicator = ' (完整)';
                    } else if (report.hasComplete) {
                      statusIndicator = ' (基础+LLM)';
                    } else if (report.baseFile && !report.llmFile) {
                      statusIndicator = ' (仅基础)';
                    } else if (report.llmFile && !report.baseFile) {
                      statusIndicator = ' (仅LLM)';
                    }

                    return (
                      <option key={index} value={index.toString()}>
                        {report.ticker} - {new Date(dateStr).toLocaleDateString('zh-CN')} ({timeStr}){statusIndicator}
                      </option>
                    );
                  })}
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
                        // Clear current selected report from sessionStorage since we're using demo data
                        sessionStorage.removeItem('currentSelectedReport');
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
        <ThemeToggle />

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
                    {availableReports.map((report, index) => {
                      const dateStr = `${report.date.slice(0, 4)}-${report.date.slice(4, 6)}-${report.date.slice(6, 8)}`;

                      // Determine status indicator
                      let statusIndicator = '';
                      if (report.legacyFile) {
                        statusIndicator = ' (完整)';
                      } else if (report.hasComplete) {
                        statusIndicator = ' (基础+LLM)';
                      } else if (report.baseFile && !report.llmFile) {
                        statusIndicator = ' (仅基础)';
                      } else if (report.llmFile && !report.baseFile) {
                        statusIndicator = ' (仅LLM)';
                      }

                      return (
                        <option key={index} value={index.toString()}>
                          {report.ticker} - {new Date(dateStr).toLocaleDateString('zh-CN')}{statusIndicator}
                        </option>
                      );
                    })}
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
          <InsightsSummaryTable 
            llmInsights={analysisData.llm_insights}
            warrenBuffettAnalysis={analysisData.warren_buffett_analysis}
            peterLynchAnalysis={analysisData.peter_lynch_analysis}
            summary={analysisData.summary}
            recommendation={analysisData.recommendation}
            analysisData={analysisData}
          />
        </div>
        
        <div className="mb-6">
          <TechnicalAnalysis 
            technicalAnalysis={analysisData.technical_analysis}
            charts={analysisData.charts}
            ticker={analysisData.ticker}
            historicalData={analysisData.historical_data}
          />
        </div>
        
        <div className="mb-6">
          <CorrelationChart 
            correlationAnalysis={analysisData.correlation_analysis}
            stockInfo={analysisData.stock_info}
          />
        </div>
        
        <div className="mb-6">
          <NewsSection 
            newsAnalysis={analysisData.news_analysis}
          />
        </div>
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
