import { CorrelationAnalysis } from '@/types/analysis';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Activity, Clock, BarChart3 } from 'lucide-react';
import { useState } from 'react';
import HelpTooltip from './HelpTooltip';

interface CorrelationChartProps {
  correlationAnalysis: CorrelationAnalysis;
}

export default function CorrelationChart({ correlationAnalysis }: CorrelationChartProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('medium_term');

  // Get symbol display name
  const getSymbolDisplayName = (symbol: string) => {
    const mapping: { [key: string]: string } = {
      '^GSPC': 'S&P 500',
      '^DJI': 'Dow Jones',
      '^IXIC': 'NASDAQ',
      '^RUT': 'Russell 2000',
      'VTI': 'Total Stock Market',
      'QQQ': 'NASDAQ 100',
      'EFA': 'EAFE (Intl Developed)',
      'EEM': 'Emerging Markets',
      'XLF': 'Financial Sector',
      'XLE': 'Energy Sector',
      'XLK': 'Technology Sector',
      'XLV': 'Healthcare Sector',
      'XLI': 'Industrial Sector',
      'XLP': 'Consumer Staples',
      'XLY': 'Consumer Discretionary',
      'XLU': 'Utilities',
      'XLRE': 'Real Estate',
      'XLB': 'Materials',
      'GLD': 'Gold',
      'TLT': 'Long-term Treasuries',
      'HYG': 'High Yield Bonds',
      'VNQ': 'REITs'
    };
    return mapping[symbol] || symbol;
  };

  // Get category for symbol
  const getSymbolCategory = (symbol: string) => {
    const categories: { [key: string]: string } = {
      '^GSPC': 'Broad Market',
      '^DJI': 'Broad Market',
      '^IXIC': 'Broad Market',
      'VTI': 'Broad Market',
      'QQQ': 'Broad Market',
      '^RUT': 'Small Cap',
      'EFA': 'International',
      'EEM': 'International',
      'XLF': 'Sector',
      'XLE': 'Sector',
      'XLK': 'Sector',
      'XLV': 'Sector',
      'XLI': 'Sector',
      'XLP': 'Sector',
      'XLY': 'Sector',
      'XLU': 'Sector',
      'XLRE': 'Sector',
      'XLB': 'Sector',
      'GLD': 'Alternative',
      'TLT': 'Fixed Income',
      'HYG': 'Fixed Income',
      'VNQ': 'Alternative'
    };
    return categories[symbol] || 'Other';
  };

  // Extract correlations for the selected timeframe
  const getTimeframeData = (timeframe: string) => {
    const correlations = correlationAnalysis.correlations;
    if (!correlations || typeof correlations !== 'object') return [];

    // Handle nested structure with timeframes
    const timeframeData = correlations[timeframe as keyof typeof correlations];
    if (!timeframeData || typeof timeframeData !== 'object') return [];

    return Object.entries(timeframeData)
      .filter(([, correlation]) => typeof correlation === 'number' && !isNaN(correlation as number))
      .map(([symbol, correlation]) => ({
        symbol,
        displayName: getSymbolDisplayName(symbol),
        category: getSymbolCategory(symbol),
        correlation: Number(((correlation as number) * 100).toFixed(1))
      }))
      .sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation)); // Sort by correlation strength
  };

  const chartData = getTimeframeData(selectedTimeframe);

  // Color based on correlation strength
  const getBarColor = (correlation: number) => {
    const absCorr = Math.abs(correlation);
    if (absCorr >= 70) return correlation > 0 ? '#22c55e' : '#ef4444'; // Strong positive/negative
    if (absCorr >= 40) return correlation > 0 ? '#84cc16' : '#f97316'; // Moderate positive/negative
    return '#6b7280'; // Weak correlation
  };

  const getCorrelationStrength = (correlation: number) => {
    const absCorr = Math.abs(correlation);
    if (absCorr >= 70) return 'Strong';
    if (absCorr >= 40) return 'Moderate';
    return 'Weak';
  };

  // Check if we have any valid correlation data
  const hasCorrelationData = chartData.length > 0;

  // Timeframe options
  const timeframes = [
    { key: 'short_term', label: 'Short Term (20 days)', icon: '📊' },
    { key: 'medium_term', label: 'Medium Term (50 days)', icon: '📈' },
    { key: 'long_term', label: 'Long Term (200 days)', icon: '📉' }
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border border-gray-200 dark:border-gray-700">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
        <BarChart3 className="mr-2 text-blue-600" />
        市场相关性分析
        <HelpTooltip 
          content="市场相关性分析衡量股票价格走势与主要市场指数和行业的一致程度。这有助于评估分散投资效益和系统性风险敞口。"
          title="什么是相关性分析？"
          size="md"
          className="ml-2"
        />
      </h2>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">贝塔系数（系统性风险）</span>
            <HelpTooltip 
              content="贝塔系数衡量系统性风险 - 股票相对于市场的波动程度。贝塔=1与市场同步，贝塔>1波动性更高（风险/回报更高），贝塔<1波动性较低（风险/回报较低）。贝塔<0与市场反向运动。"
              title="贝塔系数 - 系统性风险衡量"
              size="sm"
            />
          </div>
          <div className="flex items-center space-x-2 mt-1">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {typeof correlationAnalysis.beta === 'number' ? correlationAnalysis.beta.toFixed(3) : 'N/A'}
            </div>
            {typeof correlationAnalysis.beta === 'number' && (
              <div className={`px-2 py-1 rounded-full text-xs font-bold ${
                correlationAnalysis.beta > 1.2 ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' :
                correlationAnalysis.beta < 0.8 ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' :
                'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300'
              }`}>
                {correlationAnalysis.beta > 1.2 ? '高风险' :
                 correlationAnalysis.beta < 0.8 ? '低风险' : '中等风险'}
              </div>
            )}
          </div>
        </div>

        {typeof correlationAnalysis.diversification_score === 'number' && (
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">分散化得分</span>
              <HelpTooltip 
                content="分散化得分表明这只股票为投资组合提供分散化效益的程度。得分越高意味着与主要指数的相关性越低，与其他投资组合时提供更好的风险降低效果。"
                title="投资组合分散化得分"
                size="sm"
              />
            </div>
            <div className="flex items-center space-x-2 mt-1">
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{correlationAnalysis.diversification_score.toFixed(1)}%</div>
              <div className={`px-2 py-1 rounded-full text-xs font-bold ${
                correlationAnalysis.diversification_score >= 70 ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' :
                correlationAnalysis.diversification_score >= 40 ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' :
                'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
              }`}>
                {correlationAnalysis.diversification_score >= 70 ? '充分分散' :
                 correlationAnalysis.diversification_score >= 40 ? '适度分散' : '集中投资'}
              </div>
            </div>
          </div>
        )}

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">分析指数数量</span>
            <HelpTooltip 
              content="与此股票比较的市场指数和基准数量。更多比较提供了股票在不同市场板块相关性模式的更全面视角。"
              title="分析覆盖范围"
              size="sm"
            />
          </div>
          <div className="mt-1">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{hasCorrelationData ? chartData.length : 'N/A'}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-400">当前时间框架</div>
          </div>
        </div>
      </div>

      {/* Timeframe Selector */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center">
          <Clock className="mr-2 text-blue-600" size={20} />
          Select Timeframe
        </h3>
        <div className="flex flex-wrap gap-2">
          {timeframes.map((timeframe) => (
            <button
              key={timeframe.key}
              onClick={() => setSelectedTimeframe(timeframe.key)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedTimeframe === timeframe.key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {timeframe.icon} {timeframe.label}
            </button>
          ))}
        </div>
      </div>

      {/* Correlation Chart */}
      {hasCorrelationData ? (
        <>
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4">
              Correlation with Market Indices - {timeframes.find(t => t.key === selectedTimeframe)?.label}
            </h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="displayName" 
                    tick={{ fontSize: 10 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `${value}%`}
                    domain={[-100, 100]}
                  />
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload[0]) {
                        const data = payload[0].payload as {
                          displayName: string;
                          correlation: number;
                          category: string;
                        };
                        return (
                          <div className="bg-white dark:bg-gray-800 p-3 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg">
                            <p className="font-semibold text-gray-900 dark:text-white">{data.displayName}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{data.category}</p>
                            <p className="text-sm">
                              相关性: <span className="font-bold">{data.correlation}%</span>
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {getCorrelationStrength(data.correlation)}
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="correlation" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getBarColor(entry.correlation)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Correlation Details by Category */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Correlations */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-md font-semibold mb-3 text-gray-900">Strongest Correlations</h4>
              <div className="space-y-2">
                {chartData.slice(0, 5).map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: getBarColor(item.correlation) }}
                      />
                      <span className="text-sm font-medium text-gray-700">{item.displayName}</span>
                      <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                        {item.category}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-gray-900">{item.correlation}%</div>
                      <div className="text-xs text-gray-500">{getCorrelationStrength(Math.abs(item.correlation))}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Diversification Opportunities */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-md font-semibold mb-3 text-gray-900">Diversification Opportunities</h4>
              <div className="space-y-2">
                {(() => {
                  // First try assets with correlation < 60% (more lenient threshold)
                  const lowCorrAssets = chartData.filter(item => Math.abs(item.correlation) < 60);
                  
                  if (lowCorrAssets.length > 0) {
                    return lowCorrAssets.slice(0, 5).map((item, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: getBarColor(item.correlation) }}
                          />
                          <span className="text-sm font-medium text-gray-700">{item.displayName}</span>
                          <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                            {item.category}
                          </span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-bold text-gray-900">{item.correlation}%</div>
                          <div className="text-xs text-green-600">
                            {Math.abs(item.correlation) < 30 ? 'Excellent diversification' :
                             Math.abs(item.correlation) < 50 ? 'Good diversification' : 'Moderate diversification'}
                          </div>
                        </div>
                      </div>
                    ));
                  }
                  
                  // If no assets < 60%, show the lowest correlations available
                  const lowestCorrelations = [...chartData]
                    .sort((a, b) => Math.abs(a.correlation) - Math.abs(b.correlation))
                    .slice(0, 5);
                  
                  if (lowestCorrelations.length > 0) {
                    return (
                      <>
                        <div className="text-xs text-amber-600 mb-2 italic">
                          All assets show high correlation. Showing relatively lower correlations:
                        </div>
                        {lowestCorrelations.map((item, index) => (
                          <div key={index} className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <div 
                                className="w-3 h-3 rounded-full" 
                                style={{ backgroundColor: getBarColor(item.correlation) }}
                              />
                              <span className="text-sm font-medium text-gray-700">{item.displayName}</span>
                              <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                                {item.category}
                              </span>
                            </div>
                            <div className="text-right">
                              <div className="text-sm font-bold text-gray-900">{item.correlation}%</div>
                              <div className="text-xs text-amber-600">Best available option</div>
                            </div>
                          </div>
                        ))}
                      </>
                    );
                  }
                  
                  return (
                    <div className="text-sm text-gray-500 italic">
                      No correlation data available for diversification analysis
                    </div>
                  );
                })()}
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="text-center py-8">
          <Activity className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Correlation Data Available</h3>
          <p className="text-gray-500">
            Correlation analysis data is not available for this stock.
          </p>
        </div>
      )}
    </div>
  );
} 