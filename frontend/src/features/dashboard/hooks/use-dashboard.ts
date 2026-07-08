import { useQuery, useQueryClient } from "@tanstack/react-query";

import { dashboardApi } from "@/features/dashboard/lib/dashboard-api";

export const dashboardQueryKeys = {
  home: ["dashboard", "home"] as const,
  activities: (limit: number) => ["dashboard", "activities", limit] as const,
  analytics: ["dashboard", "analytics"] as const,
};

export function useDashboardHome() {
  return useQuery({
    queryKey: dashboardQueryKeys.home,
    queryFn: () => dashboardApi.getHome(),
    staleTime: 30_000,
  });
}

export function useDashboardActivities(limit = 100) {
  return useQuery({
    queryKey: dashboardQueryKeys.activities(limit),
    queryFn: () => dashboardApi.getActivities(limit),
    staleTime: 30_000,
  });
}

export function useDashboardAnalytics() {
  return useQuery({
    queryKey: dashboardQueryKeys.analytics,
    queryFn: () => dashboardApi.getAnalytics(),
    staleTime: 60_000,
  });
}

export function useInvalidateDashboard() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    void queryClient.invalidateQueries({ queryKey: ["complaints"] });
    void queryClient.invalidateQueries({ queryKey: ["clusters"] });
    void queryClient.invalidateQueries({ queryKey: ["priority"] });
  };
}
