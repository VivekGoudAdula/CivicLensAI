import { initializeApp, type FirebaseApp } from "firebase/app";
import {
  connectFirestoreEmulator,
  getFirestore,
  type Firestore,
} from "firebase/firestore";

import { env } from "@/config/env";

let app: FirebaseApp | null = null;
let db: Firestore | null = null;
let emulatorConnected = false;

export function isFirebaseConfigured(): boolean {
  return Boolean(env.firebase.projectId);
}

export function getFirebaseApp(): FirebaseApp | null {
  if (!isFirebaseConfigured()) {
    return null;
  }
  if (!app) {
    app = initializeApp({
      apiKey: env.firebase.apiKey,
      authDomain: env.firebase.authDomain,
      projectId: env.firebase.projectId,
      storageBucket: env.firebase.storageBucket,
      messagingSenderId: env.firebase.messagingSenderId,
      appId: env.firebase.appId,
    });
  }
  return app;
}

export function getFirebaseDb(): Firestore | null {
  if (!isFirebaseConfigured()) {
    return null;
  }
  if (!db) {
    const firebaseApp = getFirebaseApp();
    if (!firebaseApp) {
      return null;
    }
    db = getFirestore(firebaseApp);
    if (env.firebase.useEmulator && !emulatorConnected) {
      connectFirestoreEmulator(db, env.firebase.emulatorHost, env.firebase.emulatorPort);
      emulatorConnected = true;
    }
  }
  return db;
}
