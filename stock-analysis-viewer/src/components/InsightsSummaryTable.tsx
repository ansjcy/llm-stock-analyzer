'use client';

import React from 'react';
import { Brain, DollarSign, TrendingUp, TrendingDown, Activity, ChevronRight, FileText, BarChart3 } from 'lucide-react';
import { LLMInsights, WarrenBuffettAnalysis, PeterLynchAnalysis, Summary, Recommendation } from '@/types/analysis';
import { useRouter } from 'next/navigation';

interface InsightsSummaryTableProps {
  llmInsights?: LLMInsights;
  warrenBuffettAnalysis?: WarrenBuffettAnalysis;
  peterLynchAnalysis?: PeterLynchAnalysis;
  summary?: Summary;
  recommendation?: Recommendation;
  analysisData?: any; // Full analysis data to pass to the subpage
}

export default function InsightsSummaryTable({ 
  llmInsights, 
  warrenBuffettAnalysis,
  peterLynchAnalysis,
  summary, 
  recommendation,
  analysisData 
}: InsightsSummaryTableProps) {
  const router = useRouter();

  const handleAIInsightsClick = () => {
    if (llmInsights) {
      // Store data in sessionStorage to avoid URL length limits
      sessionStorage.setItem('aiInsightsData', JSON.stringify(llmInsights));
      // Store current page state to restore when returning
      sessionStorage.setItem('returnToAnalysis', 'true');
      // Store current selected report to restore dropdown selection
      const currentSelectedReport = sessionStorage.getItem('currentSelectedReport');
      if (currentSelectedReport) {
        sessionStorage.setItem('previousSelectedReport', currentSelectedReport);
      }
      router.push('/ai-insights');
    }
  };

  const handleWarrenBuffettClick = () => {
    if (warrenBuffettAnalysis) {
      // Store data in sessionStorage to avoid URL length limits
      sessionStorage.setItem('warrenBuffettData', JSON.stringify(warrenBuffettAnalysis));
      if (llmInsights?.warren_buffett) {
        sessionStorage.setItem('warrenBuffettLlmData', llmInsights.warren_buffett);
      }
      // Store current page state to restore when returning
      sessionStorage.setItem('returnToAnalysis', 'true');
      // Store current selected report to restore dropdown selection
      const currentSelectedReport = sessionStorage.getItem('currentSelectedReport');
      if (currentSelectedReport) {
        sessionStorage.setItem('previousSelectedReport', currentSelectedReport);
      }
      router.push('/warren-buffett');
    }
  };

  const handlePeterLynchClick = () => {
    if (peterLynchAnalysis) {
      // Store data in sessionStorage to avoid URL length limits
      sessionStorage.setItem('peterLynchData', JSON.stringify(peterLynchAnalysis));
      if (llmInsights?.peter_lynch) {
        sessionStorage.setItem('peterLynchLlmData', llmInsights.peter_lynch);
      }
      // Store current page state to restore when returning
      sessionStorage.setItem('returnToAnalysis', 'true');
      // Store current selected report to restore dropdown selection
      const currentSelectedReport = sessionStorage.getItem('currentSelectedReport');
      if (currentSelectedReport) {
        sessionStorage.setItem('previousSelectedReport', currentSelectedReport);
      }
      router.push('/peter-lynch');
    }
  };

  const handleExecutiveSummaryClick = () => {
    if (analysisData && (summary || recommendation)) {
      // Store full analysis data in sessionStorage
      sessionStorage.setItem('executiveSummaryData', JSON.stringify(analysisData));
      // Store current page state to restore when returning
      sessionStorage.setItem('returnToAnalysis', 'true');
      // Store current selected report to restore dropdown selection
      const currentSelectedReport = sessionStorage.getItem('currentSelectedReport');
      if (currentSelectedReport) {
        sessionStorage.setItem('previousSelectedReport', currentSelectedReport);
      }
      router.push('/executive-summary');
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal.toLowerCase()) {
      case 'buy':
      case 'strong_buy':
      case '买入':
      case '强烈买入':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300';
      case 'sell':
      case 'strong_sell':
      case '卖出':
      case '强烈卖出':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300';
      case 'hold':
      case 'neutral':
      case '持有':
      case '中性':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300';
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal.toLowerCase()) {
      case 'buy':
      case 'strong_buy':
      case '买入':
      case '强烈买入':
        return <TrendingUp size={16} />;
      case 'sell':
      case 'strong_sell':
      case '卖出':
      case '强烈卖出':
        return <TrendingDown size={16} />;
      default:
        return <Activity size={16} />;
    }
  };

  const formatSignalText = (signal: string) => {
    const signalTranslations: { [key: string]: string } = {
      'buy': '买入',
      'strong_buy': '强烈买入',
      'sell': '卖出',
      'strong_sell': '强烈卖出',
      'hold': '持有',
      'neutral': '中性'
    };
    
    return signalTranslations[signal.toLowerCase()] || signal;
  };

  const getSummaryText = (insights: LLMInsights) => {
    const sections = [];
    if (insights.technical) sections.push('技术分析');
    if (insights.fundamental) sections.push('基本面分析');
    if (insights.news) sections.push('新闻情绪');
    return `包含 ${sections.join('、')} 的AI综合见解`;
  };

  const formatCurrency = (value: number | undefined) => {
    if (!value) return 'N/A';
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600 dark:text-green-400';
    if (percentage >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          分析见解概览
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          点击行查看详细分析
        </p>
      </div>

      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {/* Executive Summary & Investment Recommendation Row */}
        {(summary || recommendation) && (
          <div 
            onClick={handleExecutiveSummaryClick}
            className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <FileText className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    执行摘要与投资建议
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    综合分析摘要和具体投资指导建议
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    详细内容
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    点击查看完整分析
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </div>
          </div>
        )}

        {/* AI Insights Row */}
        {llmInsights && (
          <div 
            onClick={handleAIInsightsClick}
            className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    AI生成的详细见解
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {getSummaryText(llmInsights)}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    详细见解
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    点击查看完整分析
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </div>
          </div>
        )}

        {/* Warren Buffett Analysis Row */}
        {warrenBuffettAnalysis && (
          <div 
            onClick={handleWarrenBuffettClick}
            className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                  <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    沃伦·巴菲特分析
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    基于价值投资原则的综合评估
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className={`px-3 py-1 rounded-full flex items-center space-x-1 ${getSignalColor(warrenBuffettAnalysis.overall_signal)}`}>
                    {getSignalIcon(warrenBuffettAnalysis.overall_signal)}
                    <span className="text-sm font-medium">
                      {formatSignalText(warrenBuffettAnalysis.overall_signal)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${getScoreColor(warrenBuffettAnalysis.score_percentage)}`}>
                    {warrenBuffettAnalysis.score_percentage.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    质量评分
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-purple-600 dark:text-purple-400">
                    {warrenBuffettAnalysis.confidence.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    信心度
                  </div>
                </div>
                {warrenBuffettAnalysis.intrinsic_value_analysis?.intrinsic_value && (
                  <div className="text-right">
                    <div className="text-sm font-semibold text-green-600 dark:text-green-400">
                      {formatCurrency(warrenBuffettAnalysis.intrinsic_value_analysis.intrinsic_value)}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-500">
                      内在价值
                    </div>
                  </div>
                )}
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </div>
          </div>
        )}

        {/* Peter Lynch Analysis Row */}
        {peterLynchAnalysis && (
          <div 
            onClick={handlePeterLynchClick}
            className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    彼得·林奇分析
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    基于GARP（合理价格成长）投资理念的评估
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className={`px-3 py-1 rounded-full flex items-center space-x-1 ${getSignalColor(peterLynchAnalysis.overall_signal)}`}>
                    {getSignalIcon(peterLynchAnalysis.overall_signal)}
                    <span className="text-sm font-medium">
                      {formatSignalText(peterLynchAnalysis.overall_signal)}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${getScoreColor(peterLynchAnalysis.score_percentage)}`}>
                    {peterLynchAnalysis.score_percentage.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    GARP评分
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-purple-600 dark:text-purple-400">
                    {peterLynchAnalysis.confidence.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    信心度
                  </div>
                </div>
                {peterLynchAnalysis.garp_analysis?.metrics?.peg_ratio && (
                  <div className="text-right">
                    <div className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                      {peterLynchAnalysis.garp_analysis.metrics.peg_ratio.toFixed(2)}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-500">
                      PEG比率
                    </div>
                  </div>
                )}
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Empty state */}
      {!llmInsights && !warrenBuffettAnalysis && !peterLynchAnalysis && !summary && !recommendation && (
        <div className="px-6 py-8 text-center">
          <div className="text-gray-500 dark:text-gray-400">
            暂无可用的分析见解
          </div>
        </div>
      )}
    </div>
  );
} 