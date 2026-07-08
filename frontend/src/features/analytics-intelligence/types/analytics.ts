export interface IntelligenceKPIs {
  total_complaints: number;
  resolved_complaints: number;
  pending_complaints: number;
  critical_issues: number;
  active_clusters: number;
  average_ai_priority: number;
  average_severity_score: number;
  average_resolution_days: number;
  departments_count: number;
  villages_count: number;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: string | number;
}

export interface TrendDataPoint {
  date: string;
  count: number;
}

export interface IntelligenceCharts {
  complaint_trend_daily: TrendDataPoint[];
  complaint_trend_weekly: TrendDataPoint[];
  complaint_trend_monthly: TrendDataPoint[];
  complaint_categories: ChartDataPoint[];
  department_distribution: ChartDataPoint[];
  village_comparison: ChartDataPoint[];
  priority_distribution: ChartDataPoint[];
  severity_distribution: ChartDataPoint[];
  cluster_size_distribution: ChartDataPoint[];
  resolution_status: ChartDataPoint[];
  top_villages: ChartDataPoint[];
  top_departments: ChartDataPoint[];
  complaint_timeline: TrendDataPoint[];
  ai_confidence_distribution: ChartDataPoint[];
}

export interface PredictiveAnalyticsCard {
  key: string;
  title: string;
  value: string;
  detail: string;
  confidence: number;
  trend_direction: string;
  model_version: string;
  metadata: Record<string, string>;
}

export interface PredictiveAnalytics {
  cards: PredictiveAnalyticsCard[];
  engine: string;
  generated_at: string;
}

export interface AnalyticsIntelligenceResponse {
  success: boolean;
  kpis: IntelligenceKPIs;
  charts: IntelligenceCharts;
  predictive: PredictiveAnalytics;
  export_rows: Array<Record<string, string | number>>;
  last_updated_at: string;
}

export interface AnalyticsFilters {
  dateFrom?: string;
  dateTo?: string;
  village?: string;
  department?: string;
  category?: string;
  priority?: string;
  severity?: string;
  cluster?: string;
  status?: string;
}
