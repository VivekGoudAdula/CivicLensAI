import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { clustersApi, type ListClustersParams } from "@/lib/clusters-api";

export function useClusters(params: ListClustersParams) {
  return useQuery({
    queryKey: ["clusters", params],
    queryFn: () => clustersApi.list(params),
  });
}

export function useCluster(id: string | undefined) {
  return useQuery({
    queryKey: ["cluster", id],
    queryFn: () => clustersApi.get(id!),
    enabled: Boolean(id),
  });
}

export function useClusterDashboard() {
  return useQuery({
    queryKey: ["cluster-dashboard"],
    queryFn: () => clustersApi.dashboard(),
  });
}

export function useProcessComplaintClustering() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ complaintId, force = false }: { complaintId: string; force?: boolean }) =>
      clustersApi.processComplaint(complaintId, force),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clusters"] });
      queryClient.invalidateQueries({ queryKey: ["cluster-dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
      queryClient.invalidateQueries({ queryKey: ["complaint"] });
    },
  });
}
