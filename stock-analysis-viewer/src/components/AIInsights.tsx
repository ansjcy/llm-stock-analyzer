import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Brain, TrendingUp, Target, Newspaper, FileText, DollarSign } from 'lucide-react';
import { LLMInsights, Recommendation, Summary } from '@/types/analysis';
import HelpTooltip from './HelpTooltip';

interface AIInsightsProps {
  llmInsights: LLMInsights;
  recommendation?: Recommendation;
  summary?: Summary;
}

export default function AIInsights({ llmInsights, recommendation, summary }: AIInsightsProps) {
  const MarkdownContent = ({ content }: { content: string }) => (
    <div className="prose prose-sm max-w-none 
                    prose-headings:text-gray-800 prose-headings:font-semibold 
                    prose-p:text-gray-800 prose-p:leading-relaxed prose-p:mb-4
                    prose-li:text-gray-800 prose-li:leading-relaxed
                    prose-strong:text-gray-900 prose-strong:font-semibold
                    prose-em:text-gray-700 prose-em:italic
                    prose-ul:mb-4 prose-ol:mb-4 prose-ul:space-y-2 prose-ol:space-y-2
                    prose-li:mb-1
                    dark:prose-headings:text-gray-200 dark:prose-p:text-gray-300 
                    dark:prose-li:text-gray-300 dark:prose-strong:text-gray-100
                    dark:prose-em:text-gray-400
                    font-sans markdown-content">
      <style dangerouslySetInnerHTML={{
        __html: `
          .markdown-content ul, .markdown-content ol {
            padding-left: 1.5rem;
            margin-bottom: 1rem;
          }
          .markdown-content li {
            margin-bottom: 0.25rem;
          }
          .markdown-content li ul, .markdown-content li ol {
            margin-top: 0.5rem;
            margin-left: 1rem;
            padding-left: 1rem;
          }
          .markdown-content li li {
            margin-bottom: 0.125rem;
          }
          .markdown-content li li ul, .markdown-content li li ol {
            margin-left: 0.75rem;
            padding-left: 0.75rem;
          }
          .markdown-content strong {
            font-weight: 600;
            color: inherit;
          }
        `
      }} />
      <ReactMarkdown
        components={{
          h1: ({node, ...props}) => <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3 mt-4" {...props} />,
          h2: ({node, ...props}) => <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 mt-4" {...props} />,
          h3: ({node, ...props}) => <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 mt-3" {...props} />,
          h4: ({node, ...props}) => <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2 mt-2" {...props} />,
          p: ({node, ...props}) => <p className="text-gray-800 dark:text-gray-300 leading-relaxed mb-3" {...props} />,
          ul: ({node, ...props}) => <ul className="list-disc" {...props} />,
          ol: ({node, ...props}) => <ol className="list-decimal" {...props} />,
          li: ({node, ...props}) => <li className="text-gray-800 dark:text-gray-300 leading-relaxed" {...props} />,
          strong: ({node, ...props}) => <strong className="font-semibold text-gray-900 dark:text-gray-100" {...props} />,
          em: ({node, ...props}) => <em className="italic text-gray-700 dark:text-gray-400" {...props} />,
          code: ({node, ...props}) => (
            <code className="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200 px-1 py-0.5 rounded text-sm font-mono" {...props} />
          ),
          blockquote: ({node, ...props}) => (
            <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-700 dark:text-gray-400 my-4" {...props} />
          )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* AI Insights */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
          <Brain className="mr-2 text-blue-600" />
          AI生成的见解
          <HelpTooltip 
            content="AI生成的见解结合多个数据源和分析技术，提供对技术指标、基本面指标和市场情绪的全面、智能解读。"
            title="AI分析概述"
            size="md"
            className="ml-2"
          />
        </h2>

        <div className="grid grid-cols-1 gap-6">
          {llmInsights.technical && (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <TrendingUp className="text-blue-600" size={20} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">技术分析</h3>
                <HelpTooltip 
                  content="AI对技术指标、图表形态和价格走势的解读。这种分析结合多个技术信号，提供关于入场/出场时机和趋势方向的可操作见解。"
                  title="AI技术分析"
                  size="sm"
                />
              </div>
              <MarkdownContent content={llmInsights.technical} />
            </div>
          )}

          {llmInsights.fundamental && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <DollarSign className="text-green-600" size={20} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">基本面分析</h3>
                <HelpTooltip 
                  content="AI对公司基本面的评估，包括财务健康状况、估值指标、竞争地位和商业模式实力。这有助于评估股票的内在价值和长期前景。"
                  title="AI基本面分析"
                  size="sm"
                />
              </div>
              <MarkdownContent content={llmInsights.fundamental} />
            </div>
          )}

          {llmInsights.news && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Newspaper className="text-purple-600" size={20} />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">新闻与情绪</h3>
                <HelpTooltip 
                  content="AI对近期新闻、市场情绪和公众认知的分析。包括对财报、分析师意见、行业趋势和可能影响股价的社交媒体情绪的评估。"
                  title="AI情绪分析"
                  size="sm"
                />
              </div>
              <MarkdownContent content={llmInsights.news} />
            </div>
          )}
        </div>
      </div>

      {/* Investment Recommendation */}
      {recommendation && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2 mb-6">
            <Target className="text-green-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">投资建议</h2>
            <HelpTooltip 
              content="基于所有分析组件的综合投资建议。包括具体的买入/卖出/持有建议、目标价格、风险评估和针对不同投资者类型的仓位配置指导。"
              title="投资建议"
              size="md"
            />
          </div>
          <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg p-6">
            <MarkdownContent content={recommendation.full_analysis} />
          </div>
        </div>
      )}

      {/* Executive Summary */}
      {summary && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2 mb-6">
            <FileText className="text-indigo-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">执行摘要</h2>
            <HelpTooltip 
              content="将所有分析结果合并为关键要点的高级概述。非常适合快速决策，本节将复杂分析提炼为可操作的见解和主要投资主题。"
              title="执行摘要"
              size="md"
            />
          </div>
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg p-6">
            <MarkdownContent content={summary.executive_summary} />
          </div>
        </div>
      )}
    </div>
  );
} 