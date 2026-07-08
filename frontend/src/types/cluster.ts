export type ClusterStatus =
  | "open"
  | "analyzing"
  | "recommended"
  | "assigned"
  | "resolved"
  | "archived";

export interface ClusterListItem {
  id: string;
  title: string;
  theme: string;
  category: string;
  status: ClusterStatus;
  department?: string | null;
  village_name?: string | null;
  complaint_count: number;
  average_severity?: string | null;
  latest_complaint_date?: string | null;
  representative_complaint_id?: string | null;
  priority_score: number;
  hotspot_score: number;
  average_confidence?: number | null;
  affected_area?: string | null;
  impact_score?: number | null;
  urgency_level?: string | null;
  priority_rank?: number | null;
  recommended_department?: string | null;
  recommended_action?: string | null;
  priority_confidence?: number | null;
  priority_updated_at?: string | null;
}

export interface ClusterComplaintSummary {
  id: string;
  title: string;
  status: string;
  village_name: string;
  submitted_at: string;
  is_duplicate: boolean;
  duplicate_score?: number | null;
  priority: string;
}

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

export interface ClusterDetail {
  id: string;
  title: string;
  description: string;
  theme: string;
  category: string;
  status: ClusterStatus;
  department?: string | null;
  village_name?: string | null;
  village_names: string[];
  coordinates?: {
    latitude: number;
    longitude: number;
    address?: string | null;
  } | null;
  complaint_ids: string[];
  complaint_count: number;
  representative_complaint_id?: string | null;
  average_severity?: string | null;
  latest_complaint_date?: string | null;
  average_confidence?: number | null;
  affected_area?: string | null;
  priority_score: number;
  hotspot_score: number;
  constituency: string;
  district: string;
  state: string;
  priority_analysis?: ClusterPriorityAnalysis | null;
  impact_score?: number | null;
  urgency_level?: string | null;
  priority_rank?: number | null;
  recommended_department?: string | null;
  recommended_action?: string | null;
  estimated_budget?: string | null;
  estimated_resolution_time?: string | null;
  affected_population?: string | null;
  priority_reasoning?: string | null;
  priority_confidence?: number | null;
  priority_updated_at?: string | null;
  related_complaints: ClusterComplaintSummary[];
}

export interface ClusterListResponse {
  success: boolean;
  items: ClusterListItem[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ClusterDashboardSummary {
  success: boolean;
  total_clusters: number;
  open_clusters: number;
  total_clustered_complaints: number;
  average_cluster_size: number;
  top_hotspots: ClusterListItem[];
}

export interface ClusterProcessResponse {
  success: boolean;
  message: string;
  complaint_id: string;
  cluster_id?: string | null;
  is_duplicate: boolean;
  duplicate_score?: number | null;
}
