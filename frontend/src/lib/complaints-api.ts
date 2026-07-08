import { apiClient } from "@/lib/api-client";
import type {
  CategoryListResponse,
  ComplaintCreateResponse,
  ComplaintDetail,
  ComplaintListResponse,
  ComplaintSubmitPayload,
} from "@/types/complaint";

export interface ListComplaintsParams {
  page?: number;
  page_size?: number;
  search?: string;
  category_id?: string;
  status?: string;
}

export const categoriesApi = {
  list: () => apiClient<CategoryListResponse>("/categories"),
};

export const complaintsApi = {
  list: (params?: ListComplaintsParams) =>
    apiClient<ComplaintListResponse>("/complaints", {
      params: params as Record<string, string | number | boolean | undefined>,
    }),

  get: (id: string) => apiClient<ComplaintDetail>(`/complaints/${id}`),

  create: (payload: ComplaintSubmitPayload) =>
    apiClient<ComplaintCreateResponse>("/complaints", {
      method: "POST",
      body: payload,
    }),

  update: (
    id: string,
    payload: Partial<{
      title: string;
      description: string;
      category_id: string;
      latitude: number;
      longitude: number;
      address: string;
      landmark: string;
      status: string;
    }>,
  ) =>
    apiClient<ComplaintDetail>(`/complaints/${id}`, {
      method: "PUT",
      body: payload,
    }),

  delete: (id: string) =>
    apiClient<{ success: boolean }>(`/complaints/${id}`, { method: "DELETE" }),

  analyze: (id: string, force = false) =>
    apiClient<ComplaintAnalyzeResponse>(`/complaints/${id}/analyze`, {
      method: "POST",
      params: { force },
    }),

  analyzeImage: (id: string, force = false) =>
    apiClient<ComplaintImageAnalyzeResponse>(`/complaints/${id}/analyze-image`, {
      method: "POST",
      params: { force },
    }),
};

export interface ComplaintAnalyzeResponse {
  success: boolean;
  message: string;
  complaint: ComplaintDetail;
}

export interface ComplaintImageAnalyzeResponse {
  success: boolean;
  message: string;
  complaint: ComplaintDetail;
}
