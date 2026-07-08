import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { priorityApi } from "@/lib/priority-api";

export function usePriorityDashboard() {
  return useQuery({
    queryKey: ["priority-dashboard"],
    queryFn: () => priorityApi.dashboard(),
  });
}

export function useAnalyzeClusterPriority() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ clusterId, force = false }: { clusterId: string; force?: boolean }) =>
      priorityApi.analyzeCluster(clusterId, force),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["priority-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["clusters"] });
      queryClient.invalidateQueries({ queryKey: ["cluster"] });
    },
  });
}

export function useRerankPriorities() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (force: boolean = false) => priorityApi.rerankAll(force),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["priority-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["clusters"] });
      queryClient.invalidateQueries({ queryKey: ["cluster-dashboard"] });
    },
  });
}
