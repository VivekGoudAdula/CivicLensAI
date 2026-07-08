import { PIN_COLORS } from "@/features/gis/lib/map-utils";
import type { GisLayerState } from "@/features/gis/types/gis";

interface MapLegendProps {
  layers: GisLayerState;
}

export function MapLegend({ layers }: MapLegendProps) {
  const priorityItems = [
    { label: "Critical", color: PIN_COLORS.critical },
    { label: "High", color: PIN_COLORS.high },
    { label: "Medium", color: PIN_COLORS.medium },
    { label: "Low", color: PIN_COLORS.low },
    { label: "Resolved", color: PIN_COLORS.resolved },
  ];

  return (
    <div className="rounded-xl border bg-background/95 p-3 shadow-lg backdrop-blur">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Legend · {layers.colorMode}
      </p>
      <div className="space-y-1.5">
        {priorityItems.map((item) => (
          <div key={item.label} className="flex items-center gap-2 text-xs">
            <span
              className="h-3 w-3 rounded-full border border-white shadow"
              style={{ backgroundColor: item.color }}
            />
            {item.label}
          </div>
        ))}
      </div>
      {layers.showHeatmap ? (
        <p className="mt-2 text-xs text-muted-foreground">
          Heatmap intensity: density × priority × severity
        </p>
      ) : null}
    </div>
  );
}
