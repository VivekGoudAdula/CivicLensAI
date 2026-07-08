import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { DashboardFilters } from "@/features/dashboard/types/dashboard";

interface DashboardFiltersContextValue {
  filters: DashboardFilters;
  setFilter: <K extends keyof DashboardFilters>(key: K, value: DashboardFilters[K]) => void;
  resetFilters: () => void;
  hasActiveFilters: boolean;
}

const DashboardFiltersContext = createContext<DashboardFiltersContextValue | null>(null);

const DEFAULT_FILTERS: DashboardFilters = {};

export function DashboardFiltersProvider({ children }: { children: ReactNode }) {
  const [filters, setFilters] = useState<DashboardFilters>(DEFAULT_FILTERS);

  const setFilter = useCallback(
    <K extends keyof DashboardFilters>(key: K, value: DashboardFilters[K]) => {
      setFilters((current) => ({ ...current, [key]: value }));
    },
    [],
  );

  const resetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  const hasActiveFilters = useMemo(
    () =>
      Object.values(filters).some(
        (value) => value !== undefined && value !== "" && value !== null,
      ),
    [filters],
  );

  const value = useMemo(
    () => ({ filters, setFilter, resetFilters, hasActiveFilters }),
    [filters, setFilter, resetFilters, hasActiveFilters],
  );

  return (
    <DashboardFiltersContext.Provider value={value}>
      {children}
    </DashboardFiltersContext.Provider>
  );
}

export function useDashboardFilters() {
  const context = useContext(DashboardFiltersContext);
  if (!context) {
    throw new Error("useDashboardFilters must be used within DashboardFiltersProvider");
  }
  return context;
}
