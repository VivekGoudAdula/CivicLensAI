import { useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { MapPin, Radio } from "lucide-react";

import { PageHeader } from "@/components/layout/PageHeader";
import {
  ConstituencyMapShell,
  useMapFullscreen,
} from "@/features/gis/components/constituency-map";
import { MapControls } from "@/features/gis/components/map-controls";
import { MapFiltersPanel } from "@/features/gis/components/map-filters-panel";
import { MapLegend } from "@/features/gis/components/map-legend";
import { filterGisData } from "@/features/gis/lib/gis-filters";
import { useGisMap } from "@/features/gis/hooks/use-gis-map";
import { useGisRealtime } from "@/features/gis/hooks/use-gis-realtime";
import type { GisFilters, GisLayerState } from "@/features/gis/types/gis";
import { AMETHI_CENTER } from "@/features/gis/lib/map-utils";
import { isFirebaseConfigured } from "@/lib/firebase";
import { formatDateTime } from "@/lib/complaint-utils";

const DEFAULT_LAYERS: GisLayerState = {
  showComplaints: true,
  showClusters: true,
  showHeatmap: false,
  colorMode: "priority",
};

export function MapPage() {
  useGisRealtime();
  const { data, isLoading, isError, refetch } = useGisMap();
  const containerRef = useRef<HTMLDivElement>(null);
  const goFullscreen = useMapFullscreen(containerRef);
  const [filters, setFilters] = useState<GisFilters>({});
  const [layers, setLayers] = useState<GisLayerState>(DEFAULT_LAYERS);
  const [resetToken, setResetToken] = useState(0);
  const [search, setSearch] = useState("");

  const mergedFilters = useMemo(
    () => ({ ...filters, search: search || filters.search }),
    [filters, search],
  );

  const filtered = useMemo(() => {
    if (!data) return { complaints: [], clusters: [] };
    return filterGisData(data, mergedFilters);
  }, [data, mergedFilters]);

  const handleLocate = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition((position) => {
      setSearch(`${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`);
    });
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Constituency GIS Intelligence"
        description="Interactive map of complaints, clusters, and AI priority hotspots across Amethi"
        actions={
          isFirebaseConfigured() ? (
            <div className="flex items-center gap-2 rounded-full border bg-card px-3 py-1.5 text-xs font-medium text-muted-foreground shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              </span>
              <Radio className="h-3.5 w-3.5" />
              Live Map
            </div>
          ) : null
        }
      />

      {data?.last_updated_at ? (
        <p className="text-sm text-muted-foreground">
          {filtered.complaints.length} pins · {filtered.clusters.length} clusters · Updated{" "}
          {formatDateTime(data.last_updated_at)}
        </p>
      ) : null}

      <MapFiltersPanel
        filters={filters}
        onChange={setFilters}
        onReset={() => {
          setFilters({});
          setSearch("");
        }}
      />

      <motion.div
        ref={containerRef}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative h-[70vh] min-h-[420px] overflow-hidden rounded-xl border shadow-lg"
      >
        <div className="absolute left-3 top-3 z-[1000] max-w-xs">
          <MapControls
            layers={layers}
            onLayersChange={setLayers}
            onLocate={handleLocate}
            onReset={() => setResetToken((t) => t + 1)}
            onFullscreen={goFullscreen}
            search={search}
            onSearchChange={setSearch}
          />
        </div>
        <div className="absolute bottom-3 left-3 z-[1000]">
          <MapLegend layers={layers} />
        </div>
        <div className="absolute right-3 top-3 z-[1000] flex items-center gap-2 rounded-lg border bg-background/90 px-3 py-2 text-xs shadow">
          <MapPin className="h-3.5 w-3.5 text-primary" />
          Center: {AMETHI_CENTER[0]}, {AMETHI_CENTER[1]}
        </div>

        <ConstituencyMapShell
          isLoading={isLoading}
          isError={isError}
          onRetry={() => void refetch()}
          data={data}
          complaints={filtered.complaints}
          clusters={filtered.clusters}
          layers={layers}
          resetToken={resetToken}
        />
      </motion.div>
    </div>
  );
}
