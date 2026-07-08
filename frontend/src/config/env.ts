export const env = {
  apiBaseUrl:
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  appName: import.meta.env.VITE_APP_NAME ?? "CivicLens AI",
  appVersion: import.meta.env.VITE_APP_VERSION ?? "1.0.0",
  googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY ?? "",
  googleMapsMapId: import.meta.env.VITE_GOOGLE_MAPS_MAP_ID ?? "DEMO_MAP_ID",
  firebase: {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY ?? "demo-api-key",
    authDomain:
      import.meta.env.VITE_FIREBASE_AUTH_DOMAIN ?? "civiclens-ai-dev.firebaseapp.com",
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID ?? "civiclens-ai-dev",
    storageBucket:
      import.meta.env.VITE_FIREBASE_STORAGE_BUCKET ?? "civiclens-ai-dev.appspot.com",
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID ?? "",
    appId: import.meta.env.VITE_FIREBASE_APP_ID ?? "",
    useEmulator: import.meta.env.VITE_FIREBASE_USE_EMULATOR === "true",
    emulatorHost: import.meta.env.VITE_FIREBASE_EMULATOR_HOST ?? "127.0.0.1",
    emulatorPort: Number(import.meta.env.VITE_FIREBASE_EMULATOR_PORT ?? "8085"),
  },
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
} as const;
