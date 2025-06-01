import React from 'react';
import { PeterLynchAnalysis } from '@/types/analysis';
import { TrendingUp, TrendingDown, Activity, DollarSign, Target, CheckCircle, BarChart3, Zap, Building } from 'lucide-react';
import HelpTooltip from './HelpTooltip';
import ReactMarkdown from 'react-markdown';

interface PeterLynchAnalysisProps {
  peterLynchAnalysis: PeterLynchAnalysis;
  llmInsights?: string;
}

export default function PeterLynchAnalysisComponent({ peterLynchAnalysis, llmInsights }: PeterLynchAnalysisProps) {
  // Always use Chinese content by default
  const isChineseContent = true;

  // Translation function
  const t = (key: string) => {
    if (!isChineseContent) return translations.en[key] || key;
    return translations.zh[key] || key;
  };

  const translations: {
    zh: { [key: string]: string };
    en: { [key: string]: string };
  } = {
    zh: {
      // Main headers
      'peter_lynch_analysis': '彼得·林奇成长分析',
      'investment_signal': '投资信号',
      'overall_score': '综合评分',
      'confidence_level': '置信度',
      
      // GARP Analysis
      'garp_analysis': 'GARP分析（合理价格成长）',
      'garp_help': 'GARP（Growth at Reasonable Price）是彼得·林奇的核心投资理念，寻找以合理价格交易的成长股。重点关注PEG比率、市盈率与增长率的关系。',
      'peg_ratio': 'PEG比率',
      'pe_ratio': 'P/E比率',
      'earnings_growth': '盈利增长率',
      'revenue_growth': '营收增长率',
      
      // Growth Analysis
      'growth_analysis': '成长一致性分析',
      'growth_help': '林奇重视持续且可预测的增长。评估公司营收和盈利增长的稳定性、趋势和质量。',
      'growth_consistency': '增长一致性',
      'growth_trend': '增长趋势',
      
      // Business Quality
      'business_quality': '企业质量分析',
      'business_help': '林奇偏好简单易懂的业务模式，具有强劲的财务指标如ROE、适度的债务水平和正现金流。',
      'return_on_equity': '净资产收益率',
      'debt_to_equity': '债务股权比',
      'current_ratio': '流动比率',
      'free_cash_flow': '自由现金流',
      
      // Market Position
      'market_position': '市场定位分析',
      'market_help': '林奇偏好中等规模公司，有足够的增长空间但不会太小而风险过高。评估市值、行业地位和增长潜力。',
      'market_cap': '市值',
      'growth_potential': '增长潜力',
      
      // Lynch Principles
      'lynch_principles': '林奇投资原则',
      'principles_help': '基于彼得·林奇四大核心投资原则的评估：GARP原则、持续增长、企业质量和市场定位。',
      'principles_met': '符合原则',
      'total_principles': '总原则数',
      'adherence_percentage': '符合度',
      
      // Principle names
      'garp_principle': 'GARP原则',
      'consistent_growth': '持续增长',
      'business_quality_principle': '企业质量',
      'market_position_principle': '市场定位',
      
      // Investment reasoning
      'investment_reasoning': '投资推理',
      'llm_insights_title': 'AI深度洞察',
      
      // Signals
      'bullish': '看涨',
      'bearish': '看跌',
      'neutral': '中性',
      'buy': '买入',
      'sell': '卖出',
      'hold': '持有',
      
      // Scores
      'excellent': '优秀',
      'good': '良好',
      'fair': '一般',
      'poor': '较差',
      'score_out_of': '评分'
    },
    en: {
      // Main headers
      'peter_lynch_analysis': 'Peter Lynch Growth Analysis',
      'investment_signal': 'Investment Signal',
      'overall_score': 'Overall Score',
      'confidence_level': 'Confidence Level',
      
      // GARP Analysis
      'garp_analysis': 'GARP Analysis (Growth at Reasonable Price)',
      'garp_help': 'GARP (Growth at Reasonable Price) is Peter Lynch\'s core investment philosophy, seeking growth stocks trading at reasonable prices. Focus on PEG ratio and relationship between P/E and growth rates.',
      'peg_ratio': 'PEG Ratio',
      'pe_ratio': 'P/E Ratio',
      'earnings_growth': 'Earnings Growth',
      'revenue_growth': 'Revenue Growth',
      
      // Growth Analysis
      'growth_analysis': 'Growth Consistency Analysis',
      'growth_help': 'Lynch valued consistent and predictable growth. Evaluates the stability, trends, and quality of revenue and earnings growth.',
      'growth_consistency': 'Growth Consistency',
      'growth_trend': 'Growth Trend',
      
      // Business Quality
      'business_quality': 'Business Quality Analysis',
      'business_help': 'Lynch preferred simple, understandable business models with strong financial metrics like ROE, moderate debt levels, and positive cash flow.',
      'return_on_equity': 'Return on Equity',
      'debt_to_equity': 'Debt to Equity',
      'current_ratio': 'Current Ratio',
      'free_cash_flow': 'Free Cash Flow',
      
      // Market Position
      'market_position': 'Market Position Analysis',
      'market_help': 'Lynch preferred mid-sized companies with room to grow but not too small to be overly risky. Evaluates market cap, industry position, and growth potential.',
      'market_cap': 'Market Cap',
      'growth_potential': 'Growth Potential',
      
      // Lynch Principles
      'lynch_principles': 'Lynch Investment Principles',
      'principles_help': 'Assessment based on Peter Lynch\'s four core investment principles: GARP principle, consistent growth, business quality, and market position.',
      'principles_met': 'Principles Met',
      'total_principles': 'Total Principles',
      'adherence_percentage': 'Adherence',
      
      // Principle names
      'garp_principle': 'GARP Principle',
      'consistent_growth': 'Consistent Growth',
      'business_quality_principle': 'Business Quality',
      'market_position_principle': 'Market Position',
      
      // Investment reasoning
      'investment_reasoning': 'Investment Reasoning',
      'llm_insights_title': 'AI Deep Insights',
      
      // Signals
      'bullish': 'Bullish',
      'bearish': 'Bearish',
      'neutral': 'Neutral',
      'buy': 'Buy',
      'sell': 'Sell',
      'hold': 'Hold',
      
      // Scores
      'excellent': 'Excellent',
      'good': 'Good',
      'fair': 'Fair',
      'poor': 'Poor',
      'score_out_of': 'Score'
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal?.toLowerCase()) {
      case 'bullish':
      case 'buy':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'bearish':
      case 'sell':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'neutral':
      case 'hold':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal?.toLowerCase()) {
      case 'bullish':
      case 'buy':
        return <TrendingUp className="w-5 h-5" />;
      case 'bearish':
      case 'sell':
        return <TrendingDown className="w-5 h-5" />;
      case 'neutral':
      case 'hold':
        return <Activity className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-blue-600';
    if (percentage >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatSignalText = (signal: string) => {
    const signalMap: { [key: string]: string } = {
      'bullish': t('bullish'),
      'bearish': t('bearish'),
      'neutral': t('neutral'),
      'buy': t('buy'),
      'sell': t('sell'),
      'hold': t('hold')
    };
    return signalMap[signal?.toLowerCase()] || signal;
  };

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A';
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
    return `$${value.toFixed(0)}`;
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatRatio = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A';
    return value.toFixed(2);
  };

  const ScoreCard = ({ 
    title, 
    score, 
    maxScore, 
    percentage, 
    details, 
    icon,
    helpText 
  }: { 
    title: string; 
    score: number; 
    maxScore: number; 
    percentage: number; 
    details: string[]; 
    icon: React.ReactNode;
    helpText?: string;
  }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-50 rounded-lg">
            {icon}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
            {helpText && <HelpTooltip content={helpText} />}
          </div>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${getScoreColor(percentage)}`}>
            {score}/{maxScore}
          </div>
          <div className={`text-sm font-medium ${getScoreColor(percentage)}`}>
            {percentage.toFixed(1)}%
          </div>
        </div>
      </div>
      
      <div className="space-y-2">
        {details.map((detail, index) => (
          <div key={index} className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
            <span className="text-sm text-gray-600 dark:text-gray-300">{detail}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const LynchPrincipleCard = ({ 
    title, 
    score, 
    description, 
    meetsCriteria,
    icon 
  }: { 
    title: string; 
    score: number; 
    description: string; 
    meetsCriteria: boolean;
    icon: React.ReactNode;
  }) => (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={`p-2 rounded-lg ${meetsCriteria ? 'bg-green-100 dark:bg-green-800' : 'bg-red-100 dark:bg-red-800'}`}>
            {icon}
          </div>
          <h4 className="font-medium text-gray-900 dark:text-white">{title}</h4>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-lg font-bold ${meetsCriteria ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
            {score.toFixed(1)}
          </span>
          {meetsCriteria ? (
            <CheckCircle className="w-5 h-5 text-green-500" />
          ) : (
            <div className="w-5 h-5 rounded-full border-2 border-red-300"></div>
          )}
        </div>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <BarChart3 className="w-8 h-8" />
          <h2 className="text-2xl font-bold">{t('peter_lynch_analysis')}</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              {getSignalIcon(peterLynchAnalysis.overall_signal)}
              <span className="font-medium">{t('investment_signal')}</span>
            </div>
            <div className="text-xl font-bold">
              {formatSignalText(peterLynchAnalysis.overall_signal)}
            </div>
          </div>
          
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Target className="w-5 h-5" />
              <span className="font-medium">{t('overall_score')}</span>
            </div>
            <div className="text-xl font-bold">
              {peterLynchAnalysis.score_percentage.toFixed(1)}%
            </div>
          </div>
          
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Activity className="w-5 h-5" />
              <span className="font-medium">{t('confidence_level')}</span>
            </div>
            <div className="text-xl font-bold">
              {peterLynchAnalysis.confidence.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* GARP Analysis */}
        <ScoreCard
          title={t('garp_analysis')}
          score={peterLynchAnalysis.garp_analysis.score}
          maxScore={peterLynchAnalysis.garp_analysis.max_score}
          percentage={peterLynchAnalysis.garp_analysis.score_percentage}
          details={peterLynchAnalysis.garp_analysis.details}
          icon={<DollarSign className="w-5 h-5 text-blue-600" />}
          helpText={t('garp_help')}
        />

        {/* Growth Analysis */}
        <ScoreCard
          title={t('growth_analysis')}
          score={peterLynchAnalysis.growth_analysis.score}
          maxScore={peterLynchAnalysis.growth_analysis.max_score}
          percentage={peterLynchAnalysis.growth_analysis.score_percentage}
          details={peterLynchAnalysis.growth_analysis.details}
          icon={<TrendingUp className="w-5 h-5 text-blue-600" />}
          helpText={t('growth_help')}
        />

        {/* Business Quality Analysis */}
        <ScoreCard
          title={t('business_quality')}
          score={peterLynchAnalysis.business_quality_analysis.score}
          maxScore={peterLynchAnalysis.business_quality_analysis.max_score}
          percentage={peterLynchAnalysis.business_quality_analysis.score_percentage}
          details={peterLynchAnalysis.business_quality_analysis.details}
          icon={<Building className="w-5 h-5 text-blue-600" />}
          helpText={t('business_help')}
        />

        {/* Market Position Analysis */}
        <ScoreCard
          title={t('market_position')}
          score={peterLynchAnalysis.market_position_analysis.score}
          maxScore={peterLynchAnalysis.market_position_analysis.max_score}
          percentage={peterLynchAnalysis.market_position_analysis.score_percentage}
          details={peterLynchAnalysis.market_position_analysis.details}
          icon={<Zap className="w-5 h-5 text-blue-600" />}
          helpText={t('market_help')}
        />
      </div>

      {/* Key Metrics Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">关键GARP指标</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('peg_ratio')}</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {formatRatio(peterLynchAnalysis.garp_analysis.metrics.peg_ratio || peterLynchAnalysis.garp_analysis.metrics.calculated_peg)}
            </div>
          </div>
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('pe_ratio')}</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {formatRatio(peterLynchAnalysis.garp_analysis.metrics.pe_ratio)}
            </div>
          </div>
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('earnings_growth')}</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {formatPercentage(peterLynchAnalysis.garp_analysis.metrics.earnings_growth)}
            </div>
          </div>
          <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{t('revenue_growth')}</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {formatPercentage(peterLynchAnalysis.garp_analysis.metrics.revenue_growth)}
            </div>
          </div>
        </div>
      </div>

      {/* Lynch Principles Assessment */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-50 rounded-lg">
              <CheckCircle className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{t('lynch_principles')}</h3>
              <HelpTooltip content={t('principles_help')} />
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {peterLynchAnalysis.lynch_principles.total_principles_met}/{peterLynchAnalysis.lynch_principles.total_principles}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {peterLynchAnalysis.lynch_principles.adherence_percentage.toFixed(1)}% {t('adherence_percentage')}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <LynchPrincipleCard
            title={t('garp_principle')}
            score={peterLynchAnalysis.lynch_principles.individual_principles.growth_at_reasonable_price.score}
            description={peterLynchAnalysis.lynch_principles.individual_principles.growth_at_reasonable_price.description}
            meetsCriteria={peterLynchAnalysis.lynch_principles.individual_principles.growth_at_reasonable_price.meets_criteria}
            icon={<DollarSign className="w-4 h-4" />}
          />
          
          <LynchPrincipleCard
            title={t('consistent_growth')}
            score={peterLynchAnalysis.lynch_principles.individual_principles.consistent_growth.score}
            description={peterLynchAnalysis.lynch_principles.individual_principles.consistent_growth.description}
            meetsCriteria={peterLynchAnalysis.lynch_principles.individual_principles.consistent_growth.meets_criteria}
            icon={<TrendingUp className="w-4 h-4" />}
          />
          
          <LynchPrincipleCard
            title={t('business_quality_principle')}
            score={peterLynchAnalysis.lynch_principles.individual_principles.business_quality.score}
            description={peterLynchAnalysis.lynch_principles.individual_principles.business_quality.description}
            meetsCriteria={peterLynchAnalysis.lynch_principles.individual_principles.business_quality.meets_criteria}
            icon={<Building className="w-4 h-4" />}
          />
          
          <LynchPrincipleCard
            title={t('market_position_principle')}
            score={peterLynchAnalysis.lynch_principles.individual_principles.market_position.score}
            description={peterLynchAnalysis.lynch_principles.individual_principles.market_position.description}
            meetsCriteria={peterLynchAnalysis.lynch_principles.individual_principles.market_position.meets_criteria}
            icon={<Zap className="w-4 h-4" />}
          />
        </div>

        {/* Overall Assessment */}
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <h4 className="font-medium text-gray-900 dark:text-white mb-2">整体评估</h4>
          <p className="text-gray-700 dark:text-gray-300">{peterLynchAnalysis.lynch_principles.overall_assessment}</p>
        </div>
      </div>

      {/* Investment Reasoning */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">{t('investment_reasoning')}</h3>
        <div className="prose prose-sm max-w-none text-gray-700 dark:text-gray-300">
          {Array.isArray(peterLynchAnalysis.investment_reasoning) 
            ? peterLynchAnalysis.investment_reasoning.map((reason, index) => (
                <p key={index} className="mb-2">{reason}</p>
              ))
            : <p>{peterLynchAnalysis.investment_reasoning}</p>
          }
        </div>
      </div>

      {/* LLM Insights */}
      {llmInsights && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{t('llm_insights_title')}</h3>
          </div>
          <div className="prose prose-sm max-w-none text-gray-700 dark:text-gray-300 dark:prose-invert">
            <ReactMarkdown>{llmInsights}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
} 