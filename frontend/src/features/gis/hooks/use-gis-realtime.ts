import { useEffect } from "react";
import { collection, limit, onSnapshot, query } from "firebase/firestore";

import { useInvalidateGis } from "@/features/gis/hooks/use-gis-map";
import { getFirebaseDb } from "@/lib/firebase";

const COLLECTIONS = ["complaints", "clusters"] as const;

export function useGisRealtime() {
  const invalidate = useInvalidateGis();

  useEffect(() => {
    const db = getFirebaseDb();
    if (!db) return;

    const unsubscribers = COLLECTIONS.map((name) =>
      onSnapshot(
        query(collection(db, name), limit(1)),
        () => invalidate(),
        (error) => console.warn(`GIS realtime error (${name}):`, error.message),
      ),
    );

    return () => unsubscribers.forEach((unsub) => unsub());
  }, [invalidate]);
}
