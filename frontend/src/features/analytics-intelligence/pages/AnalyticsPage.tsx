import { useRef, useState } from "react";
import { motion } from "framer-motion";

import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { AnalyticsChartsGrid } from "@/features/analytics-intelligence/components/analytics-charts-grid";
import { AnalyticsExportToolbar } from "@/features/analytics-intelligence/components/analytics-export-toolbar";
import { AnalyticsFiltersBar } from "@/features/analytics-intelligence/components/analytics-filters-bar";
import { AnalyticsKPIGrid } from "@/features/analytics-intelligence/components/analytics-kpi-grid";
import { PredictiveAnalyticsPanel } from "@/features/analytics-intelligence/components/predictive-analytics-panel";
import { useAnalyticsIntelligence } from "@/features/analytics-intelligence/hooks/use-analytics-intelligence";
import type { AnalyticsFilters } from "@/features/analytics-intelligence/types/analytics";
import { useGisRealtime } from "@/features/gis/hooks/use-gis-realtime";
import { formatDateTime } from "@/lib/complaint-utils";

export function AnalyticsPage() {
  useGisRealtime();
  const { data, isLoading, isError, refetch } = useAnalyticsIntelligence();
  const [filters, setFilters] = useState<AnalyticsFilters>({});
  const dashboardRef = useRef<HTMLDivElement>(null);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Constituency Analytics Intelligence"
          description="Complete analytics dashboard for government decision-making"
        />
        <div className="grid gap-4 md:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Failed to load analytics"
        description="Could not retrieve constituency analytics intelligence."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <motion.div
      ref={dashboardRef}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="analytics-print-root space-y-8"
    >
      <PageHeader
        title="Constituency Analytics Intelligence"
        description="14 professional charts, predictive insights, and exportable constituency intelligence"
        actions={<AnalyticsExportToolbar data={data} dashboardRef={dashboardRef} />}
      />

      <p className="text-sm text-muted-foreground">
        Last updated {formatDateTime(data.last_updated_at)} · Engine: {data.predictive.engine}
      </p>

      <AnalyticsFiltersBar
        filters={filters}
        onChange={setFilters}
        onReset={() => setFilters({})}
      />

      <AnalyticsKPIGrid kpis={data.kpis} />

      <PredictiveAnalyticsPanel cards={data.predictive.cards} />

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">Analytics Charts</h2>
        <AnalyticsChartsGrid charts={data.charts} />
      </section>
    </motion.div>
  );
}
