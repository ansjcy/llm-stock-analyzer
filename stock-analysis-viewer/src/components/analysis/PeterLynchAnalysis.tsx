import React from 'react';
import { PeterLynchAnalysis as PeterLynchAnalysisType } from '../../types/analysis';

interface PeterLynchAnalysisProps {
  peterLynchAnalysis: PeterLynchAnalysisType;
}

const PeterLynchAnalysis: React.FC<PeterLynchAnalysisProps> = ({ peterLynchAnalysis }) => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-purple-800 mb-2">
          Peter Lynch Analysis / 彼得·林奇分析
        </h1>
        <p className="text-lg text-gray-600">
          Growth at Reasonable Price (GARP) Investment Philosophy
        </p>
        <p className="text-sm text-gray-500 mt-2">
          "Know what you own, and know why you own it." - Peter Lynch
        </p>
      </div>

      {/* Overall Signal */}
      <div className={`text-center p-6 rounded-lg ${
        peterLynchAnalysis.overall_signal === 'bullish' ? 'bg-green-100 border border-green-300' :
        peterLynchAnalysis.overall_signal === 'bearish' ? 'bg-red-100 border border-red-300' :
        'bg-yellow-100 border border-yellow-300'
      }`}>
        <h2 className="text-2xl font-bold mb-2">
          投资信号 / Investment Signal
        </h2>
        <div className="flex items-center justify-center space-x-4">
          <span className={`text-3xl font-bold ${
            peterLynchAnalysis.overall_signal === 'bullish' ? 'text-green-600' :
            peterLynchAnalysis.overall_signal === 'bearish' ? 'text-red-600' :
            'text-yellow-600'
          }`}>
            {peterLynchAnalysis.overall_signal.toUpperCase()}
          </span>
          <div className="text-center">
            <div className="text-sm text-gray-600">Confidence Level</div>
            <div className="text-xl font-semibold">{peterLynchAnalysis.confidence.toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {/* Key Metrics - PEG Focus */}
      <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
        <h3 className="text-xl font-bold text-purple-800 mb-4">
          核心指标 / Key Metrics (GARP Focus)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg text-center">
            <h4 className="text-sm font-medium text-gray-600 mb-1">PEG Ratio</h4>
            <div className="text-2xl font-bold text-purple-600">
              {peterLynchAnalysis.garp_analysis.metrics.calculated_peg?.toFixed(2) || 'N/A'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {(peterLynchAnalysis.garp_analysis.metrics.calculated_peg || 0) < 1 ? 'Attractive' : 'Expensive'}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg text-center">
            <h4 className="text-sm font-medium text-gray-600 mb-1">P/E Ratio</h4>
            <div className="text-2xl font-bold text-purple-600">
              {peterLynchAnalysis.garp_analysis.metrics.pe_ratio?.toFixed(1) || 'N/A'}
            </div>
            <div className="text-xs text-gray-500 mt-1">市盈率</div>
          </div>
          <div className="bg-white p-4 rounded-lg text-center">
            <h4 className="text-sm font-medium text-gray-600 mb-1">Earnings Growth</h4>
            <div className="text-2xl font-bold text-purple-600">
              {((peterLynchAnalysis.garp_analysis.metrics.earnings_growth || 0) * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">盈利增长率</div>
          </div>
        </div>
      </div>

      {/* Analysis Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* GARP Analysis */}
        <div className="bg-white p-6 rounded-lg border border-purple-200 shadow-sm">
          <h3 className="text-xl font-bold text-purple-800 mb-4">
            {peterLynchAnalysis.garp_analysis.category}
          </h3>
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">Score:</span>
              <span className="text-lg font-bold text-purple-600">
                {peterLynchAnalysis.garp_analysis.score}/{peterLynchAnalysis.garp_analysis.max_score}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${peterLynchAnalysis.garp_analysis.score_percentage}%` }}
              ></div>
            </div>
            <div className="text-right text-sm text-gray-600 mt-1">
              {peterLynchAnalysis.garp_analysis.score_percentage.toFixed(1)}%
            </div>
          </div>
          <ul className="space-y-2">
            {peterLynchAnalysis.garp_analysis.details.map((detail, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="text-purple-500 mr-2">•</span>
                {detail}
              </li>
            ))}
          </ul>
        </div>

        {/* Growth Analysis */}
        <div className="bg-white p-6 rounded-lg border border-purple-200 shadow-sm">
          <h3 className="text-xl font-bold text-purple-800 mb-4">
            {peterLynchAnalysis.growth_analysis.category}
          </h3>
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">Score:</span>
              <span className="text-lg font-bold text-purple-600">
                {peterLynchAnalysis.growth_analysis.score}/{peterLynchAnalysis.growth_analysis.max_score}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${peterLynchAnalysis.growth_analysis.score_percentage}%` }}
              ></div>
            </div>
            <div className="text-right text-sm text-gray-600 mt-1">
              {peterLynchAnalysis.growth_analysis.score_percentage.toFixed(1)}%
            </div>
          </div>
          <ul className="space-y-2">
            {peterLynchAnalysis.growth_analysis.details.map((detail, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="text-purple-500 mr-2">•</span>
                {detail}
              </li>
            ))}
          </ul>
        </div>

        {/* Business Quality Analysis */}
        <div className="bg-white p-6 rounded-lg border border-purple-200 shadow-sm">
          <h3 className="text-xl font-bold text-purple-800 mb-4">
            {peterLynchAnalysis.business_quality_analysis.category}
          </h3>
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">Score:</span>
              <span className="text-lg font-bold text-purple-600">
                {peterLynchAnalysis.business_quality_analysis.score}/{peterLynchAnalysis.business_quality_analysis.max_score}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${peterLynchAnalysis.business_quality_analysis.score_percentage}%` }}
              ></div>
            </div>
            <div className="text-right text-sm text-gray-600 mt-1">
              {peterLynchAnalysis.business_quality_analysis.score_percentage.toFixed(1)}%
            </div>
          </div>
          <ul className="space-y-2">
            {peterLynchAnalysis.business_quality_analysis.details.map((detail, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="text-purple-500 mr-2">•</span>
                {detail}
              </li>
            ))}
          </ul>
        </div>

        {/* Market Position Analysis */}
        <div className="bg-white p-6 rounded-lg border border-purple-200 shadow-sm">
          <h3 className="text-xl font-bold text-purple-800 mb-4">
            {peterLynchAnalysis.market_position_analysis.category}
          </h3>
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">Score:</span>
              <span className="text-lg font-bold text-purple-600">
                {peterLynchAnalysis.market_position_analysis.score}/{peterLynchAnalysis.market_position_analysis.max_score}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${peterLynchAnalysis.market_position_analysis.score_percentage}%` }}
              ></div>
            </div>
            <div className="text-right text-sm text-gray-600 mt-1">
              {peterLynchAnalysis.market_position_analysis.score_percentage.toFixed(1)}%
            </div>
          </div>
          <ul className="space-y-2">
            {peterLynchAnalysis.market_position_analysis.details.map((detail, index) => (
              <li key={index} className="text-sm text-gray-700 flex items-start">
                <span className="text-purple-500 mr-2">•</span>
                {detail}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Lynch Principles */}
      <div className="bg-gray-50 p-6 rounded-lg">
        <h3 className="text-xl font-bold text-gray-800 mb-4">
          Lynch投资原则评估 / Lynch Investment Principles
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-lg border border-purple-200">
            <h4 className="font-semibold text-purple-800 mb-2">
              GARP原则 / GARP Principle
            </h4>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Score:</span>
              <span className={`px-2 py-1 rounded text-sm font-medium ${
                peterLynchAnalysis.lynch_principles.individual_principles.growth_at_reasonable_price.meets_criteria 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {peterLynchAnalysis.lynch_principles.individual_principles.growth_at_reasonable_price.score.toFixed(1)}%
              </span>
            </div>
            <p className="text-sm text-gray-700">
              {peterLynchAnalysis.lynch_principles.individual_principles.growth_at_reasonable_price.description}
            </p>
          </div>

          <div className="bg-white p-4 rounded-lg border border-purple-200">
            <h4 className="font-semibold text-purple-800 mb-2">
              持续增长 / Consistent Growth
            </h4>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Score:</span>
              <span className={`px-2 py-1 rounded text-sm font-medium ${
                peterLynchAnalysis.lynch_principles.individual_principles.consistent_growth.meets_criteria 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {peterLynchAnalysis.lynch_principles.individual_principles.consistent_growth.score.toFixed(1)}%
              </span>
            </div>
            <p className="text-sm text-gray-700">
              {peterLynchAnalysis.lynch_principles.individual_principles.consistent_growth.description}
            </p>
          </div>

          <div className="bg-white p-4 rounded-lg border border-purple-200">
            <h4 className="font-semibold text-purple-800 mb-2">
              业务质量 / Business Quality
            </h4>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Score:</span>
              <span className={`px-2 py-1 rounded text-sm font-medium ${
                peterLynchAnalysis.lynch_principles.individual_principles.business_quality.meets_criteria 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {peterLynchAnalysis.lynch_principles.individual_principles.business_quality.score.toFixed(1)}%
              </span>
            </div>
            <p className="text-sm text-gray-700">
              {peterLynchAnalysis.lynch_principles.individual_principles.business_quality.description}
            </p>
          </div>

          <div className="bg-white p-4 rounded-lg border border-purple-200">
            <h4 className="font-semibold text-purple-800 mb-2">
              市场定位 / Market Position
            </h4>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Score:</span>
              <span className={`px-2 py-1 rounded text-sm font-medium ${
                peterLynchAnalysis.lynch_principles.individual_principles.market_position.meets_criteria 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {peterLynchAnalysis.lynch_principles.individual_principles.market_position.score.toFixed(1)}%
              </span>
            </div>
            <p className="text-sm text-gray-700">
              {peterLynchAnalysis.lynch_principles.individual_principles.market_position.description}
            </p>
          </div>
        </div>

        {/* Overall Assessment */}
        <div className="mt-6 bg-white p-4 rounded-lg border border-purple-200">
          <h4 className="font-semibold text-purple-800 mb-2">
            整体评估 / Overall Assessment
          </h4>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">
              Principles Met: {peterLynchAnalysis.lynch_principles.total_principles_met} / {peterLynchAnalysis.lynch_principles.total_principles}
            </span>
            <span className="text-lg font-bold text-purple-600">
              {peterLynchAnalysis.lynch_principles.adherence_percentage.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
            <div 
              className="bg-purple-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${peterLynchAnalysis.lynch_principles.adherence_percentage}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-700 font-medium">
            {peterLynchAnalysis.lynch_principles.overall_assessment}
          </p>
        </div>
      </div>

      {/* Investment Reasoning */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="text-xl font-bold text-blue-800 mb-4">
          投资推理 / Investment Reasoning
        </h3>
        <div className="prose prose-blue max-w-none">
          {Array.isArray(peterLynchAnalysis.investment_reasoning) ? (
            <ul className="space-y-2">
              {peterLynchAnalysis.investment_reasoning.map((reason, index) => (
                <li key={index} className="text-gray-700">
                  {reason}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-700 whitespace-pre-wrap">
              {peterLynchAnalysis.investment_reasoning}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PeterLynchAnalysis; 