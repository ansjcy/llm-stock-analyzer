import { NewsAnalysis } from '@/types/analysis';
import { Newspaper, ExternalLink } from 'lucide-react';
import HelpTooltip from './HelpTooltip';

interface NewsSectionProps {
  newsAnalysis: NewsAnalysis;
}

export default function NewsSection({ newsAnalysis }: NewsSectionProps) {
  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'Unknown date';
    
    try {
      // Handle different date formats
      let date;
      
      // Handle formats like "2025-05-30 20:44:38" (from publish_time)
      if (dateString.includes(' ') && !dateString.includes('T')) {
        // Replace space with T and add Z for ISO format
        date = new Date(dateString.replace(' ', 'T') + 'Z');
      } else {
        // Handle ISO format like "2025-01-09T12:30:00Z" (from published)
        date = new Date(dateString);
      }
      
      if (isNaN(date.getTime())) {
        return dateString; // Return original string if parsing fails
      }
      
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  if (newsAnalysis.articles_found === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
          <Newspaper className="mr-2 text-blue-600" />
          近期新闻分析
          <HelpTooltip 
            content="新闻分析评估可能影响股价的近期头条新闻、公司公告和市场发展。包括财报、产品发布、监管变化和可能影响投资者情绪的行业趋势。"
            title="新闻分析概述"
            size="md"
            className="ml-2"
          />
        </h2>
        <div className="text-center py-8">
          <Newspaper className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">暂无近期新闻</h3>
          <p className="text-gray-500 dark:text-gray-400">
            暂未找到该股票的近期新闻文章。
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border border-gray-200 dark:border-gray-700">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
        <Newspaper className="mr-2 text-blue-600" />
        近期新闻分析
        <HelpTooltip 
          content="新闻分析评估可能影响股价的近期头条新闻、公司公告和市场发展。包括财报、产品发布、监管变化和可能影响投资者情绪的行业趋势。"
          title="新闻分析概述"
          size="md"
          className="ml-2"
        />
      </h2>

      <div className="mb-4">
        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
          <span>发现文章: <span className="font-semibold text-gray-900 dark:text-white">{newsAnalysis.articles_found}</span></span>
          <HelpTooltip 
            content="找到并分析的与该股票相关的新闻文章数量。更多文章提供了对市场情绪和公司发展的更广泛视角。新闻的质量和时效性也是重要因素。"
            title="新闻覆盖范围"
            size="sm"
          />
        </div>
      </div>

      {newsAnalysis.recent_articles && newsAnalysis.recent_articles.length > 0 ? (
        <div className="space-y-4">
          {newsAnalysis.recent_articles.map((article, index) => (
            <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white line-clamp-2">
                  {article.title}
                </h3>
                <div className="text-sm text-gray-500 dark:text-gray-400 ml-4 flex-shrink-0">
                  {formatDate((article as { publish_time?: string; published?: string }).publish_time || article.published)}
                </div>
              </div>
              
              <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                {article.summary}
              </p>
              
              {article.url && (
                <div className="mt-3">
                  <a 
                    href={article.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium flex items-center"
                  >
                    阅读完整文章
                    <ExternalLink size={14} className="ml-1" />
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <Newspaper className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">暂无近期新闻</h3>
          <p className="text-gray-500 dark:text-gray-400">
            暂未找到该股票的近期新闻文章。
          </p>
        </div>
      )}
    </div>
  );
} 