import React from 'react';
import { WarrenBuffettAnalysis } from '@/types/analysis';
import { TrendingUp, TrendingDown, Activity, DollarSign, Shield, Users, Target, CheckCircle, Brain } from 'lucide-react';
import HelpTooltip from './HelpTooltip';

interface WarrenBuffettAnalysisProps {
  warrenBuffettAnalysis: WarrenBuffettAnalysis;
  llmInsights?: string;
}

export default function WarrenBuffettAnalysisComponent({ warrenBuffettAnalysis, llmInsights }: WarrenBuffettAnalysisProps) {
  // Always use Chinese content by default
  const isChineseContent = true;

  // Translation function
  const t = (key: string) => {
    if (!isChineseContent) return translations.en[key] || key;
    return translations.zh[key] || key;
  };

  const translations: {
    en: { [key: string]: string };
    zh: { [key: string]: string };
  } = {
    en: {
      'warren_buffett_analysis': 'Warren Buffett Analysis',
      'overall_quality_score': 'Overall Quality Score',
      'margin_of_safety': 'Margin of Safety',
      'confidence_level': 'Confidence Level',
      'analysis_reliability': 'Analysis Reliability',
      'intrinsic_value_analysis': 'Intrinsic Value Analysis',
      'intrinsic_value': 'Intrinsic Value',
      'current_price': 'Current Price',
      'method': 'Method',
      'fundamental_analysis': 'Fundamental Analysis',
      'business_consistency': 'Business Consistency',
      'economic_moat': 'Economic Moat',
      'management_quality': 'Management Quality',
      'buffett_principles': 'Buffett\'s Investment Principles',
      'overall_assessment': 'Overall Assessment',
      'principles_met': 'Principles Met',
      'financial_strength': 'Financial Strength',
      'predictable_earnings': 'Predictable Earnings',
      'competitive_advantage': 'Competitive Advantage',
      'quality_management': 'Quality Management',
      'investment_reasoning': 'Investment Reasoning',
      'competitive_advantages': 'Competitive Advantages',
      'moat_strength': 'Moat Strength',
      'undervalued': 'Undervalued',
      'overvalued_fair_value': 'Overvalued or Fair Value',
      'no_investment_reasoning': 'No investment reasoning available',
      'meets_criteria': 'Meets Criteria',
      'does_not_meet_criteria': 'Does Not Meet Criteria',
      'dcf_model_terminal': 'DCF Model with Terminal Value',
      'wide_moat': 'Wide',
      'narrow_moat': 'Narrow',
      'no_moat': 'None',
      'excellent_candidate': 'Excellent Buffett candidate',
      'good_candidate': 'Good Buffett candidate',
      'fair_candidate': 'Fair Buffett candidate',
      'poor_candidate': 'Poor Buffett candidate',
      'ai_insights': 'AI Insights'
    },
    zh: {
      'warren_buffett_analysis': '沃伦·巴菲特分析',
      'overall_quality_score': '整体质量评分',
      'margin_of_safety': '安全边际',
      'confidence_level': '信心水平',
      'analysis_reliability': '分析可靠性',
      'intrinsic_value_analysis': '内在价值分析',
      'intrinsic_value': '内在价值',
      'current_price': '当前价格',
      'method': '方法',
      'fundamental_analysis': '基本面分析',
      'business_consistency': '业务一致性',
      'economic_moat': '经济护城河',
      'management_quality': '管理质量',
      'buffett_principles': '巴菲特投资原则',
      'overall_assessment': '整体评估',
      'principles_met': '符合原则',
      'financial_strength': '财务实力',
      'predictable_earnings': '可预测收益',
      'competitive_advantage': '竞争优势',
      'quality_management': '管理质量',
      'investment_reasoning': '投资理由',
      'competitive_advantages': '竞争优势',
      'moat_strength': '护城河强度',
      'undervalued': '被低估',
      'overvalued_fair_value': '被高估或公平价值',
      'no_investment_reasoning': '暂无投资理由',
      'meets_criteria': '符合标准',
      'does_not_meet_criteria': '不符合标准',
      'dcf_model_terminal': '带终值的DCF模型',
      'wide_moat': '宽阔',
      'narrow_moat': '狭窄',
      'no_moat': '无',
      'excellent_candidate': '优秀的巴菲特候选股',
      'good_candidate': '良好的巴菲特候选股',
      'fair_candidate': '一般的巴菲特候选股',
      'poor_candidate': '较差的巴菲特候选股',
      'ai_insights': 'AI洞察'
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal.toLowerCase()) {
      case 'buy':
      case 'strong_buy':
      case '买入':
      case '强烈买入':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300';
      case 'sell':
      case 'strong_sell':
      case '卖出':
      case '强烈卖出':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300';
      case 'hold':
      case 'neutral':
      case '持有':
      case '中性':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300';
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal.toLowerCase()) {
      case 'buy':
      case 'strong_buy':
      case '买入':
      case '强烈买入':
        return <TrendingUp size={16} />;
      case 'sell':
      case 'strong_sell':
      case '卖出':
      case '强烈卖出':
        return <TrendingDown size={16} />;
      default:
        return <Activity size={16} />;
    }
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600 dark:text-green-400';
    if (percentage >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getMarginOfSafetyColor = (margin: number | undefined) => {
    if (!margin) return 'text-gray-600 dark:text-gray-400';
    if (margin > 20) return 'text-green-600 dark:text-green-400';
    if (margin > 0) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const formatCurrency = (value: number | undefined) => {
    if (!value) return 'N/A';
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  const formatSignalText = (signal: string) => {
    const signalTranslations: { [key: string]: string } = {
      'buy': isChineseContent ? '买入' : 'Buy',
      'strong_buy': isChineseContent ? '强烈买入' : 'Strong Buy',
      'sell': isChineseContent ? '卖出' : 'Sell',
      'strong_sell': isChineseContent ? '强烈卖出' : 'Strong Sell',
      'hold': isChineseContent ? '持有' : 'Hold',
      'neutral': isChineseContent ? '中性' : 'Neutral'
    };
    
    return signalTranslations[signal.toLowerCase()] || signal;
  };

  const formatMoatStrength = (strength: string) => {
    const moatTranslations: { [key: string]: string } = {
      'wide': isChineseContent ? '宽阔' : 'Wide',
      'narrow': isChineseContent ? '狭窄' : 'Narrow',
      'none': isChineseContent ? '无' : 'None',
      'no': isChineseContent ? '无' : 'None',
      '宽阔': isChineseContent ? '宽阔' : 'Wide',
      '狭窄': isChineseContent ? '狭窄' : 'Narrow',
      '无': isChineseContent ? '无' : 'None'
    };
    
    return moatTranslations[strength.toLowerCase()] || strength;
  };

  const ScoreCard = ({ 
    title, 
    score, 
    maxScore, 
    percentage, 
    details, 
    icon 
  }: { 
    title: string; 
    score: number; 
    maxScore: number; 
    percentage: number; 
    details: string[]; 
    icon: React.ReactNode;
  }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          {icon}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${getScoreColor(percentage)}`}>
            {score}/{maxScore}
          </div>
          <div className={`text-sm ${getScoreColor(percentage)}`}>
            {percentage.toFixed(1)}%
          </div>
        </div>
      </div>
      
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-4">
        <div 
          className={`h-3 rounded-full transition-all duration-500 ${
            percentage >= 80 ? 'bg-green-500' : 
            percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="space-y-2">
        {details.map((detail, index) => (
          <div key={index} className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
            <span className="text-sm text-gray-600 dark:text-gray-300">{detail}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const BuffettPrincipleCard = ({ 
    title, 
    score, 
    reasoning, 
    meetsCriteria,
    icon 
  }: { 
    title: string; 
    score: number; 
    reasoning: string; 
    meetsCriteria: boolean;
    icon: React.ReactNode;
  }) => (
    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {icon}
          <h4 className="font-semibold text-gray-900 dark:text-white">{title}</h4>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`text-lg font-bold ${getScoreColor(score)}`}>
            {score.toFixed(0)}%
          </div>
          <div className={`w-3 h-3 rounded-full ${
            meetsCriteria ? 'bg-green-500' : 'bg-red-500'
          }`} title={meetsCriteria ? 'Meets Criteria' : 'Does Not Meet Criteria'} />
        </div>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">{reasoning}</p>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Overall Assessment */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center space-x-2">
            <DollarSign className="w-8 h-8 text-blue-600" />
            <span>{t('warren_buffett_analysis')}</span>
            <HelpTooltip content={
              isChineseContent ? 
                "基于沃伦·巴菲特投资原则的综合价值投资分析，包括基本面实力、业务一致性、经济护城河和管理质量。" :
                "Comprehensive value investing analysis based on Warren Buffett's investment principles including fundamental strength, business consistency, economic moat, and management quality."
            } />
          </h2>
          <div className={`px-4 py-2 rounded-full flex items-center space-x-2 ${getSignalColor(warrenBuffettAnalysis.overall_signal)}`}>
            {getSignalIcon(warrenBuffettAnalysis.overall_signal)}
            <span className="font-semibold capitalize">{formatSignalText(warrenBuffettAnalysis.overall_signal)}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {warrenBuffettAnalysis.score_percentage.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('overall_quality_score')}</div>
            <div className="text-xs text-gray-500 dark:text-gray-500">
              ({warrenBuffettAnalysis.total_score}/{warrenBuffettAnalysis.max_possible_score} points)
            </div>
          </div>
          
          <div className="text-center">
            <div className={`text-3xl font-bold ${getMarginOfSafetyColor(warrenBuffettAnalysis.margin_of_safety)}`}>
              {warrenBuffettAnalysis.margin_of_safety ? 
                `${warrenBuffettAnalysis.margin_of_safety.toFixed(1)}%` : 'N/A'}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('margin_of_safety')}</div>
            <div className="text-xs text-gray-500 dark:text-gray-500">
              {warrenBuffettAnalysis.margin_of_safety && warrenBuffettAnalysis.margin_of_safety > 0 ? 
                t('undervalued') : t('overvalued_fair_value')}
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
              {warrenBuffettAnalysis.confidence.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{t('confidence_level')}</div>
            <div className="text-xs text-gray-500 dark:text-gray-500">
              {t('analysis_reliability')}
            </div>
          </div>
        </div>

        {/* Intrinsic Value Analysis */}
        {warrenBuffettAnalysis.intrinsic_value_analysis.intrinsic_value && (
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{t('intrinsic_value_analysis')}</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-600 dark:text-gray-400">{t('intrinsic_value')}:</span>
                <span className="ml-2 font-semibold text-green-600 dark:text-green-400">
                  {formatCurrency(warrenBuffettAnalysis.intrinsic_value_analysis.intrinsic_value)}
                </span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">{t('current_price')}:</span>
                <span className="ml-2 font-semibold">
                  {formatCurrency(warrenBuffettAnalysis.intrinsic_value_analysis.current_price)}
                </span>
              </div>
              <div>
                <span className="text-gray-600 dark:text-gray-400">{t('method')}:</span>
                <span className="ml-2 font-semibold">
                  {isChineseContent && warrenBuffettAnalysis.intrinsic_value_analysis.valuation_method === 'DCF Model with Terminal Value' 
                    ? t('dcf_model_terminal') 
                    : warrenBuffettAnalysis.intrinsic_value_analysis.valuation_method}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Analysis Components Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ScoreCard
          title={t('fundamental_analysis')}
          score={warrenBuffettAnalysis.fundamental_analysis.score}
          maxScore={warrenBuffettAnalysis.fundamental_analysis.max_score}
          percentage={warrenBuffettAnalysis.fundamental_analysis.score_percentage}
          details={warrenBuffettAnalysis.fundamental_analysis.details}
          icon={<TrendingUp className="w-6 h-6 text-blue-600" />}
        />

        <ScoreCard
          title={t('business_consistency')}
          score={warrenBuffettAnalysis.consistency_analysis.score}
          maxScore={warrenBuffettAnalysis.consistency_analysis.max_score}
          percentage={warrenBuffettAnalysis.consistency_analysis.score_percentage}
          details={warrenBuffettAnalysis.consistency_analysis.details}
          icon={<Activity className="w-6 h-6 text-green-600" />}
        />

        <ScoreCard
          title={t('economic_moat')}
          score={warrenBuffettAnalysis.moat_analysis.score}
          maxScore={warrenBuffettAnalysis.moat_analysis.max_score}
          percentage={warrenBuffettAnalysis.moat_analysis.score_percentage}
          details={warrenBuffettAnalysis.moat_analysis.details}
          icon={<Shield className="w-6 h-6 text-purple-600" />}
        />

        <ScoreCard
          title={t('management_quality')}
          score={warrenBuffettAnalysis.management_analysis.score}
          maxScore={warrenBuffettAnalysis.management_analysis.max_score}
          percentage={warrenBuffettAnalysis.management_analysis.score_percentage}
          details={warrenBuffettAnalysis.management_analysis.details}
          icon={<Users className="w-6 h-6 text-orange-600" />}
        />
      </div>

      {/* Buffett's Four Principles */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
          <Target className="w-6 h-6 text-blue-600" />
          <span>{t('buffett_principles')}</span>
        </h3>
        
        <div className="mb-4">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {t('overall_assessment')}: <span className="font-semibold text-gray-900 dark:text-white">
              {(() => {
                const assessment = warrenBuffettAnalysis.buffett_principles.overall_assessment;
                if (isChineseContent) {
                  const assessmentMap: { [key: string]: string } = {
                    'excellent buffett candidate': t('excellent_candidate'),
                    'good buffett candidate': t('good_candidate'),
                    'fair buffett candidate': t('fair_candidate'),
                    'poor buffett candidate': t('poor_candidate')
                  };
                  return assessmentMap[assessment.toLowerCase()] || assessment;
                }
                return assessment;
              })()}
            </span>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            {t('principles_met')}: <span className="font-semibold">
              {warrenBuffettAnalysis.buffett_principles.total_principles_met} / {warrenBuffettAnalysis.buffett_principles.total_principles}
            </span> ({warrenBuffettAnalysis.buffett_principles.adherence_percentage.toFixed(1)}%)
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <BuffettPrincipleCard
            title={t('financial_strength')}
            score={warrenBuffettAnalysis.buffett_principles.individual_principles.financial_strength.score}
            reasoning={warrenBuffettAnalysis.buffett_principles.individual_principles.financial_strength.description}
            meetsCriteria={warrenBuffettAnalysis.buffett_principles.individual_principles.financial_strength.meets_criteria}
            icon={<Activity className="w-5 h-5 text-blue-600" />}
          />
          
          <BuffettPrincipleCard
            title={t('predictable_earnings')}
            score={warrenBuffettAnalysis.buffett_principles.individual_principles.predictable_earnings.score}
            reasoning={warrenBuffettAnalysis.buffett_principles.individual_principles.predictable_earnings.description}
            meetsCriteria={warrenBuffettAnalysis.buffett_principles.individual_principles.predictable_earnings.meets_criteria}
            icon={<TrendingUp className="w-5 h-5 text-green-600" />}
          />
          
          <BuffettPrincipleCard
            title={t('competitive_advantage')}
            score={warrenBuffettAnalysis.buffett_principles.individual_principles.competitive_advantage.score}
            reasoning={warrenBuffettAnalysis.buffett_principles.individual_principles.competitive_advantage.description}
            meetsCriteria={warrenBuffettAnalysis.buffett_principles.individual_principles.competitive_advantage.meets_criteria}
            icon={<Shield className="w-5 h-5 text-purple-600" />}
          />
          
          <BuffettPrincipleCard
            title={t('quality_management')}
            score={warrenBuffettAnalysis.buffett_principles.individual_principles.quality_management.score}
            reasoning={warrenBuffettAnalysis.buffett_principles.individual_principles.quality_management.description}
            meetsCriteria={warrenBuffettAnalysis.buffett_principles.individual_principles.quality_management.meets_criteria}
            icon={<Users className="w-5 h-5 text-orange-600" />}
          />
          
          <BuffettPrincipleCard
            title={t('margin_of_safety')}
            score={warrenBuffettAnalysis.buffett_principles.individual_principles.margin_of_safety.score}
            reasoning={warrenBuffettAnalysis.buffett_principles.individual_principles.margin_of_safety.description}
            meetsCriteria={warrenBuffettAnalysis.buffett_principles.individual_principles.margin_of_safety.meets_criteria}
            icon={<DollarSign className="w-5 h-5 text-red-600" />}
          />
        </div>
      </div>

      {/* Investment Reasoning */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">{t('investment_reasoning')}</h3>
        <div className="space-y-3">
          {(() => {
            // Handle both string and array types for investment_reasoning
            if (Array.isArray(warrenBuffettAnalysis.investment_reasoning) && warrenBuffettAnalysis.investment_reasoning.length > 0) {
              return warrenBuffettAnalysis.investment_reasoning.map((reason, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 dark:text-blue-400 text-sm font-semibold">{index + 1}</span>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">{reason}</p>
                </div>
              ));
            } else if (typeof warrenBuffettAnalysis.investment_reasoning === 'string' && warrenBuffettAnalysis.investment_reasoning.trim()) {
              return (
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-blue-600 dark:text-blue-400 text-sm font-semibold">1</span>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">{warrenBuffettAnalysis.investment_reasoning}</p>
                </div>
              );
            } else {
              return (
                <div className="text-gray-500 dark:text-gray-400 italic">
                  {t('no_investment_reasoning')}
                </div>
              );
            }
          })()}
        </div>
      </div>

      {/* Economic Moat Details */}
      {Array.isArray(warrenBuffettAnalysis.moat_analysis.competitive_advantages) && warrenBuffettAnalysis.moat_analysis.competitive_advantages.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Shield className="w-6 h-6 text-purple-600" />
            <span>{t('competitive_advantages')}</span>
          </h3>
          <div className="mb-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">{t('moat_strength')}: </span>
            <span className={`font-semibold ${
              warrenBuffettAnalysis.moat_analysis.moat_strength === 'Wide' ? 'text-green-600 dark:text-green-400' :
              warrenBuffettAnalysis.moat_analysis.moat_strength === 'Narrow' ? 'text-yellow-600 dark:text-yellow-400' :
              'text-red-600 dark:text-red-400'
            }`}>
              {formatMoatStrength(warrenBuffettAnalysis.moat_analysis.moat_strength)}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {warrenBuffettAnalysis.moat_analysis.competitive_advantages.map((advantage, index) => (
              <div key={index} className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                <span className="text-sm text-gray-700 dark:text-gray-300">{advantage}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Insights Section */}
      {llmInsights && (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <Brain className="w-6 h-6 text-purple-600" />
            <span>{t('ai_insights')}</span>
          </h3>
          <div className="prose dark:prose-invert max-w-none">
            <div className="text-gray-700 dark:text-gray-300">
              {llmInsights.split('\n').map((line, index) => {
                // Handle headers
                if (line.startsWith('## ')) {
                  return (
                    <h2 key={index} className="text-xl font-bold text-gray-900 dark:text-white mt-6 mb-3 first:mt-0">
                      {line.replace('## ', '')}
                    </h2>
                  );
                }
                if (line.startsWith('### ')) {
                  return (
                    <h3 key={index} className="text-lg font-semibold text-gray-800 dark:text-gray-200 mt-4 mb-2">
                      {line.replace('### ', '')}
                    </h3>
                  );
                }
                
                // Handle bold text
                if (line.includes('**')) {
                  const parts = line.split('**');
                  return (
                    <p key={index} className="mb-2">
                      {parts.map((part, partIndex) => 
                        partIndex % 2 === 1 ? (
                          <strong key={partIndex} className="font-semibold text-gray-900 dark:text-white">
                            {part}
                          </strong>
                        ) : (
                          <span key={partIndex}>{part}</span>
                        )
                      )}
                    </p>
                  );
                }
                
                // Handle bullet points
                if (line.startsWith('- ') || line.startsWith('• ')) {
                  return (
                    <div key={index} className="flex items-start space-x-2 mb-1">
                      <span className="text-blue-500 mt-1">•</span>
                      <span>{line.replace(/^[-•]\s/, '')}</span>
                    </div>
                  );
                }
                
                // Handle checkmarks
                if (line.startsWith('✅ ')) {
                  return (
                    <div key={index} className="flex items-start space-x-2 mb-2">
                      <span className="text-green-500 mt-1">✅</span>
                      <span>{line.replace('✅ ', '')}</span>
                    </div>
                  );
                }
                
                // Handle empty lines
                if (line.trim() === '') {
                  return <div key={index} className="h-2" />;
                }
                
                // Regular paragraphs
                return (
                  <p key={index} className="mb-2">
                    {line}
                  </p>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 