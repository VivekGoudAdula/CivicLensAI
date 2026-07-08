import { useQuery } from "@tanstack/react-query";

import { categoriesApi } from "@/lib/complaints-api";

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: categoriesApi.list,
    staleTime: 5 * 60 * 1000,
  });
}
