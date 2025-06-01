import { TechnicalAnalysis as TechnicalAnalysisType, Charts } from '@/types/analysis';
import { TrendingUp, TrendingDown, Activity, Target, Gauge, BarChart3 } from 'lucide-react';
import HelpTooltip from './HelpTooltip';
import TechnicalCharts from './TechnicalCharts';

interface TechnicalAnalysisProps {
  technicalAnalysis: TechnicalAnalysisType;
  charts?: Charts;
  ticker: string;
  historicalData?: any[];
}

export default function TechnicalAnalysis({ technicalAnalysis, charts, ticker, historicalData }: TechnicalAnalysisProps) {
  const getSignalColor = (signal: string | undefined | null) => {
    if (!signal || typeof signal !== 'string') return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300';
    if (signal === 'bullish' || signal === 'buy') return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300';
    if (signal === 'bearish' || signal === 'sell') return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300';
    return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300';
  };

  const getSignalIcon = (signal: string | undefined | null) => {
    if (!signal || typeof signal !== 'string') return <Activity size={16} />;
    if (signal === 'bullish' || signal === 'buy') return <TrendingUp size={16} />;
    if (signal === 'bearish' || signal === 'sell') return <TrendingDown size={16} />;
    return <Activity size={16} />;
  };

  const formatSignalText = (signal: string | undefined | null) => {
    if (!signal || typeof signal !== 'string') return 'Unknown';
    return signal.charAt(0).toUpperCase() + signal.slice(1);
  };

  const ConfidenceBar = ({ confidence }: { confidence: number }) => (
    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
      <div 
        className={`h-3 rounded-full transition-all duration-500 ${
          confidence >= 70 ? 'bg-green-500' : 
          confidence >= 50 ? 'bg-yellow-500' : 'bg-red-500'
        }`}
        style={{ width: `${confidence}%` }}
      />
    </div>
  );

  // RSI Chart Component
  const RSIChart = ({ rsi }: { rsi: number }) => {
    const rsiPosition = (rsi / 100) * 100; // RSI is already 0-100
    
    return (
      <div className="w-full">
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
          <span>0</span>
          <span>30</span>
          <span className="font-medium">{rsi.toFixed(1)}</span>
          <span>70</span>
          <span>100</span>
        </div>
        <div className="relative h-6 bg-gray-200 dark:bg-gray-600 rounded-full">
          {/* Oversold zone (0-30) */}
          <div className="absolute left-0 top-0 bottom-0 bg-green-300 rounded-l-full" style={{ width: '30%' }}></div>
          
          {/* Neutral zone (30-70) */}
          <div className="absolute top-0 bottom-0 bg-blue-300" style={{ left: '30%', width: '40%' }}></div>
          
          {/* Overbought zone (70-100) */}
          <div className="absolute right-0 top-0 bottom-0 bg-red-300 rounded-r-full" style={{ width: '30%' }}></div>
          
          {/* Zone markers */}
          <div className="absolute top-0 bottom-0 w-0.5 bg-green-600" style={{ left: '30%' }}></div>
          <div className="absolute top-0 bottom-0 w-0.5 bg-red-600" style={{ left: '70%' }}></div>
          
          {/* Current RSI marker */}
          <div 
            className="absolute top-0 bottom-0 w-2 bg-gray-800 dark:bg-white rounded-full transform -translate-x-1/2 shadow-lg z-10"
            style={{ left: `${rsiPosition}%` }}
          >
            <div className="absolute -top-1 -bottom-1 left-1/2 transform -translate-x-1/2 w-1 bg-gray-900 dark:bg-gray-100 rounded-full"></div>
          </div>
        </div>
        <div className="text-center mt-1">
          <span className="text-xs text-gray-600 dark:text-gray-400">
            {rsi < 30 ? 'Oversold' : rsi > 70 ? 'Overbought' : 'Neutral'}
          </span>
        </div>
      </div>
    );
  };

  // Stochastic Chart Component
  const StochasticChart = ({ stochK }: { stochK: number }) => {
    const stochPosition = (stochK / 100) * 100; // Stochastic is already 0-100
    
    return (
      <div className="w-full">
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
          <span>0</span>
          <span>20</span>
          <span className="font-medium">{stochK.toFixed(1)}</span>
          <span>80</span>
          <span>100</span>
        </div>
        <div className="relative h-6 bg-gray-200 dark:bg-gray-600 rounded-full">
          {/* Oversold zone (0-20) */}
          <div className="absolute left-0 top-0 bottom-0 bg-green-300 rounded-l-full" style={{ width: '20%' }}></div>
          
          {/* Neutral zone (20-80) */}
          <div className="absolute top-0 bottom-0 bg-blue-300" style={{ left: '20%', width: '60%' }}></div>
          
          {/* Overbought zone (80-100) */}
          <div className="absolute right-0 top-0 bottom-0 bg-red-300 rounded-r-full" style={{ width: '20%' }}></div>
          
          {/* Zone markers */}
          <div className="absolute top-0 bottom-0 w-0.5 bg-green-600" style={{ left: '20%' }}></div>
          <div className="absolute top-0 bottom-0 w-0.5 bg-red-600" style={{ left: '80%' }}></div>
          
          {/* Current Stochastic marker */}
          <div 
            className="absolute top-0 bottom-0 w-2 bg-gray-800 dark:bg-white rounded-full transform -translate-x-1/2 shadow-lg z-10"
            style={{ left: `${stochPosition}%` }}
          >
            <div className="absolute -top-1 -bottom-1 left-1/2 transform -translate-x-1/2 w-1 bg-gray-900 dark:bg-gray-100 rounded-full"></div>
          </div>
        </div>
        <div className="text-center mt-1">
          <span className="text-xs text-gray-600 dark:text-gray-400">
            {stochK < 20 ? 'Oversold' : stochK > 80 ? 'Overbought' : 'Neutral'}
          </span>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border border-gray-200 dark:border-gray-700">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
        <Target className="mr-2 text-blue-600" />
        技术分析
        <HelpTooltip 
          content="技术分析研究价格模式、趋势和交易量来预测未来价格走势。它使用数学指标和图表模式基于历史市场数据识别买卖机会。"
          title="什么是技术分析？"
          size="md"
          className="ml-2"
        />
      </h2>

      {/* Interactive Technical Analysis Charts */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <BarChart3 className="text-blue-600" size={20} />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">交互式技术分析图表</h3>
          <HelpTooltip 
            content="交互式技术分析图表显示股票价格走势、技术指标和交易量。包括移动平均线、RSI、MACD等关键指标的可视化展示，帮助识别趋势和交易机会。图表支持缩放和悬停查看详细数据。"
            title="交互式技术分析图表"
            size="sm"
          />
        </div>
        <TechnicalCharts 
          technicalAnalysis={technicalAnalysis}
          historicalData={historicalData}
          ticker={ticker}
        />
      </div>

      {/* Overall Signal */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-6 mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">总体信号</h3>
          <HelpTooltip 
            content="总体信号结合多个技术指标提供单一建议。看涨意味着买入/正面展望，看跌意味着卖出/负面展望，中性意味着持有/等待更清晰的信号。"
            title="总体技术信号"
            size="sm"
          />
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`px-4 py-2 rounded-full font-bold flex items-center space-x-2 ${getSignalColor(technicalAnalysis.overall_signal)}`}>
              {getSignalIcon(technicalAnalysis.overall_signal)}
              <span>{formatSignalText(technicalAnalysis.overall_signal)}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">信心度</div>
              <HelpTooltip 
                content="信心度表示总体信号的可靠性。较高的百分比意味着不同技术指标之间有更强的一致性。70%+被认为是高信心度，50-70%中等，低于50%低信心度。"
                title="信号信心度"
                size="sm"
              />
            </div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {typeof technicalAnalysis.confidence === 'number' ? technicalAnalysis.confidence.toFixed(1) : 'N/A'}%
            </div>
            <div className="w-32 mt-2">
              <ConfidenceBar confidence={technicalAnalysis.confidence || 0} />
            </div>
          </div>
        </div>
      </div>

      {/* Strategic Combinations */}
      {technicalAnalysis.strategic_combinations && (
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">策略信号组合</h3>
            <HelpTooltip 
              content="这些策略结合多个技术指标，比单个指标提供更可靠的信号。每个策略都有自己的优势，专注于市场行为的不同方面。"
              title="组合策略信号"
              size="sm"
            />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {technicalAnalysis.strategic_combinations.rsi_macd_strategy && (
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="text-sm font-medium text-gray-600 dark:text-gray-300">RSI + MACD策略</div>
                  <HelpTooltip 
                    content="结合RSI（动量指标）和MACD（趋势指标）。RSI识别超买/超卖情况，而MACD显示趋势方向和动量变化。两者结合提供更强的买卖信号。"
                    title="RSI + MACD策略"
                    size="sm"
                  />
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-bold inline-flex items-center space-x-1 ${getSignalColor(technicalAnalysis.strategic_combinations.rsi_macd_strategy.signal)}`}>
                  {getSignalIcon(technicalAnalysis.strategic_combinations.rsi_macd_strategy.signal)}
                  <span>{formatSignalText(technicalAnalysis.strategic_combinations.rsi_macd_strategy.signal)}</span>
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white mt-2">
                  得分: {(() => {
                    const strategy = technicalAnalysis.strategic_combinations.rsi_macd_strategy;
                    if (typeof strategy.score === 'number') {
                      return strategy.score.toFixed(1);
                    } else if (typeof strategy.confidence === 'number') {
                      return (strategy.confidence / 10).toFixed(1);
                    }
                    return 'N/A';
                  })()}
                </div>
              </div>
            )}

            {technicalAnalysis.strategic_combinations.bollinger_rsi_macd_strategy && (
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="text-sm font-medium text-gray-600 dark:text-gray-300">布林带 + RSI + MACD</div>
                  <HelpTooltip 
                    content="高级策略结合布林带（波动性）、RSI（动量）和MACD（趋势）。布林带识别价格极值，使这成为进出场时机的综合策略。"
                    title="三重指标策略"
                    size="sm"
                  />
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-bold inline-flex items-center space-x-1 ${getSignalColor(technicalAnalysis.strategic_combinations.bollinger_rsi_macd_strategy.signal)}`}>
                  {getSignalIcon(technicalAnalysis.strategic_combinations.bollinger_rsi_macd_strategy.signal)}
                  <span>{formatSignalText(technicalAnalysis.strategic_combinations.bollinger_rsi_macd_strategy.signal)}</span>
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white mt-2">
                  得分: {(() => {
                    const strategy = technicalAnalysis.strategic_combinations.bollinger_rsi_macd_strategy;
                    if (typeof strategy.score === 'number') {
                      return strategy.score.toFixed(1);
                    } else if (typeof strategy.confidence === 'number') {
                      return (strategy.confidence / 10).toFixed(1);
                    }
                    return 'N/A';
                  })()}
                </div>
              </div>
            )}

            {technicalAnalysis.strategic_combinations.ma_rsi_volume_strategy && (
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="text-sm font-medium text-gray-600 dark:text-gray-300">均线 + RSI + 成交量</div>
                  <HelpTooltip 
                    content="结合移动均线（趋势方向）、RSI（动量）和成交量（确认）。成交量确认至关重要，因为它验证价格走势是否有真正的市场支持。"
                    title="趋势 + 动量 + 成交量策略"
                    size="sm"
                  />
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-bold inline-flex items-center space-x-1 ${getSignalColor(technicalAnalysis.strategic_combinations.ma_rsi_volume_strategy.signal)}`}>
                  {getSignalIcon(technicalAnalysis.strategic_combinations.ma_rsi_volume_strategy.signal)}
                  <span>{formatSignalText(technicalAnalysis.strategic_combinations.ma_rsi_volume_strategy.signal)}</span>
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white mt-2">
                  得分: {(() => {
                    const strategy = technicalAnalysis.strategic_combinations.ma_rsi_volume_strategy;
                    if (typeof strategy.score === 'number') {
                      return strategy.score.toFixed(1);
                    } else if (typeof strategy.confidence === 'number') {
                      return (strategy.confidence / 10).toFixed(1);
                    }
                    return 'N/A';
                  })()}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Key Indicators */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Momentum Indicators */}
        {technicalAnalysis.momentum && (
          <div className="bg-white dark:bg-gray-800 border border-purple-200 dark:border-purple-700 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-4">
              <Gauge className="text-purple-600" size={20} />
              <h4 className="text-md font-semibold text-gray-900 dark:text-white">动量指标</h4>
              <HelpTooltip 
                content="动量指标衡量价格走势的速度和强度。它们帮助识别股票何时获得或失去动量，并可以信号潜在的反转或趋势延续。"
                title="动量指标"
                size="sm"
              />
            </div>
            
            {technicalAnalysis.momentum.rsi && (
              <div className="mb-4">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">RSI</span>
                  <HelpTooltip 
                    content="相对强弱指数（RSI）在0-100的范围内衡量动量。RSI > 70表示超买状态（潜在卖出信号），RSI < 30表示超卖状态（潜在买入信号）。30-70之间的值被认为是中性的。"
                    title="RSI - 相对强弱指数"
                    size="sm"
                  />
                </div>
                <div className="space-y-2">
                  <RSIChart rsi={technicalAnalysis.momentum.rsi} />
                  <div className="flex items-center justify-between">
                    <div className="text-lg font-bold text-gray-900 dark:text-white">
                      {typeof technicalAnalysis.momentum.rsi === 'number' ? technicalAnalysis.momentum.rsi.toFixed(1) : 'N/A'}
                    </div>
                    {technicalAnalysis.momentum.rsi_signal && (
                      <div className={`text-xs px-2 py-1 rounded-full ${getSignalColor(technicalAnalysis.momentum.rsi_signal)}`}>
                        {formatSignalText(technicalAnalysis.momentum.rsi_signal)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {technicalAnalysis.momentum.stoch_k && (
              <div className="mb-2">
                <div className="flex items-center space-x-2 mb-3">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">随机指标 %K</span>
                  <HelpTooltip 
                    content="随机指标%K将当前收盘价与特定期间的价格范围进行比较。与RSI类似，高于80的值表示超买状态，而低于20的值表示超卖状态。"
                    title="随机指标%K振荡器"
                    size="sm"
                  />
                </div>
                <div className="space-y-2">
                  <StochasticChart stochK={technicalAnalysis.momentum.stoch_k} />
                  <div className="flex items-center justify-between">
                    <div className="text-lg font-bold text-gray-900 dark:text-white">
                      {typeof technicalAnalysis.momentum.stoch_k === 'number' ? technicalAnalysis.momentum.stoch_k.toFixed(1) : 'N/A'}
                    </div>
                    {technicalAnalysis.momentum.stoch_signal && (
                      <div className={`text-xs px-2 py-1 rounded-full ${getSignalColor(technicalAnalysis.momentum.stoch_signal)}`}>
                        {formatSignalText(technicalAnalysis.momentum.stoch_signal)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Trend Indicators */}
        {technicalAnalysis.trend && (
          <div className="bg-white dark:bg-gray-800 border border-green-200 dark:border-green-700 rounded-lg p-4">
            <h4 className="text-md font-semibold mb-4 flex items-center text-gray-900 dark:text-white">
              <TrendingUp className="mr-2 text-green-600" size={20} />
              Trend Indicators
            </h4>
            
            {technicalAnalysis.trend.macd_signal && (
              <div className="mb-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">MACD Signal</span>
                  <div className={`px-3 py-1 rounded-full text-sm font-bold ${getSignalColor(technicalAnalysis.trend.macd_signal)}`}>
                    {formatSignalText(technicalAnalysis.trend.macd_signal)}
                  </div>
                </div>
              </div>
            )}

            {technicalAnalysis.trend.macd_histogram && (
              <div className="mb-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">MACD Histogram</span>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {typeof technicalAnalysis.trend.macd_histogram === 'number' ? 
                      technicalAnalysis.trend.macd_histogram.toFixed(4) : 'N/A'}
                  </div>
                </div>
              </div>
            )}

            {technicalAnalysis.moving_averages?.sma_trend && (
              <div className="mb-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">SMA Trend</span>
                  <div className={`px-3 py-1 rounded-full text-sm font-bold ${getSignalColor(technicalAnalysis.moving_averages.sma_trend)}`}>
                    {formatSignalText(technicalAnalysis.moving_averages.sma_trend)}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Price vs Moving Averages */}
      {technicalAnalysis.moving_averages && (
        <div className="mt-6 bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <h4 className="text-md font-semibold mb-4 text-gray-900 dark:text-white">Price vs Moving Averages</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {typeof technicalAnalysis.moving_averages.price_vs_sma_20 === 'number' && (
              <div className="text-center">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">vs SMA 20</div>
                <div className={`text-lg font-bold ${technicalAnalysis.moving_averages.price_vs_sma_20 >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {technicalAnalysis.moving_averages.price_vs_sma_20 >= 0 ? '+' : ''}{technicalAnalysis.moving_averages.price_vs_sma_20.toFixed(2)}%
                </div>
              </div>
            )}
            {typeof technicalAnalysis.moving_averages.price_vs_sma_50 === 'number' && (
              <div className="text-center">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">vs SMA 50</div>
                <div className={`text-lg font-bold ${technicalAnalysis.moving_averages.price_vs_sma_50 >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {technicalAnalysis.moving_averages.price_vs_sma_50 >= 0 ? '+' : ''}{technicalAnalysis.moving_averages.price_vs_sma_50.toFixed(2)}%
                </div>
              </div>
            )}
            {typeof technicalAnalysis.moving_averages.price_vs_sma_200 === 'number' && (
              <div className="text-center">
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">vs SMA 200</div>
                <div className={`text-lg font-bold ${technicalAnalysis.moving_averages.price_vs_sma_200 >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                  {technicalAnalysis.moving_averages.price_vs_sma_200 >= 0 ? '+' : ''}{technicalAnalysis.moving_averages.price_vs_sma_200.toFixed(2)}%
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 