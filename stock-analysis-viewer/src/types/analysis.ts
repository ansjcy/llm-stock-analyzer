export interface PEHistoryData {
  Date: string;
  Close: number;
  TTM_EPS: number;
  PE_Ratio: number;
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
  [key: string]: any;
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
  [key: string]: any;
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

export interface StockAnalysisResult {
  ticker: string;
  analysis_date: string;
  stock_info: StockInfo;
  technical_analysis: TechnicalAnalysis;
  correlation_analysis: CorrelationAnalysis;
  fundamental_analysis: any;
  news_analysis: NewsAnalysis;
  llm_insights: LLMInsights;
  recommendation: Recommendation;
  summary: Summary;
  charts: Charts;
} 