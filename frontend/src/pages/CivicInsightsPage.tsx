import { BarChart3, Layers, MapPin, Users } from "lucide-react";
import { useState } from "react";

import { ClusterCard } from "@/components/clusters/cluster-card";
import { KPICard } from "@/components/charts/kpi-card";
import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { DashboardGrid } from "@/components/layout/DashboardGrid";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { Input } from "@/components/ui/input";
import { useClusterDashboard, useClusters } from "@/hooks/use-clusters";

export function CivicInsightsPage() {
  const [search, setSearch] = useState("");

  const { data: dashboard, isLoading: dashboardLoading, isError: dashboardError, refetch: refetchDashboard } =
    useClusterDashboard();
  const {
    data: clusters,
    isLoading: clustersLoading,
    isError: clustersError,
    refetch: refetchClusters,
  } = useClusters({ page: 1, page_size: 12, search: search || undefined });

  const isLoading = dashboardLoading || clustersLoading;
  const isError = dashboardError || clustersError;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Civic Insights"
          description="AI-powered complaint clusters and duplicate detection dashboard"
        />
        <DashboardGrid columns={4}>
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </DashboardGrid>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (isError || !dashboard || !clusters) {
    return (
      <ErrorState
        title="Failed to load cluster dashboard"
        description="Could not retrieve clustering data from the API."
        onRetry={() => {
          void refetchDashboard();
          void refetchClusters();
        }}
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Civic Insights"
        description="Automatic duplicate detection and complaint clustering powered by Gemini"
      />

      <DashboardGrid columns={4}>
        <KPICard label="Total Clusters" value={dashboard.total_clusters} icon={Layers} />
        <KPICard label="Open Clusters" value={dashboard.open_clusters} icon={BarChart3} />
        <KPICard
          label="Clustered Complaints"
          value={dashboard.total_clustered_complaints}
          icon={Users}
        />
        <KPICard
          label="Avg Cluster Size"
          value={dashboard.average_cluster_size.toFixed(1)}
          icon={MapPin}
        />
      </DashboardGrid>

      {dashboard.top_hotspots.length > 0 ? (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold">Top Hotspots</h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {dashboard.top_hotspots.map((cluster) => (
              <ClusterCard key={cluster.id} cluster={cluster} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold">All Clusters</h2>
          <Input
            placeholder="Search clusters..."
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
            }}
            className="max-w-sm"
          />
        </div>

        {clusters.items.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No clusters found. Submit complaints with images to trigger automatic clustering.
          </p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {clusters.items.map((cluster) => (
              <ClusterCard key={cluster.id} cluster={cluster} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
