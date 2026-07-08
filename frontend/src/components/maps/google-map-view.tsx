import { useEffect, useRef } from "react";

import { ErrorState } from "@/components/empty-states/error-state";
import { Spinner } from "@/components/feedback/spinner";
import { env } from "@/config/env";
import {
  DEFAULT_MAP_ID,
  getGoogleMapsSetupMessage,
  useGoogleMapsLoader,
} from "@/lib/google-maps";
import { cn } from "@/lib/utils";

export interface GoogleMapViewProps {
  latitude: number;
  longitude: number;
  className?: string;
  height?: number;
  zoom?: number;
}

export function GoogleMapView({
  latitude,
  longitude,
  className,
  height = 280,
  zoom = 15,
}: GoogleMapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const { isLoaded, loadError } = useGoogleMapsLoader();

  useEffect(() => {
    if (!isLoaded || !mapContainerRef.current) {
      return;
    }

    let map: google.maps.Map | undefined;
    let marker: google.maps.marker.AdvancedMarkerElement | undefined;
    let cancelled = false;

    async function initMap() {
      const [{ Map }, { AdvancedMarkerElement }] = await Promise.all([
        google.maps.importLibrary("maps") as Promise<google.maps.MapsLibrary>,
        google.maps.importLibrary("marker") as Promise<google.maps.MarkerLibrary>,
      ]);

      if (cancelled || !mapContainerRef.current) {
        return;
      }

      map = new Map(mapContainerRef.current, {
        center: { lat: latitude, lng: longitude },
        zoom,
        mapId: env.googleMapsMapId || DEFAULT_MAP_ID,
        streetViewControl: false,
        mapTypeControl: false,
        fullscreenControl: false,
      });

      marker = new AdvancedMarkerElement({
        map,
        position: { lat: latitude, lng: longitude },
      });
    }

    void initMap();

    return () => {
      cancelled = true;
      if (marker) {
        marker.map = null;
      }
    };
  }, [isLoaded, latitude, longitude, zoom]);

  if (!env.googleMapsApiKey) {
    return (
      <div
        className={cn(
          "flex items-center justify-center rounded-xl border bg-muted/30 text-sm text-muted-foreground",
          className,
        )}
        style={{ height }}
      >
        Map unavailable — configure VITE_GOOGLE_MAPS_API_KEY
      </div>
    );
  }

  if (loadError) {
    return (
      <ErrorState
        title="Google Maps failed to load"
        description={getGoogleMapsSetupMessage()}
      />
    );
  }

  if (!isLoaded) {
    return (
      <div
        className={cn("flex items-center justify-center rounded-xl border", className)}
        style={{ height }}
      >
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div
      ref={mapContainerRef}
      className={cn("overflow-hidden rounded-xl border", className)}
      style={{ height, width: "100%" }}
      role="application"
      aria-label="Complaint location map"
    />
  );
}
