import type {
  GisClusterMarker,
  GisComplaintPin,
  GisFilters,
  GisMapResponse,
} from "@/features/gis/types/gis";

export interface GisFilterable {
  category?: string;
  department?: string;
  village_name?: string;
  priority?: string;
  severity?: string | null;
  status?: string;
  cluster_id?: string | null;
  submitted_at?: string;
  ai_confidence?: number | null;
}

function matchesGisFilters(item: GisFilterable, filters: GisFilters): boolean {
  if (filters.search) {
    const haystack = JSON.stringify(item).toLowerCase();
    if (!haystack.includes(filters.search.toLowerCase())) return false;
  }
  if (filters.category && !(item.category ?? "").toLowerCase().includes(filters.category.toLowerCase())) {
    return false;
  }
  if (filters.department && !(item.department ?? "").toLowerCase().includes(filters.department.toLowerCase())) {
    return false;
  }
  if (filters.village && !(item.village_name ?? "").toLowerCase().includes(filters.village.toLowerCase())) {
    return false;
  }
  if (filters.priority && item.priority?.toLowerCase() !== filters.priority.toLowerCase()) {
    return false;
  }
  if (filters.severity && (item.severity ?? "").toLowerCase() !== filters.severity.toLowerCase()) {
    return false;
  }
  if (filters.status && item.status?.toLowerCase() !== filters.status.toLowerCase()) {
    return false;
  }
  if (filters.cluster && item.cluster_id !== filters.cluster) {
    return false;
  }
  if (filters.dateFrom && item.submitted_at) {
    if (new Date(item.submitted_at) < new Date(filters.dateFrom)) return false;
  }
  if (filters.dateTo && item.submitted_at) {
    const to = new Date(filters.dateTo);
    to.setHours(23, 59, 59, 999);
    if (new Date(item.submitted_at) > to) return false;
  }
  if (filters.aiConfidenceMin != null && item.ai_confidence != null) {
    if (item.ai_confidence < filters.aiConfidenceMin) return false;
  }
  return true;
}

export function filterGisData(
  data: GisMapResponse,
  filters: GisFilters,
): { complaints: GisComplaintPin[]; clusters: GisClusterMarker[] } {
  const complaints = data.complaints.filter((pin) =>
    matchesGisFilters(
      {
        category: pin.category,
        department: pin.department,
        village_name: pin.village_name,
        priority: pin.priority,
        severity: pin.severity,
        status: pin.status,
        cluster_id: pin.cluster_id,
        submitted_at: pin.submitted_at,
        ai_confidence: pin.ai_confidence,
      },
      filters,
    ),
  );

  const visibleClusterIds = new Set(complaints.map((c) => c.cluster_id).filter(Boolean));
  const clusters = data.clusters.filter((cluster) => {
    if (filters.cluster && cluster.id !== filters.cluster) return false;
    if (filters.village && !(cluster.village_name ?? "").toLowerCase().includes(filters.village.toLowerCase())) {
      return false;
    }
    if (filters.department && !(cluster.department ?? "").toLowerCase().includes(filters.department.toLowerCase())) {
      return false;
    }
    if (complaints.length > 0 && !visibleClusterIds.has(cluster.id) && filters.cluster) {
      return false;
    }
    return true;
  });

  return { complaints, clusters };
}
