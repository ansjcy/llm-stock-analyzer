'use client';

import React, { useMemo, useState } from 'react';
import {
  ComposedChart,
  LineChart,
  BarChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart,
  Cell
} from 'recharts';
import { TechnicalAnalysis } from '@/types/analysis';
import HelpTooltip from './HelpTooltip';

interface HistoricalDataPoint {
  date: string;
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma_20?: number;
  sma_50?: number;
  sma_200?: number;
  rsi?: number;
  macd_line?: number;
  macd_signal?: number;
  macd_histogram?: number;
  bb_upper?: number;
  bb_lower?: number;
  bb_middle?: number;
}

interface TechnicalChartsProps {
  technicalAnalysis: TechnicalAnalysis;
  historicalData?: HistoricalDataPoint[];
  ticker: string;
}

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-800 p-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
        <p className="text-sm font-medium text-gray-900 dark:text-white">{`Date: ${label}`}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {`${entry.name}: ${typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

// Generate mock historical data with technical indicators
const generateMockData = (technicalAnalysis: TechnicalAnalysis): HistoricalDataPoint[] => {
  const data: HistoricalDataPoint[] = [];
  const basePrice = 100;
  const days = 60; // 2 months of data
  
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i));
    
    // Generate realistic price movement
    const trend = Math.sin((i / days) * Math.PI * 2) * 0.1;
    const volatility = Math.random() * 0.05 - 0.025;
    const price = basePrice * (1 + trend + volatility) * (1 + i * 0.001);
    
    // Calculate moving averages
    const sma_20 = i >= 19 ? price * (0.98 + Math.random() * 0.04) : undefined;
    const sma_50 = i >= 49 ? price * (0.97 + Math.random() * 0.06) : undefined;
    const sma_200 = price * (0.95 + Math.random() * 0.1);
    
    // Calculate RSI (simplified)
    const rsi = technicalAnalysis.momentum?.rsi || (50 + Math.sin(i * 0.2) * 20 + Math.random() * 10);
    
    // Calculate MACD (simplified)
    const macd_line = Math.sin(i * 0.15) * 2 + Math.random() * 0.5;
    const macd_signal = macd_line * 0.8;
    const macd_histogram = macd_line - macd_signal;
    
    // Calculate Bollinger Bands - Fixed calculation
    const bb_middle = sma_20 || price;
    const volatilityFactor = 0.02 + Math.random() * 0.01; // More realistic volatility
    const bb_upper = bb_middle * (1 + volatilityFactor);
    const bb_lower = bb_middle * (1 - volatilityFactor);
    
    data.push({
      date: date.toISOString().split('T')[0],
      timestamp: date.getTime(),
      open: price * (0.99 + Math.random() * 0.02),
      high: price * (1.01 + Math.random() * 0.02),
      low: price * (0.98 + Math.random() * 0.02),
      close: price,
      volume: Math.floor(1000000 + Math.random() * 5000000),
      sma_20,
      sma_50,
      sma_200,
      rsi: Math.max(0, Math.min(100, rsi)),
      macd_line,
      macd_signal,
      macd_histogram,
      bb_upper,
      bb_lower,
      bb_middle
    });
  }
  
  return data;
};

// Custom legend component that shows toggle state
const CustomLegend = ({ visibility, onToggle }: { 
  visibility: {
    close: boolean;
    sma_20: boolean;
    sma_50: boolean;
    sma_200: boolean;
    bb_upper: boolean;
    bb_lower: boolean;
    bb_middle: boolean;
    support_resistance: boolean;
  }; 
  onToggle: (key: keyof typeof visibility) => void 
}) => {
  const legendItems = [
    { key: 'close' as const, name: '收盘价', color: '#3B82F6' },
    { key: 'sma_20' as const, name: 'SMA 20', color: '#10B981' },
    { key: 'sma_50' as const, name: 'SMA 50', color: '#F59E0B' },
    { key: 'sma_200' as const, name: 'SMA 200', color: '#DC2626' },
    { key: 'bb_upper' as const, name: '布林带上轨', color: '#9CA3AF' },
    { key: 'bb_lower' as const, name: '布林带下轨', color: '#9CA3AF' },
    { key: 'bb_middle' as const, name: '布林带中轨', color: '#9CA3AF' },
  ];

  return (
    <div className="flex flex-wrap gap-4 mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
      {legendItems.map(item => (
        <button
          key={item.key}
          onClick={() => onToggle(item.key)}
          className={`flex items-center gap-2 px-2 py-1 rounded transition-all ${
            visibility[item.key] 
              ? 'opacity-100 hover:bg-gray-200 dark:hover:bg-gray-700' 
              : 'opacity-50 hover:opacity-75'
          }`}
        >
          <div 
            className="w-3 h-3 rounded-sm border"
            style={{ 
              backgroundColor: visibility[item.key] ? item.color : 'transparent',
              borderColor: item.color,
              borderWidth: '1px'
            }}
          />
          <span className={`text-sm ${
            visibility[item.key] 
              ? 'text-gray-900 dark:text-white' 
              : 'text-gray-400 dark:text-gray-500 line-through'
          }`}>
            {item.name}
          </span>
        </button>
      ))}
    </div>
  );
};

export default function TechnicalCharts({ technicalAnalysis, historicalData, ticker }: TechnicalChartsProps) {
  const chartData = useMemo(() => {
    return historicalData && historicalData.length > 0 
      ? historicalData 
      : generateMockData(technicalAnalysis);
  }, [historicalData, technicalAnalysis]);

  // Zoom state management
  const [zoomState, setZoomState] = useState({
    startIndex: 0,
    endIndex: chartData.length - 1,
    refAreaLeft: '',
    refAreaRight: '',
    isZooming: false
  });

  // Visibility state for different chart elements
  const [visibility, setVisibility] = useState({
    close: true,
    sma_20: true,
    sma_50: true,
    sma_200: true,
    bb_upper: true,
    bb_lower: true,
    bb_middle: true,
    support_resistance: true
  });

  // Toggle visibility function
  const toggleVisibility = (key: keyof typeof visibility) => {
    setVisibility(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  // Get zoomed data - Always keep the rightmost (latest) data
  const zoomedData = chartData.slice(zoomState.startIndex, zoomState.endIndex + 1);

  // Zoom functions
  const zoomOut = () => {
    setZoomState(prev => ({
      ...prev,
      startIndex: 0,
      endIndex: chartData.length - 1
    }));
  };

  const zoomIn = () => {
    const currentRange = zoomState.endIndex - zoomState.startIndex + 1;
    const newRange = Math.max(10, Math.floor(currentRange * 0.7)); // Zoom in to 70% of current range
    // Always keep endIndex at the latest data point
    const newStartIndex = Math.max(0, chartData.length - newRange);
    const newEndIndex = chartData.length - 1;
    
    setZoomState(prev => ({
      ...prev,
      startIndex: newStartIndex,
      endIndex: newEndIndex
    }));
  };

  // Price Chart with Moving Averages and Bollinger Bands
  const PriceChart = () => {
    // Get support and resistance levels from technical analysis
    const supportResistance = technicalAnalysis.support_resistance as any || {};
    const resistance1 = supportResistance.resistance_1;
    const support1 = supportResistance.support_1;
    
    // Calculate price range for better Y-axis scaling using zoomed data
    const prices = zoomedData.map(d => d.close).filter(p => p !== null);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;
    const yAxisPadding = priceRange * 0.05; // 5% padding

    // Custom tooltip that includes support/resistance info
    const PriceTooltip = ({ active, payload, label }: any) => {
      if (active && payload && payload.length) {
        return (
          <div className="bg-white dark:bg-gray-800 p-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
            <p className="text-sm font-medium text-gray-900 dark:text-white">{`Date: ${label}`}</p>
            {payload.map((entry: any, index: number) => (
              <p key={index} className="text-sm" style={{ color: entry.color }}>
                {`${entry.name}: ${typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}`}
              </p>
            ))}
            {/* Support and Resistance info */}
            {(resistance1 || support1) && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">关键价位:</p>
                {resistance1 && (
                  <p className="text-xs" style={{ color: '#DC2626' }}>
                    阻力位: ${resistance1.toFixed(2)}
                  </p>
                )}
                {support1 && (
                  <p className="text-xs" style={{ color: '#16A34A' }}>
                    支撑位: ${support1.toFixed(2)}
                  </p>
                )}
              </div>
            )}
          </div>
        );
      }
      return null;
    };
    
    return (
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            价格走势与移动平均线
            <HelpTooltip 
              title="价格走势与移动平均线图表"
              content="**收盘价**：股票每日的收盘价格，反映当日交易结束时的股价

**移动平均线系统**：
- SMA 20：过去20天的平均价格，短期趋势指标
- SMA 50：过去50天的平均价格，中期趋势指标  
- SMA 200：过去200天的平均价格，长期趋势指标

**布林带系统**：
- 布林带上轨：布林带的上边界线，通常作为阻力位
- 布林带下轨：布林带的下边界线，通常作为支撑位
- 布林带中轨：布林带的中线，**与 SMA 20 完全相同**，会重叠显示

**关键价位**：
- 支撑位：股价下跌时可能遇到支撑的关键价格水平
- 阻力位：股价上涨时可能遇到阻力的关键价格水平

**注意**：布林带中轨 和 SMA 20 是相同的指标，同时显示时会完全重叠"
            />
          </h3>
          <div className="flex gap-2">
            <button
              onClick={zoomIn}
              disabled={zoomState.endIndex - zoomState.startIndex <= 10}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              🔍+ 放大
            </button>
            <button
              onClick={zoomOut}
              disabled={zoomState.startIndex === 0 && zoomState.endIndex === chartData.length - 1}
              className="px-3 py-1 text-sm bg-gray-500 text-white rounded hover:bg-gray-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              🔍- 缩小
            </button>
            <span className="text-sm text-gray-600 dark:text-gray-400 px-2 py-1">
              显示最近 {zoomState.endIndex - zoomState.startIndex + 1} 天数据
            </span>
          </div>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          💡 使用放大/缩小按钮来调整时间范围查看详细数据，点击图例可以显示/隐藏对应的线条
        </p>
        <CustomLegend visibility={visibility} onToggle={toggleVisibility} />
        
        {/* Support/Resistance Values Display */}
        {(resistance1 || support1) && (
          <div className="mb-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg flex gap-4 text-sm">
            {resistance1 && (
              <span className="font-medium" style={{ color: '#DC2626' }}>
                阻力位: ${resistance1.toFixed(2)}
              </span>
            )}
            {support1 && (
              <span className="font-medium" style={{ color: '#16A34A' }}>
                支撑位: ${support1.toFixed(2)}
              </span>
            )}
          </div>
        )}
        
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={zoomedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="date" 
                stroke="#6B7280"
                fontSize={12}
                tick={{ fill: '#6B7280' }}
                interval="preserveStartEnd"
              />
              <YAxis 
                stroke="#6B7280"
                fontSize={12}
                tick={{ fill: '#6B7280' }}
                domain={[minPrice - yAxisPadding, maxPrice + yAxisPadding]}
                tickFormatter={(value) => `$${value.toFixed(2)}`}
              />
              <Tooltip content={<PriceTooltip />} />
              
              {/* Support and Resistance Lines */}
              {visibility.support_resistance && resistance1 && (
                <ReferenceLine 
                  y={resistance1} 
                  stroke="#DC2626" 
                  strokeWidth={2}
                  strokeDasharray="5 5" 
                  label={{ 
                    value: `阻力位 $${resistance1.toFixed(2)}`, 
                    position: "right",
                    style: { fill: '#DC2626', fontWeight: 'bold', fontSize: '12px' }
                  }}
                />
              )}
              {visibility.support_resistance && support1 && (
                <ReferenceLine 
                  y={support1} 
                  stroke="#16A34A" 
                  strokeWidth={2}
                  strokeDasharray="5 5" 
                  label={{ 
                    value: `支撑位 $${support1.toFixed(2)}`, 
                    position: "right",
                    style: { fill: '#16A34A', fontWeight: 'bold', fontSize: '12px' }
                  }}
                />
              )}
              
              {/* Moving Averages - Better colors and spacing */}
              {visibility.sma_200 && zoomedData.some(d => d.sma_200) && (
                <Line
                  type="monotone"
                  dataKey="sma_200"
                  stroke="#DC2626"
                  strokeWidth={1.5}
                  dot={false}
                  name="SMA 200"
                  strokeOpacity={0.8}
                />
              )}
              {visibility.sma_50 && zoomedData.some(d => d.sma_50) && (
                <Line
                  type="monotone"
                  dataKey="sma_50"
                  stroke="#F59E0B"
                  strokeWidth={1.5}
                  dot={false}
                  name="SMA 50"
                  strokeOpacity={0.8}
                />
              )}
              {visibility.sma_20 && zoomedData.some(d => d.sma_20) && (
                <Line
                  type="monotone"
                  dataKey="sma_20"
                  stroke="#10B981"
                  strokeWidth={1.5}
                  dot={false}
                  name="SMA 20"
                  strokeOpacity={0.8}
                />
              )}
              
              {/* Price Line - Most prominent */}
              {visibility.close && (
                <Line
                  type="monotone"
                  dataKey="close"
                  stroke="#3B82F6"
                  strokeWidth={2.5}
                  dot={false}
                  name="收盘价"
                />
              )}
              
              {/* Bollinger Band Lines */}
              {visibility.bb_upper && zoomedData.some(d => d.bb_upper) && (
                <Line
                  type="monotone"
                  dataKey="bb_upper"
                  stroke="#9CA3AF"
                  strokeWidth={1}
                  strokeDasharray="2 2"
                  dot={false}
                  name="布林带上轨"
                  strokeOpacity={0.6}
                />
              )}
              {visibility.bb_lower && zoomedData.some(d => d.bb_lower) && (
                <Line
                  type="monotone"
                  dataKey="bb_lower"
                  stroke="#9CA3AF"
                  strokeWidth={1}
                  strokeDasharray="2 2"
                  dot={false}
                  name="布林带下轨"
                  strokeOpacity={0.6}
                />
              )}
              {visibility.bb_middle && zoomedData.some(d => d.bb_middle) && (
                <Line
                  type="monotone"
                  dataKey="bb_middle"
                  stroke="#9CA3AF"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  dot={false}
                  name="布林带中轨"
                  strokeOpacity={0.8}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  // RSI Chart
  const RSIChart = () => (
    <div className="mb-8">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        相对强弱指数 (RSI)
        <HelpTooltip 
          title="相对强弱指数 (RSI)"
          content="**RSI 指标**：相对强弱指数，范围0-100，用于判断股票的超买或超卖状态

**关键区域**：
- **RSI > 70**：通常表示超买状态，股价可能面临回调压力
- **RSI < 30**：通常表示超卖状态，股价可能面临反弹机会  
- **RSI = 50**：表示中性状态，多空力量相对平衡

**技术分析**：
- **RSI背离**：价格与RSI走势相反，可能预示趋势反转
- **强势趋势**：RSI可能在超买或超卖状态保持较长时间

**使用建议**：结合其他指标使用，避免单独依赖RSI做交易决策"
        />
      </h3>
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
            <XAxis 
              dataKey="date" 
              stroke="#6B7280"
              fontSize={12}
              tick={{ fill: '#6B7280' }}
              interval="preserveStartEnd"
            />
            <YAxis 
              stroke="#6B7280"
              fontSize={12}
              tick={{ fill: '#6B7280' }}
              domain={[0, 100]}
              tickFormatter={(value) => `${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Overbought/Oversold zones */}
            <ReferenceLine y={70} stroke="#DC2626" strokeDasharray="5 5" label="超买 (70)" />
            <ReferenceLine y={30} stroke="#16A34A" strokeDasharray="5 5" label="超卖 (30)" />
            <ReferenceLine y={50} stroke="#6B7280" strokeDasharray="2 2" />
            
            {/* RSI Line */}
            <Line
              type="monotone"
              dataKey="rsi"
              stroke="#8B5CF6"
              strokeWidth={2}
              dot={false}
              name="RSI"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  // MACD Chart
  const MACDChart = () => (
    <div className="mb-8">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        MACD (移动平均收敛散度)
        <HelpTooltip 
          title="MACD (移动平均收敛散度)"
          content="**MACD 组成**：
- **MACD线**：快速EMA与慢速EMA的差值，反映短期与长期趋势关系
- **信号线**：MACD线的移动平均，用于产生买卖信号
- **MACD 柱状图**：MACD线与信号线的差值，显示两线收敛散度

**交易信号**：
- **黄金交叉**：MACD线向上穿越信号线，可能是买入信号
- **死亡交叉**：MACD线向下穿越信号线，可能是卖出信号
- **零轴穿越**：MACD线穿越零轴，表示趋势可能发生变化

**高级分析**：
- **背离现象**：价格与MACD走势相反，可能预示趋势反转
- **柱状图变化**：柱状图缩短可能预示趋势放缓"
        />
      </h3>
      <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
        <ResponsiveContainer width="100%" height={250}>
          <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
            <XAxis 
              dataKey="date" 
              stroke="#6B7280"
              fontSize={12}
              tick={{ fill: '#6B7280' }}
              interval="preserveStartEnd"
            />
            <YAxis 
              stroke="#6B7280"
              fontSize={12}
              tick={{ fill: '#6B7280' }}
              tickFormatter={(value) => `${value.toFixed(3)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            
            {/* Zero line */}
            <ReferenceLine y={0} stroke="#6B7280" />
            
            {/* MACD Histogram */}
            <Bar
              dataKey="macd_histogram"
              fill="#9CA3AF"
              opacity={0.6}
              name="MACD 柱状图"
            />
            
            {/* MACD Lines */}
            <Line
              type="monotone"
              dataKey="macd_line"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={false}
              name="MACD 线"
            />
            <Line
              type="monotone"
              dataKey="macd_signal"
              stroke="#DC2626"
              strokeWidth={2}
              dot={false}
              name="信号线"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  // Volume Chart with color-coded bars - Fixed implementation
  const VolumeChart = () => {
    // Calculate if each day is up or down using zoomed data
    const volumeData = zoomedData.map((item, index) => {
      const prevClose = index > 0 ? zoomedData[index - 1].close : item.close;
      const isUp = item.close >= prevClose;
      return {
        ...item,
        isUp,
        barColor: isUp ? '#10B981' : '#EF4444'
      };
    });

    return (
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          成交量分析
          <HelpTooltip 
            title="成交量分析图表"
            content="**成交量指标**：每日股票交易的股数，反映市场活跃度和交易兴趣

**颜色含义**：
- **绿色柱状图**：当日股价上涨时的成交量，表明买方力量较强
- **红色柱状图**：当日股价下跌时的成交量，表明卖方力量较强

**分析要点**：
- **高成交量**：通常伴随重要的价格变动，增加趋势的可信度
- **低成交量**：可能表明市场观望情绪或趋势力量减弱
- **量价配合**：上涨伴随放量，下跌伴随缩量，趋势更可靠

**交易参考**：
- **突破确认**：重要阻力/支撑位突破需要成交量配合
- **趋势衰竭**：价格新高但成交量萎缩可能预示趋势结束"
          />
        </h3>
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={volumeData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
              <XAxis 
                dataKey="date" 
                stroke="#6B7280"
                fontSize={12}
                tick={{ fill: '#6B7280' }}
                interval="preserveStartEnd"
              />
              <YAxis 
                stroke="#6B7280"
                fontSize={12}
                tick={{ fill: '#6B7280' }}
                tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
              />
              <Tooltip 
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    
                    return (
                      <div className="bg-white dark:bg-gray-800 p-3 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{`日期: ${label}`}</p>
                        <p className="text-sm" style={{ color: data.isUp ? '#10B981' : '#EF4444' }}>
                          {`成交量: ${(data.volume / 1000000).toFixed(1)}M`}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {`收盘价: $${data.close?.toFixed(2)}`}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {data.isUp ? '上涨日' : '下跌日'}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              
              {/* Volume bars with conditional colors */}
              <Bar dataKey="volume" name="成交量">
                {volumeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.barColor} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4 mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          {ticker} - 技术分析图表
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          交互式技术分析图表，包含价格走势、技术指标和成交量分析
        </p>
      </div>
      
      <PriceChart />
      <VolumeChart />
      <RSIChart />
      <MACDChart />
    </div>
  );
}