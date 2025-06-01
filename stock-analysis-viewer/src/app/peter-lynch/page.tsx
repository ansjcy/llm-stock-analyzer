'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import PeterLynchAnalysis from '@/components/PeterLynchAnalysis';
import { ThemeProvider } from '@/contexts/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';

function PeterLynchContent() {
  const router = useRouter();
  const [peterLynchAnalysis, setPeterLynchAnalysis] = React.useState<any>(null);
  const [llmInsights, setLlmInsights] = React.useState<string>('');
  const [loading, setLoading] = React.useState(true);

  useEffect(() => {
    // Get data from sessionStorage
    try {
      const peterLynchData = sessionStorage.getItem('peterLynchData');
      const llmData = sessionStorage.getItem('peterLynchLlmData');
      
      if (peterLynchData) {
        const parsedPeterData = JSON.parse(peterLynchData);
        setPeterLynchAnalysis(parsedPeterData);
      }
      
      if (llmData) {
        setLlmInsights(llmData);
      }
    } catch (error) {
      console.error('Error loading Peter Lynch analysis data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleBack = () => {
    // Check if we should return to analysis page
    const shouldReturn = sessionStorage.getItem('returnToAnalysis');
    if (shouldReturn) {
      // Clear the return flag
      sessionStorage.removeItem('returnToAnalysis');
      // Go back to analysis page
      router.push('/');
    } else {
      // Fallback to router back
      router.back();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading Peter Lynch Analysis...</p>
        </div>
      </div>
    );
  }

  if (!peterLynchAnalysis) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Theme Toggle */}
          <ThemeToggle />

          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              No Peter Lynch Analysis Data Available
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              Please go back to the main analysis page and ensure Peter Lynch analysis data is available.
            </p>
            <button
              onClick={handleBack}
              className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2 mx-auto"
            >
              <ArrowLeft size={20} />
              <span>Back to Analysis</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Theme Toggle */}
        <ThemeToggle />

        {/* Header with Back Button */}
        <div className="mb-6">
          <button
            onClick={handleBack}
            className="flex items-center space-x-2 text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors mb-4"
          >
            <ArrowLeft size={20} />
            <span>返回分析概览</span>
          </button>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              彼得·林奇成长分析报告
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              基于GARP（合理价格成长）投资理念的深度股票分析
            </p>
            <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
              <span>股票代码: {peterLynchAnalysis.ticker}</span>
              <span>分析日期: {new Date(peterLynchAnalysis.analysis_date).toLocaleDateString('zh-CN')}</span>
            </div>
          </div>
        </div>

        {/* Peter Lynch Analysis Component */}
        <PeterLynchAnalysis
          peterLynchAnalysis={peterLynchAnalysis}
          llmInsights={llmInsights}
        />
      </div>
    </div>
  );
}

export default function PeterLynchPage() {
  return (
    <ThemeProvider>
      <PeterLynchContent />
    </ThemeProvider>
  );
}