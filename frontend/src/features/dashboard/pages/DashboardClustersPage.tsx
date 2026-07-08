import { useState } from "react";

import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { ClusterCardsGrid } from "@/features/dashboard/components/clusters/cluster-cards-grid";
import { ClusterDetailDrawer } from "@/features/dashboard/components/drawers/cluster-detail-drawer";
import { useDashboardHome } from "@/features/dashboard/hooks/use-dashboard";
import { useClusters } from "@/hooks/use-clusters";

export function DashboardClustersPage() {
  const [clusterDrawerId, setClusterDrawerId] = useState<string | null>(null);
  const { data: dashboardData, isLoading: dashboardLoading } = useDashboardHome();
  const { data: clustersData, isLoading, isError, refetch } = useClusters({
    page: 1,
    page_size: 50,
  });

  const clusters = (dashboardData?.cluster_summary.length ?? 0) >= 10
      ? dashboardData!.cluster_summary
      : (clustersData?.items ?? []).map((cluster) => ({
          id: cluster.id,
          title: cluster.title,
          complaint_count: cluster.complaint_count,
          average_severity: cluster.average_severity,
          priority_score: cluster.impact_score ?? Math.round((cluster.priority_score ?? 0) * 100),
          village_name: cluster.village_name,
          department: cluster.recommended_department ?? cluster.department,
          latest_complaint_date: cluster.latest_complaint_date,
          representative_complaint_id: cluster.representative_complaint_id,
        }));

  if (isLoading || dashboardLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Cluster Intelligence" description="Duplicate clusters and civic hotspots" />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load clusters"
        description="Could not retrieve cluster intelligence."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cluster Intelligence"
        description="AI-detected duplicate complaint clusters ranked by severity and priority"
      />
      <ClusterCardsGrid clusters={clusters} onQuickView={setClusterDrawerId} />
      <ClusterDetailDrawer
        clusterId={clusterDrawerId}
        open={Boolean(clusterDrawerId)}
        onOpenChange={(open) => !open && setClusterDrawerId(null)}
      />
    </div>
  );
}
