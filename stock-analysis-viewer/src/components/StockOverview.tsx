import { StockInfo, PEHistory } from '@/types/analysis';
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart3 } from 'lucide-react';
import HelpTooltip from './HelpTooltip';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface StockOverviewProps {
  ticker: string;
  stockInfo: StockInfo;
  analysisDate: string;
}

// Box and Whisker Plot Component for Price Ranges
const PriceRangeChart = ({ 
  low, 
  high, 
  current, 
  label 
}: { 
  low: number; 
  high: number; 
  current: number; 
  label: string; 
}) => {
  const range = high - low;
  const currentPosition = range > 0 ? ((current - low) / range) * 100 : 50;
  
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
        <span>${low.toFixed(2)}</span>
        <span className="font-medium">${current.toFixed(2)}</span>
        <span>${high.toFixed(2)}</span>
      </div>
      <div className="relative h-6 bg-gray-200 dark:bg-gray-600 rounded-full">
        {/* Range bar */}
        <div className="absolute inset-y-0 left-0 right-0 bg-gradient-to-r from-red-300 via-yellow-300 to-green-300 rounded-full"></div>
        
        {/* Low marker */}
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-red-600 rounded-l-full"></div>
        
        {/* High marker */}
        <div className="absolute right-0 top-0 bottom-0 w-1 bg-green-600 rounded-r-full"></div>
        
        {/* Current price marker */}
        <div 
          className="absolute top-0 bottom-0 w-2 bg-blue-600 rounded-full transform -translate-x-1/2 shadow-lg"
          style={{ left: `${currentPosition}%` }}
        >
          <div className="absolute -top-1 -bottom-1 left-1/2 transform -translate-x-1/2 w-1 bg-blue-800 rounded-full"></div>
        </div>
      </div>
      <div className="text-center mt-1">
        <span className="text-xs text-gray-600 dark:text-gray-400">
          {currentPosition.toFixed(1)}% of {label}
        </span>
      </div>
    </div>
  );
};

// PE Ratio Chart Component
const PERatioChart = ({ peHistory }: { peHistory: PEHistory }) => {
  if (!peHistory.historical_data || peHistory.historical_data.length === 0) {
    return (
      <div className="text-gray-600 dark:text-gray-400 text-center py-4">
        暂无历史市盈率数据
      </div>
    );
  }

  // Process data for chart (take last 90 days for better readability)
  const chartData = peHistory.historical_data
    .slice(-90)
    .map(item => ({
      date: new Date(item.Date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
      pe: item.PE_Ratio,
      price: item.Close
    }));

  const CustomTooltip = ({ active, payload, label }: {
    active?: boolean;
    payload?: Array<{
      value: number;
      payload: { price: number };
    }>;
    label?: string;
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg p-3 shadow-lg">
          <p className="text-gray-600 dark:text-gray-300">{`日期: ${label}`}</p>
          <p className="text-blue-600 dark:text-blue-400">{`市盈率: ${payload[0].value.toFixed(2)}`}</p>
          <p className="text-green-600 dark:text-green-400">{`股价: $${payload[0].payload.price.toFixed(2)}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            tickMargin={5}
            interval="preserveStartEnd"
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            tickMargin={5}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Average PE line */}
          {peHistory.avg_pe_1y && (
            <ReferenceLine 
              y={peHistory.avg_pe_1y} 
              stroke="#6B7280" 
              strokeDasharray="5 5"
              label={{ value: `平均: ${peHistory.avg_pe_1y.toFixed(1)}`, position: "top" }}
            />
          )}
          
          <Line 
            type="monotone" 
            dataKey="pe" 
            stroke="#3B82F6" 
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

// PE Ratio Summary Stats Component
const PERatioStats = ({ peHistory }: { peHistory: PEHistory }) => {
  const formatPE = (value: number | undefined) => {
    if (!value || typeof value !== 'number') return 'N/A';
    return value.toFixed(2);
  };

  const getPercentileColor = (percentile: number | undefined) => {
    if (!percentile) return 'text-gray-600 dark:text-gray-400';
    if (percentile <= 25) return 'text-green-600 dark:text-green-400';
    if (percentile <= 50) return 'text-yellow-600 dark:text-yellow-400';
    if (percentile <= 75) return 'text-orange-600 dark:text-orange-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
      <div className="text-center">
        <div className="text-sm text-gray-600 dark:text-gray-400">当前市盈率</div>
        <div className="text-lg font-bold text-gray-900 dark:text-white">
          {formatPE(peHistory.current_pe)}
        </div>
      </div>
      
      <div className="text-center">
        <div className="text-sm text-gray-600 dark:text-gray-400">一年平均</div>
        <div className="text-lg font-bold text-gray-900 dark:text-white">
          {formatPE(peHistory.avg_pe_1y)}
        </div>
      </div>
      
      <div className="text-center">
        <div className="text-sm text-gray-600 dark:text-gray-400">区间 (最低-最高)</div>
        <div className="text-lg font-bold text-gray-900 dark:text-white">
          {formatPE(peHistory.min_pe_1y)} - {formatPE(peHistory.max_pe_1y)}
        </div>
      </div>
      
      <div className="text-center">
        <div className="text-sm text-gray-600 dark:text-gray-400">历史百分位</div>
        <div className={`text-lg font-bold ${getPercentileColor(peHistory.pe_percentile)}`}>
          {peHistory.pe_percentile ? `${peHistory.pe_percentile.toFixed(0)}%` : 'N/A'}
        </div>
      </div>
    </div>
  );
};

export default function StockOverview({ ticker, stockInfo, analysisDate }: StockOverviewProps) {
  const formatCurrency = (value: number | null | undefined) => {
    if (!value || typeof value !== 'number') return 'N/A';
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
    return `$${value.toFixed(2)}`;
  };

  const formatNumber = (value: number | null | undefined) => {
    if (!value || typeof value !== 'number') return 'N/A';
    return new Intl.NumberFormat().format(value);
  };

  const formatPrice = (value: number | null | undefined) => {
    if (!value || typeof value !== 'number') return 'N/A';
    return `$${value.toFixed(2)}`;
  };

  // Helper function to safely access 52-week data with fallback keys
  const get52WeekLow = () => {
    return stockInfo.week_52_low || stockInfo['52_week_low'] || null;
  };

  const get52WeekHigh = () => {
    return stockInfo.week_52_high || stockInfo['52_week_high'] || null;
  };

  // Safe calculations with null checks
  const safeCurrentPrice = stockInfo.current_price || 0;
  const safePreviousClose = stockInfo.previous_close || 0;
  const priceChange = safeCurrentPrice - safePreviousClose;
  const priceChangePercent = safePreviousClose !== 0 ? (priceChange / safePreviousClose) * 100 : 0;
  const isPositive = priceChange >= 0;

  const week52Low = get52WeekLow();
  const week52High = get52WeekHigh();

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{ticker}</h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">{stockInfo.name}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">分析日期: {new Date(analysisDate).toLocaleDateString('zh-CN')}</p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-gray-900 dark:text-white">
            {formatPrice(stockInfo.current_price)}
          </div>
          <div className={`flex items-center justify-end space-x-1 ${isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
            <span className="font-semibold">
              {isPositive ? '+' : ''}{priceChange.toFixed(2)} ({isPositive ? '+' : ''}{priceChangePercent.toFixed(2)}%)
            </span>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="text-blue-600" size={20} />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">昨日收盘</span>
            <HelpTooltip 
              content="股票在前一个交易日的收盘价。这是计算每日价格变化和百分比涨跌的基准。"
              title="昨日收盘价"
              size="sm"
            />
          </div>
          <div className="text-xl font-bold text-gray-900 dark:text-white">
            {formatPrice(stockInfo.previous_close)}
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="text-green-600" size={20} />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">当日区间</span>
            <HelpTooltip 
              content="股票在当前交易日内的最低价和最高价。这显示了股票的日内波动性和交易区间。"
              title="当日交易区间"
              size="sm"
            />
          </div>
          {stockInfo.day_low && stockInfo.day_high && stockInfo.current_price ? (
            <PriceRangeChart 
              low={stockInfo.day_low}
              high={stockInfo.day_high}
              current={stockInfo.current_price}
              label="daily range"
            />
          ) : (
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {formatPrice(stockInfo.day_low)} - {formatPrice(stockInfo.day_high)}
            </div>
          )}
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="text-purple-600" size={20} />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">52周区间</span>
            <HelpTooltip 
              content="股票在过去52周（一年）内的最低价和最高价。这提供了股票长期价格走势的视角以及当前相对于年度区间的位置。"
              title="52周交易区间"
              size="sm"
            />
          </div>
          {week52Low && week52High && stockInfo.current_price ? (
            <PriceRangeChart 
              low={week52Low}
              high={week52High}
              current={stockInfo.current_price}
              label="52-week range"
            />
          ) : (
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {formatPrice(week52Low)} - {formatPrice(week52High)}
            </div>
          )}
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <DollarSign className="text-yellow-600" size={20} />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">市值</span>
            <HelpTooltip 
              content="市值是公司在股票市场的总价值。计算方法为当前股价乘以流通股数。这表明了公司的规模和投资级别。"
              title="市场资本化"
              size="sm"
            />
          </div>
          <div className="text-lg font-bold text-gray-900 dark:text-white">
            {formatCurrency(stockInfo.market_cap)}
          </div>
        </div>

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="text-indigo-600" size={20} />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">成交量</span>
            <HelpTooltip 
              content="当前或最近交易日的股票交易量。高成交量通常表明投资者兴趣浓厚，可以确认价格走势。低成交量可能表明兴趣有限或流动性不足。"
              title="交易量"
              size="sm"
            />
          </div>
          <div className="text-lg font-bold text-gray-900 dark:text-white">
            {formatNumber(stockInfo.volume)}
          </div>
        </div>

        {stockInfo.pe_ratio && (
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <TrendingUp className="text-orange-600" size={20} />
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">市盈率</span>
              <HelpTooltip 
                content="市盈率将公司股价与每股收益进行比较。它表明投资者愿意为每美元收益支付多少钱。较高的市盈率可能表明增长预期，而较低的比率可能表明价值机会或增长较慢。"
                title="市盈率"
                size="sm"
              />
            </div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {typeof stockInfo.pe_ratio === 'number' ? stockInfo.pe_ratio.toFixed(2) : 'N/A'}
            </div>
          </div>
        )}

        {stockInfo.beta && (
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Activity className="text-red-600" size={20} />
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">贝塔系数</span>
              <HelpTooltip 
                content="贝塔系数衡量股票相对于整体市场的波动性。贝塔=1表示与市场同步。贝塔>1表示波动性较高（风险/回报更高）。贝塔<1表示波动性较低（风险/回报较低）。"
                title="贝塔系数（市场风险）"
                size="sm"
              />
            </div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {typeof stockInfo.beta === 'number' ? stockInfo.beta.toFixed(3) : 'N/A'}
            </div>
          </div>
        )}

        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Activity className="text-teal-600" size={20} />
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">行业</span>
            <HelpTooltip 
              content="公司所属的商业部门或行业类别。行业分类帮助投资者了解公司的商业模式、竞争环境以及可能影响其表现的经济因素。"
              title="商业部门"
              size="sm"
            />
          </div>
          <div className="text-lg font-bold text-gray-900 dark:text-white">
            {stockInfo.sector || 'N/A'}
          </div>
        </div>
      </div>

      {/* PE Ratio Chart and Stats - Only show if PE history is available */}
      {stockInfo.pe_history && (
        <div className="mt-6">
          <div className="flex items-center space-x-2 mb-4">
            <BarChart3 className="text-blue-600" size={24} />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">市盈率历史</h2>
            <HelpTooltip 
              content="显示股票过去一年的市盈率变化趋势。市盈率反映了投资者对公司未来盈利的预期，较低的市盈率通常意味着更好的价值投资机会。"
              title="历史市盈率分析"
              size="sm"
            />
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <PERatioChart peHistory={stockInfo.pe_history} />
            <PERatioStats peHistory={stockInfo.pe_history} />
          </div>
        </div>
      )}
    </div>
  );
} 