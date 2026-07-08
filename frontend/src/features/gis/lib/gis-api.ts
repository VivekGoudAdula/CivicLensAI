import { apiClient } from "@/lib/api-client";
import type { GisMapResponse } from "@/features/gis/types/gis";

export const gisApi = {
  getMap: () => apiClient<GisMapResponse>("/gis/map"),
};
