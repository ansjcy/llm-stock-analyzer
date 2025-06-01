export interface PEHistoryData {
  Date: string;
  Close: number;
  TTM_EPS: number;
  PE_Ratio: number;
  timestamp: number;  // Unix timestamp for better date handling
}

export interface PEHistory {
  historical_data?: PEHistoryData[];
  current_pe?: number;
  avg_pe_1y?: number;
  avg_pe_6m?: number;
  avg_pe_3m?: number;
  min_pe_1y?: number;
  max_pe_1y?: number;
  median_pe_1y?: number;
  pe_percentile?: number;
}

export interface StockInfo {
  name: string;
  current_price?: number;
  previous_close?: number;
  day_low?: number;
  day_high?: number;
  week_52_low?: number;
  week_52_high?: number;
  '52_week_low'?: number;  // Alternative key format from llm-stock-analysis
  '52_week_high'?: number; // Alternative key format from llm-stock-analysis
  market_cap?: number;
  volume?: number;
  pe_ratio?: number;
  beta?: number;
  sector?: string;
  industry?: string;
  dividend_yield?: number;
  pe_history?: PEHistory;
  [key: string]: unknown;
}

export interface TechnicalIndicator {
  signal: string;
  score?: number;
  confidence?: number;
  reasoning?: string;
}

export interface TechnicalAnalysis {
  overall_signal: string;
  confidence: number;
  strategic_combinations?: {
    rsi_macd_strategy?: TechnicalIndicator;
    bollinger_rsi_macd_strategy?: TechnicalIndicator;
    ma_rsi_volume_strategy?: TechnicalIndicator;
  };
  momentum?: {
    rsi?: number;
    rsi_signal?: string;
    stoch_k?: number;
    stoch_signal?: string;
  };
  trend?: {
    macd_signal?: string;
    macd_histogram?: number;
  };
  moving_averages?: {
    sma_trend?: string;
    price_vs_sma_20?: number;
    price_vs_sma_50?: number;
    price_vs_sma_200?: number;
  };
  [key: string]: unknown;
}

export interface CorrelationAnalysis {
  correlations: {
    [symbol: string]: number;
  };
  beta?: number;
  diversification_score?: number;
}

export interface NewsArticle {
  title: string;
  published?: string;  // Used in sample data
  publish_time?: string;  // Used in actual generated data
  summary: string;
  url?: string;
}

export interface NewsAnalysis {
  articles_found: number;
  recent_articles: NewsArticle[];
}

export interface LLMInsights {
  technical?: string;
  fundamental?: string;
  news?: string;
  warren_buffett?: string;
}

export interface Recommendation {
  full_analysis: string;
}

export interface Summary {
  executive_summary: string;
}

export interface Charts {
  technical_analysis?: string;
  correlation?: string;
}

// Warren Buffett Analysis Types
export interface WarrenBuffettFundamentalAnalysis {
  score: number;
  max_score: number;
  score_percentage: number;
  details: string[];
  metrics: {
    return_on_equity?: number;
    debt_to_equity?: number;
    operating_margin?: number;
    current_ratio?: number;
    [key: string]: unknown;
  };
}

export interface WarrenBuffettConsistencyAnalysis {
  score: number;
  max_score: number;
  score_percentage: number;
  details: string[];
  revenue_growth_consistency?: number;
  earnings_growth_consistency?: number;
  fcf_growth_consistency?: number;
}

export interface WarrenBuffettMoatAnalysis {
  score: number;
  max_score: number;
  score_percentage: number;
  details: string[];
  competitive_advantages: string[];
  moat_strength: string;
}

export interface WarrenBuffettManagementAnalysis {
  score: number;
  max_score: number;
  score_percentage: number;
  details: string[];
  capital_allocation_score?: number;
  shareholder_returns_score?: number;
}

export interface WarrenBuffettIntrinsicValueAnalysis {
  intrinsic_value?: number;
  current_price?: number;
  margin_of_safety?: number;
  valuation_method: string;
  dcf_details?: {
    free_cash_flow?: number;
    growth_rate?: number;
    terminal_value?: number;
    discount_rate?: number;
    [key: string]: unknown;
  };
  reasoning: string[];
}

export interface WarrenBuffettPrinciples {
  individual_principles: {
    financial_strength: {
      score: number;
      meets_criteria: boolean;
      description: string;
    };
    predictable_earnings: {
      score: number;
      meets_criteria: boolean;
      description: string;
    };
    competitive_advantage: {
      score: number;
      meets_criteria: boolean;
      description: string;
    };
    quality_management: {
      score: number;
      meets_criteria: boolean;
      description: string;
    };
    margin_of_safety: {
      score: number;
      meets_criteria: boolean;
      description: string;
    };
  };
  total_principles_met: number;
  total_principles: number;
  adherence_percentage: number;
  overall_assessment: string;
}

export interface WarrenBuffettAnalysis {
  ticker: string;
  analysis_date: string;
  overall_signal: string;
  confidence: number;
  total_score: number;
  max_possible_score: number;
  score_percentage: number;
  margin_of_safety?: number;
  fundamental_analysis: WarrenBuffettFundamentalAnalysis;
  consistency_analysis: WarrenBuffettConsistencyAnalysis;
  moat_analysis: WarrenBuffettMoatAnalysis;
  management_analysis: WarrenBuffettManagementAnalysis;
  intrinsic_value_analysis: WarrenBuffettIntrinsicValueAnalysis;
  investment_reasoning: string | string[];
  buffett_principles: WarrenBuffettPrinciples;
}

export interface StockAnalysisResult {
  ticker: string;
  analysis_date: string;
  stock_info: StockInfo;
  technical_analysis: TechnicalAnalysis;
  correlation_analysis: CorrelationAnalysis;
  fundamental_analysis: Record<string, unknown>;
  warren_buffett_analysis?: WarrenBuffettAnalysis;
  news_analysis: NewsAnalysis;
  llm_insights: LLMInsights;
  recommendation: Recommendation;
  summary: Summary;
  charts: Charts;
} 