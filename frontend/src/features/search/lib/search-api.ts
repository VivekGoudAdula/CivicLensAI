import { apiClient } from "@/lib/api-client";
import type {
  GlobalSearchFilters,
  GlobalSearchResponse,
  SearchSortOption,
} from "@/features/search/types/search";

export const searchApi = {
  search: (
    query: string,
    options?: {
      sort?: SearchSortOption;
      limit?: number;
      filters?: GlobalSearchFilters;
    },
  ) =>
    apiClient<GlobalSearchResponse>("/search", {
      params: {
        q: query,
        sort: options?.sort,
        limit: options?.limit,
        ...options?.filters,
      },
    }),
};
