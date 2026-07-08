import { useQuery, useQueryClient } from "@tanstack/react-query";

import { gisApi } from "@/features/gis/lib/gis-api";

export const gisQueryKeys = {
  map: ["gis", "map"] as const,
};

export function useGisMap() {
  return useQuery({
    queryKey: gisQueryKeys.map,
    queryFn: () => gisApi.getMap(),
    staleTime: 30_000,
  });
}

export function useInvalidateGis() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: ["gis"] });
    void queryClient.invalidateQueries({ queryKey: ["analytics-intelligence"] });
    void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };
}
