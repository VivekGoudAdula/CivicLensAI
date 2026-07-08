import { apiClient } from "@/lib/api-client";
import type {
  RecommendationCenter,
  RecommendationGenerateResponse,
  RecommendationListResponse,
} from "@/features/recommendations/types/recommendation";

export const recommendationApi = {
  getCenter: () => apiClient<RecommendationCenter>("/recommendations/center"),
  generate: (force = false) =>
    apiClient<RecommendationGenerateResponse>("/recommendations/generate", {
      method: "POST",
      params: { force },
    }),
  list: (limit = 50) =>
    apiClient<RecommendationListResponse>("/recommendations", { params: { limit } }),
};
