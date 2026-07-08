import { RefreshCw } from "lucide-react";

import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { DashboardGrid } from "@/components/layout/DashboardGrid";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { PriorityBreakdownTable } from "@/components/priority/priority-breakdown-table";
import { PriorityLeaderboard } from "@/components/priority/priority-leaderboard";
import { PriorityRecommendationCard } from "@/components/priority/priority-recommendation-panel";
import { PrimaryButton } from "@/components/ui/buttons";
import { AIPrioritySection } from "@/features/dashboard/components/priority/ai-priority-section";
import { PriorityDetailDrawer } from "@/features/dashboard/components/drawers/priority-detail-drawer";
import { usePriorityDashboard, useRerankPriorities } from "@/hooks/use-priority";
import { showErrorToast, showSuccessToast } from "@/components/feedback/toast";
import { formatDateTime } from "@/lib/complaint-utils";
import { useState } from "react";
import type { PriorityClusterCard } from "@/types/priority";

export function DashboardPriorityPage() {
  const { data, isLoading, isError, refetch } = usePriorityDashboard();
  const rerankMutation = useRerankPriorities();
  const [selectedCluster, setSelectedCluster] = useState<PriorityClusterCard | null>(null);

  const handleRerank = async () => {
    try {
      const response = await rerankMutation.mutateAsync(false);
      if (response.success) {
        showSuccessToast(
          "Priority rankings updated",
          `Analyzed ${response.clusters_analyzed} clusters`,
        );
      } else {
        showErrorToast("Priority recalculation completed with errors", response.message);
      }
    } catch {
      showErrorToast("Failed to recalculate priorities");
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Priority Center" description="AI-ranked constituency priorities" />
        <DashboardGrid columns={4}>
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </DashboardGrid>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Failed to load priority center"
        description="Could not retrieve AI priority intelligence."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Priority Center"
        description="Explainable AI priority rankings for government decision-making"
        actions={
          <PrimaryButton onClick={() => void handleRerank()} loading={rerankMutation.isPending}>
            <RefreshCw className="h-4 w-4" />
            Recalculate Priorities
          </PrimaryButton>
        }
      />

      {data.last_updated_at ? (
        <p className="text-sm text-muted-foreground">
          Last updated {formatDateTime(data.last_updated_at)}
        </p>
      ) : null}

      <AIPrioritySection
        priorities={data.top_priorities}
        onViewPriority={(id) => {
          const cluster = data.top_priorities.find((item) => item.id === id) ?? null;
          setSelectedCluster(cluster);
        }}
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <PriorityLeaderboard items={data.leaderboard} />
        <div className="space-y-4">
          {data.recommendations.map((recommendation) => (
            <PriorityRecommendationCard
              key={recommendation.cluster_id}
              recommendation={recommendation}
            />
          ))}
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <PriorityBreakdownTable title="Department-wise Priority" items={data.department_breakdown} />
        <PriorityBreakdownTable title="Village-wise Ranking" items={data.village_breakdown} />
      </div>

      <PriorityDetailDrawer
        cluster={selectedCluster}
        open={Boolean(selectedCluster)}
        onOpenChange={(open) => !open && setSelectedCluster(null)}
      />
    </div>
  );
}
