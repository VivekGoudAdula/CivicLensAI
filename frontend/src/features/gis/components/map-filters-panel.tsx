import { RotateCcw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { GisFilters } from "@/features/gis/types/gis";

interface MapFiltersPanelProps {
  filters: GisFilters;
  onChange: (filters: GisFilters) => void;
  onReset: () => void;
}

export function MapFiltersPanel({ filters, onChange, onReset }: MapFiltersPanelProps) {
  const set = <K extends keyof GisFilters>(key: K, value: GisFilters[K]) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="grid gap-2 rounded-xl border bg-background/95 p-3 shadow-lg backdrop-blur md:grid-cols-4 xl:grid-cols-6">
      <Input
        type="date"
        value={filters.dateFrom ?? ""}
        onChange={(e) => set("dateFrom", e.target.value || undefined)}
        aria-label="From date"
      />
      <Input
        type="date"
        value={filters.dateTo ?? ""}
        onChange={(e) => set("dateTo", e.target.value || undefined)}
        aria-label="To date"
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
              {p === "all" ? "All priorities" : p}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={filters.severity ?? "all"}
        onValueChange={(v) => set("severity", v === "all" ? undefined : v)}
      >
        <SelectTrigger>
          <SelectValue placeholder="Severity" />
        </SelectTrigger>
        <SelectContent>
          {["all", "Critical", "High", "Medium", "Low"].map((s) => (
            <SelectItem key={s} value={s}>
              {s === "all" ? "All severities" : s}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Input
        placeholder="Cluster ID"
        value={filters.cluster ?? ""}
        onChange={(e) => set("cluster", e.target.value || undefined)}
      />
      <Button variant="outline" size="icon" onClick={onReset} aria-label="Reset filters">
        <RotateCcw className="h-4 w-4" />
      </Button>
    </div>
  );
}
