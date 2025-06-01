'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Moon, Sun } from 'lucide-react';
import CombinedExecutiveSummary from '@/components/CombinedExecutiveSummary';
import { StockAnalysisResult } from '@/types/analysis';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';

function ExecutiveSummaryPageContent() {
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();
  const [analysisData, setAnalysisData] = useState<StockAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get data from sessionStorage
    const storedData = sessionStorage.getItem('executiveSummaryData');
    if (storedData) {
      try {
        const data = JSON.parse(storedData);
        setAnalysisData(data);
      } catch (error) {
        console.error('Error parsing stored analysis data:', error);
        // Redirect back to main page if data is invalid
        router.push('/');
        return;
      }
    } else {
      // No data found, redirect to main page
      router.push('/');
      return;
    }
    setLoading(false);
  }, [router]);

  const handleBackClick = () => {
    // Clear the stored data
    sessionStorage.removeItem('executiveSummaryData');
    // Set the flag to indicate we're returning to analysis
    sessionStorage.setItem('returnToAnalysis', 'true');
    // Navigate back
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-lg text-gray-600 dark:text-gray-400">加载中...</div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-lg text-gray-600 dark:text-gray-400">未找到分析数据</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
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

        {/* Header */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleBackClick}
                className="flex items-center space-x-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
                <span className="text-sm font-medium">返回分析报告</span>
              </button>
            </div>
            <div className="text-right">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                执行摘要与投资建议
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {analysisData.ticker} - {new Date(analysisData.analysis_date).toLocaleDateString('zh-CN')}
              </p>
            </div>
          </div>
        </div>

        {/* Combined Executive Summary and Investment Recommendation */}
        <div className="space-y-8">
          <CombinedExecutiveSummary 
            summary={analysisData.summary}
            recommendation={analysisData.recommendation}
          />
        </div>
      </div>
    </div>
  );
}

export default function ExecutiveSummaryPage() {
  return (
    <ThemeProvider>
      <ExecutiveSummaryPageContent />
    </ThemeProvider>
  );
} 