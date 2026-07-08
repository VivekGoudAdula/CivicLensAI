import { useEffect } from "react";
import { collection, limit, onSnapshot, query } from "firebase/firestore";

import { getFirebaseDb } from "@/lib/firebase";
import { useInvalidateDashboard } from "@/features/dashboard/hooks/use-dashboard";

const REALTIME_COLLECTIONS = ["complaints", "clusters"] as const;

export function useFirestoreRealtime() {
  const invalidateDashboard = useInvalidateDashboard();

  useEffect(() => {
    const db = getFirebaseDb();
    if (!db) {
      return;
    }

    const unsubscribers = REALTIME_COLLECTIONS.map((collectionName) => {
      const collectionQuery = query(collection(db, collectionName), limit(1));

      return onSnapshot(
        collectionQuery,
        () => {
          invalidateDashboard();
        },
        (error) => {
          console.warn(`Firestore listener error (${collectionName}):`, error.message);
        },
      );
    });

    return () => {
      unsubscribers.forEach((unsubscribe) => unsubscribe());
    };
  }, [invalidateDashboard]);
}
