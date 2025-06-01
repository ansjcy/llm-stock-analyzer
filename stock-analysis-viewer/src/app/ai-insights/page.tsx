'use client';

import React from 'react';
import { Suspense } from 'react';
import AIInsights from '@/components/AIInsights';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { ThemeProvider } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';

function AIInsightsContent() {
  const [llmInsights, setLlmInsights] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);
  
  React.useEffect(() => {
    // Read data from sessionStorage
    const storedData = sessionStorage.getItem('aiInsightsData');
    if (storedData) {
      try {
        const parsedData = JSON.parse(storedData);
        setLlmInsights(parsedData);
      } catch (error) {
        console.error('Error parsing stored data:', error);
      }
    }
    setLoading(false);
  }, []);
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">加载中...</p>
        </div>
      </div>
    );
  }
  
  if (!llmInsights) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Theme Toggle */}
          <ThemeToggle />

          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              未找到分析数据
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              请从主页面选择一个股票分析报告。
            </p>
            <Link
              href="/"
              className="inline-flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
              onClick={() => {
                sessionStorage.setItem('returnToAnalysis', 'true');
              }}
            >
              <ArrowLeft size={20} />
              <span>返回主页</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Theme Toggle */}
        <ThemeToggle />

        {/* Header with back button */}
        <div className="mb-6">
          <Link 
            href="/"
            className="inline-flex items-center space-x-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors mb-4"
            onClick={() => {
              sessionStorage.setItem('returnToAnalysis', 'true');
            }}
          >
            <ArrowLeft size={20} />
            <span>返回主页</span>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            AI生成的详细见解
          </h1>
        </div>

        {/* AI Insights Component */}
        <AIInsights llmInsights={llmInsights} />
      </div>
    </div>
  );
}

export default function AIInsightsPage() {
  return (
    <ThemeProvider>
      <Suspense fallback={
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-300">加载中...</p>
          </div>
        </div>
      }>
        <AIInsightsContent />
      </Suspense>
    </ThemeProvider>
  );
} 