import { useCallback, useEffect, useState } from "react";

export function useDebouncedValue<T>(value: T, delayMs = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}

const RECENT_SEARCHES_KEY = "civiclens-recent-searches";
const SAVED_FILTERS_KEY = "civiclens-saved-filters";
const MAX_RECENT = 8;

export function useRecentSearches() {
  const [recent, setRecent] = useState<string[]>(() => {
    try {
      return JSON.parse(localStorage.getItem(RECENT_SEARCHES_KEY) ?? "[]") as string[];
    } catch {
      return [];
    }
  });

  const addRecent = useCallback((query: string) => {
    const trimmed = query.trim();
    if (!trimmed) return;
    setRecent((current) => {
      const next = [trimmed, ...current.filter((item) => item !== trimmed)].slice(0, MAX_RECENT);
      localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  const clearRecent = useCallback(() => {
    localStorage.removeItem(RECENT_SEARCHES_KEY);
    setRecent([]);
  }, []);

  return { recent, addRecent, clearRecent };
}

export function useSavedFilters() {
  const [saved, setSaved] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(SAVED_FILTERS_KEY) ?? "[]");
    } catch {
      return [];
    }
  });

  const persist = useCallback((items: unknown[]) => {
    localStorage.setItem(SAVED_FILTERS_KEY, JSON.stringify(items));
    setSaved(items);
  }, []);

  return { saved, persist };
}
