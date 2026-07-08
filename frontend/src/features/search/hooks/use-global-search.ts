import { useQuery } from "@tanstack/react-query";

import { searchApi } from "@/features/search/lib/search-api";
import type { GlobalSearchFilters, SearchSortOption } from "@/features/search/types/search";

export function useGlobalSearch(
  query: string,
  options?: {
    sort?: SearchSortOption;
    filters?: GlobalSearchFilters;
    enabled?: boolean;
  },
) {
  const trimmed = query.trim();
  return useQuery({
    queryKey: ["global-search", trimmed, options?.sort, options?.filters],
    queryFn: () =>
      searchApi.search(trimmed, {
        sort: options?.sort ?? "newest",
        limit: 50,
        filters: options?.filters,
      }),
    enabled: (options?.enabled ?? true) && trimmed.length >= 2,
    staleTime: 15_000,
  });
}
