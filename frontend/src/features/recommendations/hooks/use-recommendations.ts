import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { recommendationApi } from "@/features/recommendations/lib/recommendation-api";

export const recommendationKeys = {
  center: ["recommendations", "center"] as const,
  list: ["recommendations", "list"] as const,
};

export function useRecommendationCenter() {
  return useQuery({
    queryKey: recommendationKeys.center,
    queryFn: () => recommendationApi.getCenter(),
    staleTime: 60_000,
  });
}

export function useGenerateRecommendations() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (force: boolean) => recommendationApi.generate(force),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });
}
