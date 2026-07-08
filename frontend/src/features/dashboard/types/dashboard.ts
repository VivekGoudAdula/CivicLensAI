import type { PriorityClusterCard, PriorityRecommendationPanel } from "@/types/priority";

export type ActivityType =
  | "complaint_submitted"
  | "ai_analysis_completed"
  | "image_analysis_completed"
  | "cluster_created"
  | "cluster_updated"
  | "priority_updated"
  | "recommendation_generated";

export interface DashboardKPIs {
  total_complaints: number;
  open_complaints: number;
  resolved_complaints: number;
  active_clusters: number;
  critical_issues: number;
  average_ai_priority_score: number;
  departments_involved: number;
  villages_covered: number;
  todays_complaints: number;
  todays_ai_analyses: number;
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

export interface DashboardCharts {
  complaints_by_category: ChartDataPoint[];
  complaints_by_department: ChartDataPoint[];
  priority_distribution: ChartDataPoint[];
  severity_distribution: ChartDataPoint[];
  village_wise_complaints: ChartDataPoint[];
  department_workload: ChartDataPoint[];
  complaint_trend_daily: TrendDataPoint[];
  complaint_trend_weekly: TrendDataPoint[];
  complaint_trend_monthly: TrendDataPoint[];
  top_categories: ChartDataPoint[];
  top_villages: ChartDataPoint[];
  top_departments: ChartDataPoint[];
}

export interface DashboardActivityItem {
  id: string;
  type: ActivityType;
  title: string;
  description: string;
  entity_id: string;
  entity_type: string;
  occurred_at: string;
  metadata: Record<string, string>;
}

export interface DashboardComplaintSummary {
  id: string;
  title: string;
  category_name: string;
  status: string;
  village_name: string;
  priority_score?: number | null;
  severity?: string | null;
  submitted_at: string;
  has_ai_analysis: boolean;
  cluster_id?: string | null;
}

export interface DashboardClusterSummary {
  id: string;
  title: string;
  complaint_count: number;
  average_severity?: string | null;
  priority_score: number;
  village_name?: string | null;
  department?: string | null;
  latest_complaint_date?: string | null;
  representative_complaint_id?: string | null;
}

export interface DashboardDepartmentSummary {
  department: string;
  complaint_count: number;
  cluster_count: number;
  average_priority_score: number;
}

export interface DashboardVillageSummary {
  village_name: string;
  complaint_count: number;
  cluster_count: number;
  average_priority_score: number;
}

export interface DashboardAIInsights {
  highest_risk_area: string;
  most_common_issue: string;
  department_overload: string;
  trending_complaints: string[];
  fastest_growing_cluster?: string | null;
  suggested_actions: string[];
  todays_highlights: string[];
}

export interface DashboardHomeResponse {
  success: boolean;
  kpis: DashboardKPIs;
  top_priorities: PriorityClusterCard[];
  recommendations: PriorityRecommendationPanel[];
  recent_complaints: DashboardComplaintSummary[];
  cluster_summary: DashboardClusterSummary[];
  department_summary: DashboardDepartmentSummary[];
  village_summary: DashboardVillageSummary[];
  recent_activities: DashboardActivityItem[];
  ai_insights: DashboardAIInsights;
  charts: DashboardCharts;
  last_updated_at: string;
}

export interface DashboardActivitiesResponse {
  success: boolean;
  items: DashboardActivityItem[];
  total: number;
}

export interface DashboardAnalyticsResponse {
  success: boolean;
  charts: DashboardCharts;
  kpis: DashboardKPIs;
  ai_insights: DashboardAIInsights;
}

export interface DashboardFilters {
  dateFrom?: string;
  dateTo?: string;
  village?: string;
  department?: string;
  category?: string;
  priority?: string;
  severity?: string;
  status?: string;
  aiConfidenceMin?: number;
  search?: string;
}
