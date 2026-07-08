import { apiClient } from "@/lib/api-client";
import type {
  PriorityAnalyzeResponse,
  PriorityDashboard,
  PriorityRerankResponse,
} from "@/types/priority";

export const priorityApi = {
  dashboard: () => apiClient<PriorityDashboard>("/priority/dashboard"),

  analyzeCluster: (clusterId: string, force = false) =>
    apiClient<PriorityAnalyzeResponse>(`/priority/analyze/${clusterId}`, {
      method: "POST",
      params: { force },
    }),

  rerankAll: (force = false) =>
    apiClient<PriorityRerankResponse>("/priority/rerank", {
      method: "POST",
      params: { force },
    }),
};
