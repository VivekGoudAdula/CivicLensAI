import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  complaintsApi,
  type ListComplaintsParams,
} from "@/lib/complaints-api";
import type { ComplaintSubmitPayload } from "@/types/complaint";

export function useComplaints(params: ListComplaintsParams) {
  return useQuery({
    queryKey: ["complaints", params],
    queryFn: () => complaintsApi.list(params),
  });
}

export function useComplaint(id: string | undefined) {
  return useQuery({
    queryKey: ["complaint", id],
    queryFn: () => complaintsApi.get(id!),
    enabled: Boolean(id),
  });
}

export function useCreateComplaint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ComplaintSubmitPayload) =>
      complaintsApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
    },
  });
}

export function useDeleteComplaint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => complaintsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
    },
  });
}

export function useAnalyzeComplaint() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, force = false }: { id: string; force?: boolean }) =>
      complaintsApi.analyze(id, force),
    onSuccess: (response) => {
      queryClient.setQueryData(["complaint", response.complaint.id], response.complaint);
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
    },
  });
}

export function useAnalyzeComplaintImage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, force = false }: { id: string; force?: boolean }) =>
      complaintsApi.analyzeImage(id, force),
    onSuccess: (response) => {
      queryClient.setQueryData(["complaint", response.complaint.id], response.complaint);
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
    },
  });
}
