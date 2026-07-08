import { SearchX } from "lucide-react";

import { EmptyState } from "@/components/empty-states/empty-state";

export function NoSearchResultsEmptyState({ query }: { query?: string }) {
  return (
    <EmptyState
      icon={SearchX}
      title="No results found"
      description={
        query
          ? `No results match "${query}". Try adjusting your search terms or filters.`
          : "No results match your search. Try adjusting your search terms or filters."
      }
    />
  );
}
