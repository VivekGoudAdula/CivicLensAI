import { RotateCcw, SlidersHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AnalyticsFilters } from "@/features/analytics-intelligence/types/analytics";

interface AnalyticsFiltersBarProps {
  filters: AnalyticsFilters;
  onChange: (filters: AnalyticsFilters) => void;
  onReset: () => void;
}

export function AnalyticsFiltersBar({ filters, onChange, onReset }: AnalyticsFiltersBarProps) {
  const set = <K extends keyof AnalyticsFilters>(key: K, value: AnalyticsFilters[K]) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="flex flex-col gap-3 rounded-xl border bg-muted/20 p-4">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <SlidersHorizontal className="h-4 w-4" />
        Global Analytics Filters
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8">
        <Input
          type="date"
          value={filters.dateFrom ?? ""}
          onChange={(e) => set("dateFrom", e.target.value || undefined)}
        />
        <Input
          type="date"
          value={filters.dateTo ?? ""}
          onChange={(e) => set("dateTo", e.target.value || undefined)}
        />
        <Input
          placeholder="Village"
          value={filters.village ?? ""}
          onChange={(e) => set("village", e.target.value || undefined)}
        />
        <Input
          placeholder="Department"
          value={filters.department ?? ""}
          onChange={(e) => set("department", e.target.value || undefined)}
        />
        <Input
          placeholder="Category"
          value={filters.category ?? ""}
          onChange={(e) => set("category", e.target.value || undefined)}
        />
        <Select
          value={filters.priority ?? "all"}
          onValueChange={(v) => set("priority", v === "all" ? undefined : v)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            {["all", "critical", "high", "medium", "low"].map((p) => (
              <SelectItem key={p} value={p}>
                {p === "all" ? "All" : p}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={filters.status ?? "all"}
          onValueChange={(v) => set("status", v === "all" ? undefined : v)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {["all", "pending", "submitted", "in_progress", "resolved", "closed"].map((s) => (
              <SelectItem key={s} value={s}>
                {s === "all" ? "All" : s.replace(/_/g, " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button variant="outline" size="icon" onClick={onReset} aria-label="Reset filters">
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
