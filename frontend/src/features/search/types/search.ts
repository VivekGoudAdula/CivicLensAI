export type SearchEntityType = "complaint" | "cluster" | "recommendation";
export type SearchSortOption =
  | "newest"
  | "oldest"
  | "highest_priority"
  | "highest_severity"
  | "most_complaints"
  | "alphabetical";

export interface GlobalSearchFilters {
  category?: string;
  department?: string;
  village?: string;
  priority?: string;
  severity?: string;
  status?: string;
  cluster_id?: string;
  date_from?: string;
  date_to?: string;
  ai_confidence_min?: number;
  recommendation_status?: string;
  urgency?: string;
  resolved?: boolean;
}

export interface GlobalSearchResultItem {
  id: string;
  type: SearchEntityType;
  title: string;
  subtitle: string;
  description: string;
  category?: string | null;
  department?: string | null;
  village?: string | null;
  priority?: string | null;
  severity?: string | null;
  status?: string | null;
  score: number;
  highlight?: string | null;
  url_path: string;
  occurred_at?: string | null;
}

export interface GlobalSearchResponse {
  success: boolean;
  query: string;
  items: GlobalSearchResultItem[];
  total: number;
  suggestions: string[];
  took_ms: number;
}

export interface SavedFilterPreset {
  id: string;
  name: string;
  query: string;
  filters: GlobalSearchFilters;
  sort: SearchSortOption;
}
