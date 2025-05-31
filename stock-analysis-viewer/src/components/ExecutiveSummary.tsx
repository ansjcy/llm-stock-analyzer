import React from 'react';
import ReactMarkdown from 'react-markdown';
import { FileText } from 'lucide-react';
import { Summary } from '@/types/analysis';
import HelpTooltip from './HelpTooltip';

interface ExecutiveSummaryProps {
  summary?: Summary;
}

export default function ExecutiveSummary({ summary }: ExecutiveSummaryProps) {
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
          h1: ({...props}) => <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-3 mt-4" {...props} />,
          h2: ({...props}) => <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 mt-4" {...props} />,
          h3: ({...props}) => <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 mb-2 mt-3" {...props} />,
          h4: ({...props}) => <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2 mt-2" {...props} />,
          p: ({...props}) => <p className="text-gray-800 dark:text-gray-300 leading-relaxed mb-3" {...props} />,
          ul: ({...props}) => <ul className="list-disc" {...props} />,
          ol: ({...props}) => <ol className="list-decimal" {...props} />,
          li: ({...props}) => <li className="text-gray-800 dark:text-gray-300 leading-relaxed" {...props} />,
          strong: ({...props}) => <strong className="font-semibold text-gray-900 dark:text-gray-100" {...props} />,
          em: ({...props}) => <em className="italic text-gray-700 dark:text-gray-400" {...props} />,
          code: ({...props}) => (
            <code className="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-200 px-1 py-0.5 rounded text-sm font-mono" {...props} />
          ),
          blockquote: ({...props}) => (
            <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-700 dark:text-gray-400 my-4" {...props} />
          )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );

  if (!summary) {
    return null;
  }

  return (
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
  );
} 