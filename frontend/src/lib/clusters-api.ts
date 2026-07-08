import { apiClient } from "@/lib/api-client";
import type {
  ClusterDashboardSummary,
  ClusterDetail,
  ClusterListResponse,
  ClusterProcessResponse,
} from "@/types/cluster";

export interface ListClustersParams {
  page?: number;
  page_size?: number;
  search?: string;
  category?: string;
  status?: string;
}

export const clustersApi = {
  list: (params?: ListClustersParams) =>
    apiClient<ClusterListResponse>("/clusters", {
      params: params as Record<string, string | number | boolean | undefined>,
    }),

  get: (id: string) => apiClient<ClusterDetail>(`/clusters/${id}`),

  dashboard: () => apiClient<ClusterDashboardSummary>("/clusters/dashboard"),

  processComplaint: (complaintId: string, force = false) =>
    apiClient<ClusterProcessResponse>(`/clusters/process/${complaintId}`, {
      method: "POST",
      params: { force },
    }),
};
