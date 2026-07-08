import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Filter, RotateCcw, Search } from "lucide-react";

import { NoInternetEmptyState } from "@/components/empty-states/no-internet";
import { PageHeader } from "@/components/layout/PageHeader";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { QuickFilters, SavedFiltersPanel } from "@/features/search/components/saved-filters-panel";
import { RecentSearches, SearchResultsList } from "@/features/search/components/search-results-list";
import { useDebouncedValue, useRecentSearches } from "@/features/search/hooks/use-search-storage";
import { useGlobalSearch } from "@/features/search/hooks/use-global-search";
import type { GlobalSearchFilters, SavedFilterPreset, SearchSortOption } from "@/features/search/types/search";

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get("q") ?? "";
  const [query, setQuery] = useState(initialQuery);
  const [sort, setSort] = useState<SearchSortOption>("newest");
  const [filters, setFilters] = useState<GlobalSearchFilters>({});
  const [offline, setOffline] = useState(!navigator.onLine);
  const debouncedQuery = useDebouncedValue(query, 300);
  const { recent, addRecent, clearRecent } = useRecentSearches();

  useEffect(() => {
    const handleOnline = () => setOffline(false);
    const handleOffline = () => setOffline(true);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const { data, isLoading, isFetching, refetch } = useGlobalSearch(debouncedQuery, {
    sort,
    filters,
    enabled: !offline,
  });

  const showResults = debouncedQuery.length >= 2;
  const resultCount = useMemo(() => data?.total ?? 0, [data?.total]);

  const handleSearch = (value: string) => {
    setQuery(value);
    if (value.trim().length >= 2) {
      setSearchParams({ q: value.trim() });
      addRecent(value.trim());
    }
  };

  const applyPreset = (preset: SavedFilterPreset) => {
    setQuery(preset.query);
    setFilters(preset.filters);
    setSort(preset.sort);
    if (preset.query.trim().length >= 2) {
      setSearchParams({ q: preset.query.trim() });
    }
  };

  if (offline) {
    return (
      <div className="space-y-6">
        <PageHeader title="Global Search" description="Enterprise search across CivicLens AI" />
        <NoInternetEmptyState onRetry={() => window.location.reload()} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Global Search"
        description="Search complaints, clusters, recommendations, villages, departments, and AI summaries"
      />

      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder="Search the entire platform..."
          value={query}
          onChange={(event) => handleSearch(event.target.value)}
          aria-label="Global search query"
        />
      </div>

      <QuickFilters onApply={(next) => setFilters((current) => ({ ...current, ...next }))} />

      <SavedFiltersPanel query={query} filters={filters} sort={sort} onApply={applyPreset} />

      <div className="flex flex-col gap-3 rounded-xl border bg-muted/20 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Filter className="h-4 w-4" />
          Advanced Filters
        </div>
        <div className="grid flex-1 gap-2 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6">
          <Input
            placeholder="Village"
            value={filters.village ?? ""}
            onChange={(e) => setFilters({ ...filters, village: e.target.value || undefined })}
          />
          <Input
            placeholder="Department"
            value={filters.department ?? ""}
            onChange={(e) => setFilters({ ...filters, department: e.target.value || undefined })}
          />
          <Input
            placeholder="Category"
            value={filters.category ?? ""}
            onChange={(e) => setFilters({ ...filters, category: e.target.value || undefined })}
          />
          <Input
            placeholder="Priority"
            value={filters.priority ?? ""}
            onChange={(e) => setFilters({ ...filters, priority: e.target.value || undefined })}
          />
          <Input
            placeholder="Severity"
            value={filters.severity ?? ""}
            onChange={(e) => setFilters({ ...filters, severity: e.target.value || undefined })}
          />
          <Input
            placeholder="Status"
            value={filters.status ?? ""}
            onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined })}
          />
          <Input
            type="date"
            aria-label="Date from"
            value={filters.date_from ?? ""}
            onChange={(e) => setFilters({ ...filters, date_from: e.target.value || undefined })}
          />
          <Input
            type="date"
            aria-label="Date to"
            value={filters.date_to ?? ""}
            onChange={(e) => setFilters({ ...filters, date_to: e.target.value || undefined })}
          />
          <Select value={sort} onValueChange={(v) => setSort(v as SearchSortOption)}>
            <SelectTrigger>
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest</SelectItem>
              <SelectItem value="oldest">Oldest</SelectItem>
              <SelectItem value="highest_priority">Highest Priority</SelectItem>
              <SelectItem value="highest_severity">Highest Severity</SelectItem>
              <SelectItem value="most_complaints">Most Complaints</SelectItem>
              <SelectItem value="alphabetical">Alphabetical</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button variant="outline" size="icon" onClick={() => setFilters({})} aria-label="Clear filters">
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      {!showResults ? (
        <RecentSearches items={recent} onSelect={handleSearch} onClear={clearRecent} />
      ) : (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            {resultCount} results {data ? `in ${data.took_ms}ms` : ""}
            {isFetching && !isLoading ? " · updating..." : ""}
          </p>
          {data?.suggestions.length ? (
            <div className="flex flex-wrap gap-2">
              {data.suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  className="rounded-full border px-2.5 py-0.5 text-xs hover:bg-muted"
                  onClick={() => handleSearch(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          ) : null}
          <SearchResultsList items={data?.items ?? []} query={debouncedQuery} isLoading={isLoading} />
          {!isLoading && data?.items.length === 0 ? (
            <Button variant="outline" onClick={() => void refetch()}>
              Retry Search
            </Button>
          ) : null}
        </div>
      )}
    </div>
  );
}
