import { apiClient } from "@/lib/api-client";
import type { AnalyticsIntelligenceResponse } from "@/features/analytics-intelligence/types/analytics";

export const analyticsIntelligenceApi = {
  getIntelligence: () => apiClient<AnalyticsIntelligenceResponse>("/analytics/intelligence"),
};
