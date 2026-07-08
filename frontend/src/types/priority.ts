export interface ClusterPriorityAnalysis {
  priority_score: number;
  impact_score: number;
  urgency_level: string;
  risk_level: string;
  affected_population_estimate: string;
  public_safety_risk: string;
  infrastructure_criticality: string;
  environmental_impact: string;
  economic_impact: string;
  suggested_department: string;
  recommended_action: string;
  estimated_resolution_time: string;
  estimated_budget_range: string;
  priority_rank?: number | null;
  reasoning: string;
  confidence_score: number;
  contributing_factors: string[];
  expected_impact: string;
  estimated_beneficiaries: string;
  why_priority_ranked_high: string;
  analysis_hash: string;
  processed_at: string;
  model_version: string;
  prompt_version: string;
}

export interface PriorityClusterCard {
  id: string;
  title: string;
  category: string;
  status: string;
  village_name?: string | null;
  department?: string | null;
  complaint_count: number;
  priority_score: number;
  impact_score: number;
  urgency_level?: string | null;
  risk_level?: string | null;
  priority_rank?: number | null;
  recommended_department?: string | null;
  recommended_action?: string | null;
  affected_population?: string | null;
  priority_confidence?: number | null;
  latest_complaint_date?: string | null;
  priority_updated_at?: string | null;
}

export interface PriorityRecommendationPanel {
  cluster_id: string;
  cluster_title: string;
  priority_rank: number;
  priority_score: number;
  impact_score: number;
  why_priority_ranked_high: string;
  contributing_factors: string[];
  expected_impact: string;
  estimated_beneficiaries: string;
  recommended_action: string;
  estimated_resolution_time?: string | null;
  estimated_budget?: string | null;
  confidence_score: number;
  reasoning: string;
}

export interface PriorityBreakdownItem {
  label: string;
  count: number;
  average_priority_score: number;
  average_impact_score: number;
}

export interface PriorityDashboard {
  success: boolean;
  total_analyzed_clusters: number;
  critical_clusters: number;
  high_urgency_clusters: number;
  average_priority_score: number;
  average_impact_score: number;
  top_priorities: PriorityClusterCard[];
  leaderboard: PriorityClusterCard[];
  critical_issues: PriorityClusterCard[];
  highest_impact_areas: PriorityClusterCard[];
  department_breakdown: PriorityBreakdownItem[];
  village_breakdown: PriorityBreakdownItem[];
  recommendations: PriorityRecommendationPanel[];
  last_updated_at?: string | null;
}

export interface PriorityAnalyzeResponse {
  success: boolean;
  message: string;
  cluster_id: string;
  priority_analysis?: ClusterPriorityAnalysis | null;
}

export interface PriorityRerankResponse {
  success: boolean;
  message: string;
  clusters_analyzed: number;
  clusters_skipped: number;
  ranks_updated: number;
  errors: string[];
}
