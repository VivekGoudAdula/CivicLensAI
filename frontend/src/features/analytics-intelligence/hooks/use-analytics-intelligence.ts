import { useQuery } from "@tanstack/react-query";

import { analyticsIntelligenceApi } from "@/features/analytics-intelligence/lib/analytics-api";

export const analyticsIntelligenceKeys = {
  intelligence: ["analytics-intelligence"] as const,
};

export function useAnalyticsIntelligence() {
  return useQuery({
    queryKey: analyticsIntelligenceKeys.intelligence,
    queryFn: () => analyticsIntelligenceApi.getIntelligence(),
    staleTime: 60_000,
  });
}
