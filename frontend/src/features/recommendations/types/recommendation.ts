export interface MpDevelopmentWorkItem {
  priority_rank: number;
  project_title: string;
  category: string;
  village: string;
  department: string;
  reason: string;
  impact_score: number;
  priority_score: number;
  urgency: string;
  estimated_beneficiaries: string;
  estimated_budget: string;
  estimated_resolution_time: string;
  government_scheme?: string | null;
  expected_social_impact: string;
  expected_infrastructure_improvement: string;
  ai_confidence: number;
  risk_if_ignored: string;
  executive_summary: string;
  detailed_explanation: string;
  recommended_action: string;
  cluster_id?: string | null;
}

export interface RecommendationCenter {
  success: boolean;
  executive_brief: string;
  decision_timeline_summary: string;
  recommendations: MpDevelopmentWorkItem[];
  total_recommendations: number;
  engine: string;
  model_version: string;
  prompt_version: string;
  context_hash: string;
  generated_at: string;
  from_cache?: boolean;
}

export interface RecommendationGenerateResponse {
  success: boolean;
  message: string;
  center?: RecommendationCenter | null;
}

export interface RecommendationListResponse {
  success: boolean;
  items: MpDevelopmentWorkItem[];
  total: number;
}
