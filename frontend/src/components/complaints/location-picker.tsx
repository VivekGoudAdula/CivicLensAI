import { useCallback, useEffect, useRef, useState } from "react";
import { LocateFixed, MapPin } from "lucide-react";

import { ErrorState } from "@/components/empty-states/error-state";
import { Spinner } from "@/components/feedback/spinner";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { env } from "@/config/env";
import {
  AMETHI_CENTER,
  DEFAULT_MAP_ID,
  getGoogleMapsSetupMessage,
  isMapsActivationError,
  useGoogleMapsLoader,
} from "@/lib/google-maps";
import { cn } from "@/lib/utils";

export interface LocationValue {
  latitude: number;
  longitude: number;
  address: string;
}

export interface LocationPickerProps {
  value?: LocationValue | null;
  onChange: (value: LocationValue) => void;
  error?: string;
  className?: string;
}

function LocationPickerInner({
  value,
  onChange,
  error,
  className,
}: LocationPickerProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const autocompleteContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<google.maps.Map | null>(null);
  const markerRef = useRef<google.maps.marker.AdvancedMarkerElement | null>(null);
  const onChangeRef = useRef(onChange);
  const hasAutoDetectedRef = useRef(false);
  const shouldAutoDetectRef = useRef(!value);
  const detectCurrentLocationRef = useRef<((options?: { silent?: boolean }) => void) | null>(
    null,
  );

  const [marker, setMarker] = useState<LocationValue>(
    () =>
      value ?? {
        latitude: AMETHI_CENTER.lat,
        longitude: AMETHI_CENTER.lng,
        address: "",
      },
  );
  const [geocoding, setGeocoding] = useState(false);
  const [detectingLocation, setDetectingLocation] = useState(false);
  const [locationHint, setLocationHint] = useState<string | null>(null);
  const [mapError, setMapError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    onChangeRef.current = onChange;
  }, [onChange]);

  const reverseGeocode = useCallback(async (lat: number, lng: number) => {
    setGeocoding(true);
    try {
      const geocoder = new google.maps.Geocoder();
      const response = await geocoder.geocode({ location: { lat, lng } });
      const address =
        response.results[0]?.formatted_address ?? `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
      const next = { latitude: lat, longitude: lng, address };
      setMarker(next);
      onChangeRef.current(next);
    } catch {
      const next = {
        latitude: lat,
        longitude: lng,
        address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
      };
      setMarker(next);
      onChangeRef.current(next);
    } finally {
      setGeocoding(false);
    }
  }, []);

  const updateMarkerPosition = useCallback(
    async (lat: number, lng: number, options?: { zoom?: number }) => {
      if (markerRef.current) {
        markerRef.current.position = { lat, lng };
      }
      mapRef.current?.panTo({ lat, lng });
      if (options?.zoom) {
        mapRef.current?.setZoom(options.zoom);
      }
      await reverseGeocode(lat, lng);
    },
    [reverseGeocode],
  );

  const detectCurrentLocation = useCallback(
    (options?: { silent?: boolean }) => {
      if (!navigator.geolocation) {
        if (!options?.silent) {
          setLocationHint("Geolocation is not supported in this browser.");
        }
        return;
      }

      setDetectingLocation(true);
      if (!options?.silent) {
        setLocationHint(null);
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          void updateMarkerPosition(lat, lng, { zoom: 16 }).finally(() => {
            setDetectingLocation(false);
            setLocationHint("Location detected automatically.");
          });
        },
        (geoError) => {
          setDetectingLocation(false);
          if (!options?.silent) {
            const message =
              geoError.code === geoError.PERMISSION_DENIED
                ? "Location permission denied. Search or drop a pin manually."
                : "Could not detect location. Search or drop a pin manually.";
            setLocationHint(message);
          }
        },
        {
          enableHighAccuracy: true,
          timeout: 12000,
          maximumAge: 60000,
        },
      );
    },
    [updateMarkerPosition],
  );

  useEffect(() => {
    detectCurrentLocationRef.current = detectCurrentLocation;
  }, [detectCurrentLocation]);

  useEffect(() => {
    if (!mapContainerRef.current || !autocompleteContainerRef.current) {
      return;
    }

    let cancelled = false;
    let clickListener: google.maps.MapsEventListener | null = null;
    let dragListener: google.maps.MapsEventListener | null = null;
    let selectListener: ((event: Event) => void) | null = null;
    let autocompleteElement: google.maps.places.PlaceAutocompleteElement | null = null;

    async function init() {
      try {
        const [mapsLib, placesLib, markerLib] = await Promise.all([
          google.maps.importLibrary("maps"),
          google.maps.importLibrary("places"),
          google.maps.importLibrary("marker"),
        ]);

        const { Map } = mapsLib as google.maps.MapsLibrary;
        const { AdvancedMarkerElement } = markerLib as google.maps.MarkerLibrary;
        const PlaceAutocompleteElement = (
          placesLib as google.maps.PlacesLibrary & {
            PlaceAutocompleteElement: new (
              options?: google.maps.places.PlaceAutocompleteElementOptions,
            ) => google.maps.places.PlaceAutocompleteElement;
          }
        ).PlaceAutocompleteElement;

        if (cancelled || !mapContainerRef.current || !autocompleteContainerRef.current) {
          return;
        }

        const initial = value ?? {
          latitude: AMETHI_CENTER.lat,
          longitude: AMETHI_CENTER.lng,
          address: "",
        };

        const map = new Map(mapContainerRef.current, {
          center: { lat: initial.latitude, lng: initial.longitude },
          zoom: 14,
          mapId: env.googleMapsMapId || DEFAULT_MAP_ID,
          streetViewControl: false,
          mapTypeControl: false,
          fullscreenControl: false,
        });
        mapRef.current = map;

        const advancedMarker = new AdvancedMarkerElement({
          map,
          position: { lat: initial.latitude, lng: initial.longitude },
          gmpDraggable: true,
        });
        markerRef.current = advancedMarker;

        autocompleteElement = new PlaceAutocompleteElement({
          includedRegionCodes: ["in"],
        } as google.maps.places.PlaceAutocompleteElementOptions);
        autocompleteElement.className = "civiclens-place-autocomplete";
        autocompleteContainerRef.current.replaceChildren(autocompleteElement);

        selectListener = async (event: Event) => {
          const selectEvent = event as Event & {
            placePrediction: { toPlace: () => google.maps.places.Place };
          };
          const place = selectEvent.placePrediction.toPlace();
          await place.fetchFields({ fields: ["location", "formattedAddress"] });

          if (!place.location) {
            return;
          }

          const lat = place.location.lat();
          const lng = place.location.lng();
          const address = place.formattedAddress ?? `${lat}, ${lng}`;
          const next = { latitude: lat, longitude: lng, address };
          setMarker(next);
          onChangeRef.current(next);
          advancedMarker.position = { lat, lng };
          map.panTo({ lat, lng });
          map.setZoom(16);
        };
        autocompleteElement.addEventListener("gmp-select", selectListener);

        clickListener = map.addListener("click", (event: google.maps.MapMouseEvent) => {
          if (!event.latLng) {
            return;
          }
          void updateMarkerPosition(event.latLng.lat(), event.latLng.lng());
        });

        dragListener = advancedMarker.addListener("dragend", () => {
          const position = advancedMarker.position;
          if (!position) {
            return;
          }
          const lat = typeof position.lat === "function" ? position.lat() : position.lat;
          const lng = typeof position.lng === "function" ? position.lng() : position.lng;
          void updateMarkerPosition(lat, lng);
        });

        if (!cancelled) {
          setReady(true);
          if (shouldAutoDetectRef.current && !hasAutoDetectedRef.current) {
            hasAutoDetectedRef.current = true;
            detectCurrentLocationRef.current?.({ silent: false });
          } else if (!value?.address) {
            void reverseGeocode(initial.latitude, initial.longitude);
          }
        }
      } catch (initError) {
        if (!cancelled) {
          const message =
            initError instanceof Error ? initError.message : "Failed to initialize Google Maps";
          setMapError(message);
        }
      }
    }

    void init();

    return () => {
      cancelled = true;
      if (clickListener) {
        google.maps.event.removeListener(clickListener);
      }
      if (dragListener) {
        google.maps.event.removeListener(dragListener);
      }
      if (autocompleteElement && selectListener) {
        autocompleteElement.removeEventListener("gmp-select", selectListener);
      }
      if (markerRef.current) {
        markerRef.current.map = null;
      }
      mapRef.current = null;
      markerRef.current = null;
    };
  }, [reverseGeocode, updateMarkerPosition, value?.address]);

  useEffect(() => {
    const previousHandler = window.gm_authFailure;
    window.gm_authFailure = () => {
      setMapError("Google Maps API is not activated or the API key is invalid.");
    };
    return () => {
      window.gm_authFailure = previousHandler;
    };
  }, []);

  if (mapError) {
    return (
      <ErrorState
        title="Google Maps could not load"
        description={
          isMapsActivationError(mapError)
            ? getGoogleMapsSetupMessage()
            : mapError
        }
      />
    );
  }

  return (
    <div className={cn("space-y-3", className)}>
      <div className="space-y-2">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <Label htmlFor="location-search">Search Location</Label>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => detectCurrentLocation()}
            disabled={detectingLocation || !ready}
            aria-label="Detect my current location"
          >
            <LocateFixed className="h-4 w-4" />
            {detectingLocation ? "Detecting..." : "Use my location"}
          </Button>
        </div>
        <div
          ref={autocompleteContainerRef}
          id="location-search"
          className="civiclens-place-autocomplete-shell"
          aria-label="Search location"
        />
        {locationHint ? (
          <p className="text-xs text-muted-foreground">{locationHint}</p>
        ) : null}
      </div>

      <div className="relative overflow-hidden rounded-xl border">
        <div
          ref={mapContainerRef}
          className="h-[360px] w-full"
          role="application"
          aria-label="Interactive location map"
        />
        {!ready || geocoding || detectingLocation ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-background/60">
            <Spinner />
            {detectingLocation ? (
              <p className="text-sm text-muted-foreground">Detecting your location...</p>
            ) : null}
          </div>
        ) : null}
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border bg-muted/30 p-3">
          <p className="text-xs font-medium text-muted-foreground">Latitude</p>
          <p className="mt-1 font-mono text-sm">{marker.latitude.toFixed(6)}</p>
        </div>
        <div className="rounded-lg border bg-muted/30 p-3">
          <p className="text-xs font-medium text-muted-foreground">Longitude</p>
          <p className="mt-1 font-mono text-sm">{marker.longitude.toFixed(6)}</p>
        </div>
        <div className="rounded-lg border bg-muted/30 p-3 sm:col-span-1">
          <p className="text-xs font-medium text-muted-foreground">Pin</p>
          <p className="mt-1 flex items-center gap-1 text-sm">
            <MapPin className="h-3.5 w-3.5 text-primary" />
            Auto-detect, search, or drag pin
          </p>
        </div>
      </div>

      {error ? <p className="text-sm text-destructive">{error}</p> : null}
    </div>
  );
}

export function LocationPicker(props: LocationPickerProps) {
  const { isLoaded, loadError } = useGoogleMapsLoader();

  if (!env.googleMapsApiKey) {
    return (
      <ErrorState
        title="Google Maps not configured"
        description="Add VITE_GOOGLE_MAPS_API_KEY to your frontend .env file to enable the location picker."
      />
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
      <div className="flex h-[360px] items-center justify-center rounded-xl border">
        <Spinner size="lg" />
      </div>
    );
  }

  return <LocationPickerInner {...props} />;
}

declare global {
  interface Window {
    gm_authFailure?: () => void;
  }
}
