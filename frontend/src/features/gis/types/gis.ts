export interface GisBounds {
  south: number;
  west: number;
  north: number;
  east: number;
  center_lat: number;
  center_lng: number;
}

export interface GisComplaintPin {
  id: string;
  title: string;
  description: string;
  latitude: number;
  longitude: number;
  category: string;
  department: string;
  priority: string;
  severity?: string | null;
  status: string;
  village_name: string;
  cluster_id?: string | null;
  cluster_title?: string | null;
  ai_summary?: string | null;
  ai_confidence?: number | null;
  has_image: boolean;
  address?: string | null;
  submitted_at: string;
  heat_weight: number;
}

export interface GisClusterMarker {
  id: string;
  title: string;
  latitude: number;
  longitude: number;
  complaint_count: number;
  average_priority: number;
  highest_severity?: string | null;
  representative_complaint_id?: string | null;
  cluster_score: number;
  department?: string | null;
  village_name?: string | null;
  hotspot_score: number;
  heat_weight: number;
}

export interface GisMapResponse {
  success: boolean;
  complaints: GisComplaintPin[];
  clusters: GisClusterMarker[];
  bounds?: GisBounds | null;
  total_complaints: number;
  total_clusters: number;
  last_updated_at: string;
}

export interface GisFilters {
  dateFrom?: string;
  dateTo?: string;
  village?: string;
  department?: string;
  category?: string;
  priority?: string;
  severity?: string;
  status?: string;
  cluster?: string;
  aiConfidenceMin?: number;
  search?: string;
}

export interface GisLayerState {
  showComplaints: boolean;
  showClusters: boolean;
  showHeatmap: boolean;
  colorMode: "priority" | "severity" | "department";
}
