import { memo, useCallback, useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import { ErrorState } from "@/components/empty-states/error-state";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { HeatmapLayer } from "@/features/gis/components/heatmap-layer";
import { ClusterMarkers, ComplaintMarkers } from "@/features/gis/components/map-markers";
import {
  MapClusterDrawer,
  MapPinDrawer,
} from "@/features/gis/components/map-pin-drawer";
import { AMETHI_CENTER, DEFAULT_ZOOM } from "@/features/gis/lib/map-utils";
import type {
  GisClusterMarker,
  GisComplaintPin,
  GisLayerState,
  GisMapResponse,
} from "@/features/gis/types/gis";

function MapViewportController({
  bounds,
  resetToken,
}: {
  bounds: GisMapResponse["bounds"];
  resetToken: number;
}) {
  const map = useMap();

  const applyBounds = useCallback(() => {
    if (bounds) {
      map.fitBounds(
        [
          [bounds.south, bounds.west],
          [bounds.north, bounds.east],
        ],
        { padding: [40, 40] },
      );
    } else {
      map.setView(AMETHI_CENTER, DEFAULT_ZOOM);
    }
  }, [bounds, map]);

  useEffect(() => {
    applyBounds();
  }, [applyBounds, resetToken]);

  return null;
}

interface ConstituencyMapProps {
  data: GisMapResponse;
  complaints: GisComplaintPin[];
  clusters: GisClusterMarker[];
  layers: GisLayerState;
  resetToken: number;
  onSelectComplaint: (complaint: GisComplaintPin) => void;
  onSelectCluster: (cluster: GisClusterMarker) => void;
}

export const ConstituencyMap = memo(function ConstituencyMap({
  data,
  complaints,
  clusters,
  layers,
  resetToken,
  onSelectComplaint,
  onSelectCluster,
}: ConstituencyMapProps) {
  const heatPoints = useMemo(() => {
    const complaintPoints = complaints.map(
      (c) => [c.latitude, c.longitude, c.heat_weight] as [number, number, number],
    );
    const clusterPoints = clusters.map(
      (c) => [c.latitude, c.longitude, c.heat_weight] as [number, number, number],
    );
    return [...complaintPoints, ...clusterPoints];
  }, [complaints, clusters]);

  const center: [number, number] = data.bounds
    ? [data.bounds.center_lat, data.bounds.center_lng]
    : AMETHI_CENTER;

  return (
    <MapContainer
      center={center}
      zoom={DEFAULT_ZOOM}
      className="h-full w-full rounded-xl"
      scrollWheelZoom
      zoomControl={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapViewportController bounds={data.bounds} resetToken={resetToken} />
      <HeatmapLayer points={heatPoints} enabled={layers.showHeatmap} />
      <ComplaintMarkers
        complaints={complaints}
        layers={layers}
        onSelect={onSelectComplaint}
      />
      <ClusterMarkers clusters={clusters} layers={layers} onSelect={onSelectCluster} />
    </MapContainer>
  );
});

export function ConstituencyMapShell({
  isLoading,
  isError,
  onRetry,
  data,
  complaints,
  clusters,
  layers,
  resetToken,
}: {
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  data?: GisMapResponse;
  complaints: GisComplaintPin[];
  clusters: GisClusterMarker[];
  layers: GisLayerState;
  resetToken: number;
}) {
  const [selectedComplaint, setSelectedComplaint] = useState<GisComplaintPin | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<GisClusterMarker | null>(null);

  if (isLoading) {
    return <div className="h-[70vh]"><SkeletonCard /></div>;
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Failed to load map data"
        description="Could not retrieve constituency GIS intelligence."
        onRetry={onRetry}
      />
    );
  }

  return (
    <>
      <ConstituencyMap
        data={data}
        complaints={complaints}
        clusters={clusters}
        layers={layers}
        resetToken={resetToken}
        onSelectComplaint={setSelectedComplaint}
        onSelectCluster={setSelectedCluster}
      />
      <MapPinDrawer
        complaint={selectedComplaint}
        open={Boolean(selectedComplaint)}
        onOpenChange={(open) => !open && setSelectedComplaint(null)}
      />
      <MapClusterDrawer
        cluster={selectedCluster}
        open={Boolean(selectedCluster)}
        onOpenChange={(open) => !open && setSelectedCluster(null)}
      />
    </>
  );
}

export function useMapFullscreen(containerRef: React.RefObject<HTMLElement | null>) {
  return useCallback(() => {
    const element = containerRef.current;
    if (!element) return;
    if (document.fullscreenElement) {
      void document.exitFullscreen();
    } else {
      void element.requestFullscreen();
    }
  }, [containerRef]);
}
