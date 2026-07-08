import { useEffect } from "react";
import { useMap } from "react-leaflet";
import "leaflet.heat";

import { L } from "@/features/gis/lib/leaflet-setup";

interface HeatmapLayerProps {
  points: Array<[number, number, number]>;
  enabled: boolean;
}

export function HeatmapLayer({ points, enabled }: HeatmapLayerProps) {
  const map = useMap();

  useEffect(() => {
    if (!enabled || points.length === 0) {
      return;
    }

    const layer = L.heatLayer(points, {
      radius: 28,
      blur: 18,
      maxZoom: 16,
      max: 1.0,
      gradient: {
        0.2: "#22c55e",
        0.4: "#eab308",
        0.6: "#f97316",
        0.8: "#ef4444",
        1.0: "#7f1d1d",
      },
    });
    layer.addTo(map);

    return () => {
      map.removeLayer(layer);
    };
  }, [map, points, enabled]);

  return null;
}
