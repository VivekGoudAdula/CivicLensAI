import { Bookmark, BookmarkPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { GlobalSearchFilters, SavedFilterPreset, SearchSortOption } from "@/features/search/types/search";
import { useSavedFilters } from "@/features/search/hooks/use-search-storage";

interface SavedFiltersPanelProps {
  query: string;
  filters: GlobalSearchFilters;
  sort: SearchSortOption;
  onApply: (preset: SavedFilterPreset) => void;
}

export function SavedFiltersPanel({ query, filters, sort, onApply }: SavedFiltersPanelProps) {
  const { saved, persist } = useSavedFilters() as {
    saved: SavedFilterPreset[];
    persist: (items: SavedFilterPreset[]) => void;
  };

  const handleSave = () => {
    const name = window.prompt("Name this filter preset:");
    if (!name?.trim()) return;
    const preset: SavedFilterPreset = {
      id: crypto.randomUUID(),
      name: name.trim(),
      query,
      filters,
      sort,
    };
    persist([preset, ...saved].slice(0, 12));
  };

  const handleRemove = (id: string) => {
    persist(saved.filter((item) => item.id !== id));
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Bookmark className="h-4 w-4" />
          Saved Filters
        </p>
        <Button variant="ghost" size="sm" onClick={handleSave}>
          <BookmarkPlus className="h-4 w-4" />
          Save Current
        </Button>
      </div>
      {saved.length === 0 ? (
        <p className="text-xs text-muted-foreground">No saved filters yet.</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {saved.map((preset) => (
            <div key={preset.id} className="flex items-center gap-1 rounded-full border pl-3 pr-1">
              <button
                type="button"
                className="py-1 text-xs hover:text-primary"
                onClick={() => onApply(preset)}
              >
                {preset.name}
              </button>
              <button
                type="button"
                className="rounded-full px-2 py-1 text-xs text-muted-foreground hover:text-destructive"
                onClick={() => handleRemove(preset.id)}
                aria-label={`Remove ${preset.name}`}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface QuickFiltersProps {
  onApply: (filters: GlobalSearchFilters) => void;
}

const QUICK_FILTERS: { label: string; filters: GlobalSearchFilters }[] = [
  { label: "High Priority", filters: { priority: "high" } },
  { label: "Critical Severity", filters: { severity: "critical" } },
  { label: "Pending", filters: { resolved: false } },
  { label: "Resolved", filters: { resolved: true } },
];

export function QuickFilters({ onApply }: QuickFiltersProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {QUICK_FILTERS.map((item) => (
        <button
          key={item.label}
          type="button"
          className="rounded-full border px-3 py-1 text-xs transition-colors hover:bg-muted"
          onClick={() => onApply(item.filters)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
