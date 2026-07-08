import { Layers, LocateFixed, Maximize2, RotateCcw, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { GisLayerState } from "@/features/gis/types/gis";

interface MapControlsProps {
  layers: GisLayerState;
  onLayersChange: (layers: GisLayerState) => void;
  onLocate: () => void;
  onReset: () => void;
  onFullscreen: () => void;
  search: string;
  onSearchChange: (value: string) => void;
}

export function MapControls({
  layers,
  onLayersChange,
  onLocate,
  onReset,
  onFullscreen,
  search,
  onSearchChange,
}: MapControlsProps) {
  const toggle = (key: keyof GisLayerState, value?: boolean) => {
    onLayersChange({ ...layers, [key]: value ?? !layers[key] });
  };

  return (
    <div className="flex flex-col gap-2 rounded-xl border bg-background/95 p-3 shadow-lg backdrop-blur">
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          className="h-9 pl-8"
          placeholder="Search location..."
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Button variant="outline" size="sm" onClick={onLocate}>
          <LocateFixed className="h-4 w-4" />
          Locate
        </Button>
        <Button variant="outline" size="sm" onClick={onReset}>
          <RotateCcw className="h-4 w-4" />
          Reset
        </Button>
        <Button variant="outline" size="sm" onClick={onFullscreen}>
          <Maximize2 className="h-4 w-4" />
          Fullscreen
        </Button>
        <Button
          variant={layers.showHeatmap ? "default" : "outline"}
          size="sm"
          onClick={() => toggle("showHeatmap")}
        >
          <Layers className="h-4 w-4" />
          Heatmap
        </Button>
      </div>
      <div className="flex flex-wrap gap-1">
        <Button
          variant={layers.showComplaints ? "default" : "outline"}
          size="sm"
          className="text-xs"
          onClick={() => toggle("showComplaints")}
        >
          Complaints
        </Button>
        <Button
          variant={layers.showClusters ? "default" : "outline"}
          size="sm"
          className="text-xs"
          onClick={() => toggle("showClusters")}
        >
          Clusters
        </Button>
        {(["priority", "severity", "department"] as const).map((mode) => (
          <Button
            key={mode}
            variant={layers.colorMode === mode ? "default" : "outline"}
            size="sm"
            className="text-xs capitalize"
            onClick={() => onLayersChange({ ...layers, colorMode: mode })}
          >
            {mode}
          </Button>
        ))}
      </div>
    </div>
  );
}
