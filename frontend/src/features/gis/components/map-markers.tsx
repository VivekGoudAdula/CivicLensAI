import { useEffect, useRef } from "react";
import { Marker, Popup, useMap } from "react-leaflet";
import "leaflet.markercluster";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";

import { L } from "@/features/gis/lib/leaflet-setup";
import {
  departmentColor,
  getClusterPinColor,
  getComplaintPinColor,
} from "@/features/gis/lib/map-utils";
import type { GisClusterMarker, GisComplaintPin, GisLayerState } from "@/features/gis/types/gis";

function pinColor(
  complaint: GisComplaintPin,
  colorMode: GisLayerState["colorMode"],
): string {
  if (colorMode === "department") {
    return departmentColor(complaint.department);
  }
  if (colorMode === "severity" && complaint.severity) {
    return getComplaintPinColor(complaint.severity, complaint.status);
  }
  return getComplaintPinColor(complaint.priority, complaint.status);
}

function createDivIcon(color: string, label: string, size = 28) {
  return L.divIcon({
    className: "civiclens-map-pin",
    html: `<div style="background:${color};width:${size}px;height:${size}px;border-radius:50%;border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,.25);display:flex;align-items:center;justify-content:center;color:white;font-size:10px;font-weight:700;">${label}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

interface ComplaintMarkersProps {
  complaints: GisComplaintPin[];
  layers: GisLayerState;
  onSelect: (complaint: GisComplaintPin) => void;
}

export function ComplaintMarkers({ complaints, layers, onSelect }: ComplaintMarkersProps) {
  const map = useMap();
  const clusterGroupRef = useRef<L.MarkerClusterGroup | null>(null);

  useEffect(() => {
    if (!layers.showComplaints) {
      if (clusterGroupRef.current) {
        map.removeLayer(clusterGroupRef.current);
        clusterGroupRef.current = null;
      }
      return;
    }

    const group = L.markerClusterGroup({
      showCoverageOnHover: false,
      maxClusterRadius: 50,
      spiderfyOnMaxZoom: true,
    });

    complaints.forEach((complaint) => {
      const color = pinColor(complaint, layers.colorMode);
      const marker = L.marker([complaint.latitude, complaint.longitude], {
        icon: createDivIcon(color, complaint.priority[0]?.toUpperCase() ?? "C", 24),
      });
      marker.on("click", () => onSelect(complaint));
      marker.bindPopup(`<strong>${complaint.title}</strong><br/>${complaint.village_name}`);
      group.addLayer(marker);
    });

    map.addLayer(group);
    clusterGroupRef.current = group;

    return () => {
      map.removeLayer(group);
      clusterGroupRef.current = null;
    };
  }, [complaints, layers.showComplaints, layers.colorMode, map, onSelect]);

  return null;
}

interface ClusterMarkersProps {
  clusters: GisClusterMarker[];
  layers: GisLayerState;
  onSelect: (cluster: GisClusterMarker) => void;
}

export function ClusterMarkers({ clusters, layers, onSelect }: ClusterMarkersProps) {
  if (!layers.showClusters) {
    return null;
  }

  return (
    <>
      {clusters.map((cluster) => {
        const color = getClusterPinColor(cluster.cluster_score);
        return (
          <Marker
            key={cluster.id}
            position={[cluster.latitude, cluster.longitude]}
            icon={createDivIcon(color, String(cluster.complaint_count), 34)}
            eventHandlers={{ click: () => onSelect(cluster) }}
          >
            <Popup>
              <div className="space-y-1 text-sm">
                <p className="font-semibold">{cluster.title}</p>
                <p>{cluster.complaint_count} complaints</p>
                <p>Priority score: {cluster.cluster_score}</p>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
}
