import { RotateCcw, Search, SlidersHorizontal } from "lucide-react";

import { useDashboardFilters } from "@/features/dashboard/context/dashboard-filters-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const STATUS_OPTIONS = [
  "all",
  "pending",
  "submitted",
  "under_review",
  "clustered",
  "in_progress",
  "resolved",
  "rejected",
  "closed",
];

const PRIORITY_OPTIONS = ["all", "low", "medium", "high", "critical"];
const SEVERITY_OPTIONS = ["all", "Low", "Medium", "High", "Critical"];

export function DashboardFiltersBar() {
  const { filters, setFilter, resetFilters, hasActiveFilters } = useDashboardFilters();

  return (
    <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <SlidersHorizontal className="h-4 w-4" />
        Global Filters
      </div>

      <div className="grid flex-1 gap-2 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8">
        <Input
          type="date"
          value={filters.dateFrom ?? ""}
          onChange={(event) => setFilter("dateFrom", event.target.value || undefined)}
          aria-label="Date from"
        />
        <Input
          type="date"
          value={filters.dateTo ?? ""}
          onChange={(event) => setFilter("dateTo", event.target.value || undefined)}
          aria-label="Date to"
        />
        <Input
          placeholder="Village"
          value={filters.village ?? ""}
          onChange={(event) => setFilter("village", event.target.value || undefined)}
        />
        <Input
          placeholder="Department"
          value={filters.department ?? ""}
          onChange={(event) => setFilter("department", event.target.value || undefined)}
        />
        <Input
          placeholder="Category"
          value={filters.category ?? ""}
          onChange={(event) => setFilter("category", event.target.value || undefined)}
        />
        <Select
          value={filters.priority ?? "all"}
          onValueChange={(value) =>
            setFilter("priority", value === "all" ? undefined : value)
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            {PRIORITY_OPTIONS.map((option) => (
              <SelectItem key={option} value={option}>
                {option === "all" ? "All Priorities" : option}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={filters.severity ?? "all"}
          onValueChange={(value) =>
            setFilter("severity", value === "all" ? undefined : value)
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent>
            {SEVERITY_OPTIONS.map((option) => (
              <SelectItem key={option} value={option}>
                {option === "all" ? "All Severities" : option}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={filters.status ?? "all"}
          onValueChange={(value) =>
            setFilter("status", value === "all" ? undefined : value)
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((option) => (
              <SelectItem key={option} value={option}>
                {option === "all" ? "All Statuses" : option.replace(/_/g, " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center gap-2">
        <div className="relative min-w-[200px] flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Search..."
            value={filters.search ?? ""}
            onChange={(event) => setFilter("search", event.target.value || undefined)}
          />
        </div>
        {hasActiveFilters ? (
          <Button variant="outline" size="icon" onClick={resetFilters} aria-label="Reset filters">
            <RotateCcw className="h-4 w-4" />
          </Button>
        ) : null}
      </div>
    </div>
  );
}
