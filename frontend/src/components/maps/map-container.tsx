import type { ReactNode } from "react";

import { Spinner } from "@/components/feedback/spinner";
import { NoAnalyticsEmptyState } from "@/components/empty-states/no-analytics";
import { cn } from "@/lib/utils";

export interface MapLegendItem {
  color: string;
  label: string;
}

export interface MapLegendProps {
  items: MapLegendItem[];
  className?: string;
}

export function MapLegend({ items, className }: MapLegendProps) {
  return (
    <div
      className={cn(
        "rounded-lg border bg-background/95 p-3 shadow-card backdrop-blur",
        className,
      )}
      role="list"
      aria-label="Map legend"
    >
      <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Legend
      </p>
      <ul className="space-y-1.5">
        {items.map((item) => (
          <li key={item.label} className="flex items-center gap-2 text-sm" role="listitem">
            <span
              className="h-3 w-3 rounded-full"
              style={{ backgroundColor: item.color }}
              aria-hidden="true"
            />
            {item.label}
          </li>
        ))}
      </ul>
    </div>
  );
}

export interface MapControlsProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onReset?: () => void;
  className?: string;
}

export function MapControls({
  onZoomIn,
  onZoomOut,
  onReset,
  className,
}: MapControlsProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-1 rounded-lg border bg-background/95 p-1 shadow-card backdrop-blur",
        className,
      )}
      role="toolbar"
      aria-label="Map controls"
    >
      <button
        type="button"
        onClick={onZoomIn}
        className="flex h-8 w-8 items-center justify-center rounded-md text-sm hover:bg-accent"
        aria-label="Zoom in"
      >
        +
      </button>
      <button
        type="button"
        onClick={onZoomOut}
        className="flex h-8 w-8 items-center justify-center rounded-md text-sm hover:bg-accent"
        aria-label="Zoom out"
      >
        −
      </button>
      <button
        type="button"
        onClick={onReset}
        className="flex h-8 w-8 items-center justify-center rounded-md text-xs hover:bg-accent"
        aria-label="Reset view"
      >
        ⟲
      </button>
    </div>
  );
}

export interface MapMarker {
  id: string;
  x: number;
  y: number;
  label: string;
  color?: string;
}

export interface MapMarkerLayerProps {
  markers: MapMarker[];
}

export function MapMarkerLayer({ markers }: MapMarkerLayerProps) {
  return (
    <>
      {markers.map((marker) => (
        <div
          key={marker.id}
          className="absolute -translate-x-1/2 -translate-y-1/2"
          style={{ left: `${marker.x}%`, top: `${marker.y}%` }}
          role="img"
          aria-label={marker.label}
        >
          <div
            className="flex h-6 w-6 items-center justify-center rounded-full border-2 border-background shadow-md"
            style={{ backgroundColor: marker.color ?? "hsl(var(--primary))" }}
          >
            <span className="h-2 w-2 rounded-full bg-white" />
          </div>
          <span className="absolute left-1/2 top-full mt-1 -translate-x-1/2 whitespace-nowrap rounded bg-background px-1.5 py-0.5 text-[10px] font-medium shadow-sm">
            {marker.label}
          </span>
        </div>
      ))}
    </>
  );
}

export interface MapHeatmapLayerProps {
  points: Array<{ x: number; y: number; intensity: number }>;
}

export function MapHeatmapLayer({ points }: MapHeatmapLayerProps) {
  return (
    <>
      {points.map((point, index) => (
        <div
          key={index}
          className="pointer-events-none absolute rounded-full blur-xl"
          style={{
            left: `${point.x}%`,
            top: `${point.y}%`,
            width: `${40 + point.intensity * 60}px`,
            height: `${40 + point.intensity * 60}px`,
            transform: "translate(-50%, -50%)",
            backgroundColor: `hsl(var(--destructive) / ${0.1 + point.intensity * 0.4})`,
          }}
          aria-hidden="true"
        />
      ))}
    </>
  );
}

export interface MapContainerProps {
  loading?: boolean;
  empty?: boolean;
  children?: ReactNode;
  markers?: MapMarker[];
  heatmapPoints?: Array<{ x: number; y: number; intensity: number }>;
  legendItems?: MapLegendItem[];
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onReset?: () => void;
  className?: string;
}

export function MapContainer({
  loading = false,
  empty = false,
  children,
  markers = [],
  heatmapPoints = [],
  legendItems = [],
  onZoomIn,
  onZoomOut,
  onReset,
  className,
}: MapContainerProps) {
  if (loading) {
    return (
      <div
        className={cn(
          "flex aspect-[16/9] items-center justify-center rounded-xl border bg-muted/30",
          className,
        )}
        role="status"
        aria-label="Loading map"
      >
        <Spinner size="lg" />
      </div>
    );
  }

  if (empty) {
    return (
      <div className={cn("aspect-[16/9]", className)}>
        <NoAnalyticsEmptyState />
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative aspect-[16/9] overflow-hidden rounded-xl border bg-gradient-to-br from-muted/50 to-muted",
        className,
      )}
      role="application"
      aria-label="Constituency map"
    >
      <div
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage:
            "linear-gradient(hsl(var(--border)) 1px, transparent 1px), linear-gradient(90deg, hsl(var(--border)) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
        aria-hidden="true"
      />
      <MapHeatmapLayer points={heatmapPoints} />
      <MapMarkerLayer markers={markers} />
      {children}
      <MapControls
        onZoomIn={onZoomIn}
        onZoomOut={onZoomOut}
        onReset={onReset}
        className="absolute right-4 top-4"
      />
      {legendItems.length > 0 ? (
        <MapLegend items={legendItems} className="absolute bottom-4 left-4" />
      ) : null}
    </div>
  );
}
