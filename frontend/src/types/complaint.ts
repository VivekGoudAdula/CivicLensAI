export type AnalysisStatus = "pending" | "processing" | "completed" | "failed";

export type SentimentLabel = "positive" | "neutral" | "negative" | "mixed";

export interface ComplaintImageAnalysis {
  primary_issue: string;
  secondary_issue?: string | null;
  description: string;
  severity: string;
  confidence_score: number;
  visible_damage: string;
  estimated_area_affected: string;
  safety_risk: string;
  suggested_department: string;
  suggested_immediate_action: string;
  suggested_long_term_action: string;
  possible_public_impact: string;
  duplicate_indicators: string[];
  detected_objects: string[];
  environmental_risk: string;
  road_safety_risk: string;
  human_presence: boolean;
  vehicles_present: boolean;
  requires_urgent_attention: boolean;
  reasoning: string;
  processed_at: string;
  model_version: string;
  prompt_version: string;
}

export interface ComplaintAIAnalysis {
  category: string;
  sub_category: string;
  responsible_department: string;
  urgency: string;
  severity: string;
  priority_level: string;
  summary: string;
  detailed_explanation: string;
  keywords: string[];
  affected_infrastructure: string;
  affected_citizens_estimate?: string | null;
  government_scheme?: string | null;
  suggested_immediate_action: string;
  suggested_long_term_action: string;
  required_department: string;
  required_team: string;
  confidence_score: number;
  reasoning: string;
  duplicate_possibility: number;
  tags: string[];
  language_detected: string;
  translated_english?: string | null;
  voice_transcript?: string | null;
  sentiment: SentimentLabel;
  urgency_score: number;
  language: string;
  processed_at: string;
  model_version: string;
  prompt_version: string;
}

export type ComplaintStatus =
  | "pending"
  | "submitted"
  | "under_review"
  | "clustered"
  | "in_progress"
  | "resolved"
  | "rejected"
  | "closed";

export type ComplaintPriority = "low" | "medium" | "high" | "critical";

export interface GeoLocation {
  latitude: number;
  longitude: number;
  address?: string | null;
}

export interface DocumentMetadata {
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
  version: number;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  icon?: string | null;
  display_order: number;
  is_active: boolean;
  metadata: DocumentMetadata;
}

export interface ComplaintMediaPayload {
  data: string;
  mime_type: string;
  file_name?: string;
}

export interface ComplaintSubmitPayload {
  title: string;
  description: string;
  category_id: string;
  latitude: number;
  longitude: number;
  address: string;
  landmark?: string;
  image?: ComplaintMediaPayload;
  audio?: ComplaintMediaPayload;
  audio_duration_seconds?: number;
  contact_name?: string;
  mobile_number: string;
  is_anonymous: boolean;
}

export interface ComplaintListItem {
  id: string;
  title: string;
  description: string;
  category_id: string;
  category_name: string;
  category_slug: string;
  status: ComplaintStatus;
  priority: ComplaintPriority;
  address?: string | null;
  landmark?: string | null;
  is_anonymous: boolean;
  citizen_name?: string | null;
  citizen_phone?: string | null;
  has_image: boolean;
  has_audio: boolean;
  submitted_at: string;
  constituency: string;
  analysis_status?: AnalysisStatus | null;
  has_ai_analysis?: boolean;
  cluster_id?: string | null;
  is_duplicate?: boolean;
  duplicate_score?: number | null;
}

export interface ComplaintDetail {
  id: string;
  title: string;
  description: string;
  category_id: string;
  category_name: string;
  category_slug: string;
  status: ComplaintStatus;
  priority: ComplaintPriority;
  location?: GeoLocation | null;
  landmark?: string | null;
  image_base64?: string | null;
  image_mime_type?: string | null;
  audio_base64?: string | null;
  audio_mime_type?: string | null;
  audio_duration_seconds?: number | null;
  is_anonymous: boolean;
  citizen_name?: string | null;
  citizen_phone?: string | null;
  constituency: string;
  district: string;
  state: string;
  village_name: string;
  submitted_at: string;
  resolved_at?: string | null;
  metadata: DocumentMetadata;
  ai_analysis?: ComplaintAIAnalysis | null;
  analysis_status: AnalysisStatus;
  analysis_started_at?: string | null;
  analysis_completed_at?: string | null;
  analysis_model_name?: string | null;
  analysis_processing_time_ms?: number | null;
  analysis_prompt_version?: string | null;
  analysis_error_message?: string | null;
  analysis_retry_count: number;
  image_analysis?: ComplaintImageAnalysis | null;
  image_analysis_status?: AnalysisStatus | null;
  vision_model?: string | null;
  vision_processing_time_ms?: number | null;
  vision_completed_at?: string | null;
  vision_started_at?: string | null;
  vision_prompt_version?: string | null;
  vision_error_message?: string | null;
  vision_retry_count: number;
  cluster_id?: string | null;
  is_duplicate?: boolean;
  duplicate_score?: number | null;
  duplicate_reason?: string | null;
  duplicate_confidence?: number | null;
  matched_complaint_id?: string | null;
  matched_cluster_id?: string | null;
}

export interface ComplaintListResponse {
  success: boolean;
  items: ComplaintListItem[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ComplaintCreateResponse {
  success: boolean;
  message: string;
  complaint: ComplaintDetail;
}

export interface CategoryListResponse {
  success: boolean;
  items: Category[];
}
