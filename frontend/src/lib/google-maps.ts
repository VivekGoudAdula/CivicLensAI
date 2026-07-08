import { useJsApiLoader } from "@react-google-maps/api";

import { env } from "@/config/env";

export const AMETHI_CENTER = { lat: 26.1539, lng: 81.8139 };
export const DEFAULT_MAP_ID = "DEMO_MAP_ID";

export function useGoogleMapsLoader() {
  return useJsApiLoader({
    id: "civiclens-google-maps",
    googleMapsApiKey: env.googleMapsApiKey,
    version: "weekly",
  });
}

export function getGoogleMapsSetupMessage(): string {
  return [
    "Enable these APIs in Google Cloud Console for your project:",
    "• Maps JavaScript API",
    "• Places API (New)",
    "• Geocoding API",
    "",
    "Ensure billing is enabled and your API key allows http://localhost:5173.",
    "Create a Map ID (or use DEMO_MAP_ID for development) for advanced markers.",
  ].join("\n");
}

export function isMapsActivationError(message: string): boolean {
  const normalized = message.toLowerCase();
  return (
    normalized.includes("apinotactivated") ||
    normalized.includes("api not activated") ||
    normalized.includes("referernotallowed") ||
    normalized.includes("invalidkeymaperror")
  );
}
