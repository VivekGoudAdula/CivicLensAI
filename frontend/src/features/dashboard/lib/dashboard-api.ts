import { apiClient } from "@/lib/api-client";
import type {
  DashboardActivitiesResponse,
  DashboardAnalyticsResponse,
  DashboardHomeResponse,
} from "@/features/dashboard/types/dashboard";

export const dashboardApi = {
  getHome: () => apiClient<DashboardHomeResponse>("/analytics/dashboard"),
  getActivities: (limit = 100) =>
    apiClient<DashboardActivitiesResponse>("/analytics/activities", {
      params: { limit },
    }),
  getAnalytics: () => apiClient<DashboardAnalyticsResponse>("/analytics/overview"),
};
