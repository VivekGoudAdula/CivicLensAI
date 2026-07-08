import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Clock, Layers, MessageSquareWarning, Sparkles } from "lucide-react";

import { NoSearchResultsEmptyState } from "@/components/empty-states/no-search-results";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import type { GlobalSearchResultItem } from "@/features/search/types/search";
import { cn } from "@/lib/utils";

const TYPE_ICONS = {
  complaint: MessageSquareWarning,
  cluster: Layers,
  recommendation: Sparkles,
};

function highlightText(text: string, query: string) {
  if (!query) return text;
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx < 0) return text;
  return (
    <>
      {text.slice(0, idx)}
      <mark className="rounded bg-primary/20 px-0.5">{text.slice(idx, idx + query.length)}</mark>
      {text.slice(idx + query.length)}
    </>
  );
}

interface SearchResultsListProps {
  items: GlobalSearchResultItem[];
  query: string;
  isLoading: boolean;
}

export function SearchResultsList({ items, query, isLoading }: SearchResultsListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return <NoSearchResultsEmptyState query={query} />;
  }

  return (
    <div className="space-y-2">
      {items.map((item, index) => {
        const Icon = TYPE_ICONS[item.type];
        return (
          <motion.div
            key={`${item.type}-${item.id}`}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.02 }}
          >
            <Link
              to={item.url_path}
              className="flex gap-3 rounded-xl border bg-card p-4 transition-all hover:border-primary/30 hover:shadow-md"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
                <Icon className="h-4 w-4 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium">{highlightText(item.title, query)}</p>
                  <span className="rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-wide text-muted-foreground">
                    {item.type}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">{item.subtitle}</p>
                {item.highlight ? (
                  <p className={cn("mt-1 line-clamp-2 text-xs text-muted-foreground")}>
                    {highlightText(item.highlight, query)}
                  </p>
                ) : null}
              </div>
            </Link>
          </motion.div>
        );
      })}
    </div>
  );
}

interface RecentSearchesProps {
  items: string[];
  onSelect: (query: string) => void;
  onClear: () => void;
}

export function RecentSearches({ items, onSelect, onClear }: RecentSearchesProps) {
  if (items.length === 0) return null;
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
          <Clock className="h-4 w-4" />
          Recent Searches
        </p>
        <button type="button" className="text-xs text-primary hover:underline" onClick={onClear}>
          Clear
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => onSelect(item)}
            className="rounded-full border px-3 py-1 text-xs transition-colors hover:bg-muted"
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}
