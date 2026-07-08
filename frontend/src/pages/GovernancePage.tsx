import { AlertTriangle, BarChart3, RefreshCw, ShieldAlert, Target } from "lucide-react";

import { KPICard } from "@/components/charts/kpi-card";
import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { DashboardGrid } from "@/components/layout/DashboardGrid";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { PriorityBreakdownTable } from "@/components/priority/priority-breakdown-table";
import { PriorityClusterCardView } from "@/components/priority/priority-cluster-card";
import { PriorityLeaderboard } from "@/components/priority/priority-leaderboard";
import { PriorityRecommendationCard } from "@/components/priority/priority-recommendation-panel";
import { PrimaryButton } from "@/components/ui/buttons";
import { usePriorityDashboard, useRerankPriorities } from "@/hooks/use-priority";
import { formatDateTime } from "@/lib/complaint-utils";
import { showErrorToast, showSuccessToast } from "@/components/feedback/toast";

export function GovernancePage() {
  const { data, isLoading, isError, refetch } = usePriorityDashboard();
  const rerankMutation = useRerankPriorities();

  const handleRerank = async () => {
    try {
      const response = await rerankMutation.mutateAsync(false);
      if (response.success) {
        showSuccessToast(
          "Priority rankings updated",
          `Analyzed ${response.clusters_analyzed} clusters, updated ${response.ranks_updated} ranks`,
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
        <PageHeader
          title="Governance Priority Dashboard"
          description="AI-powered constituency priority intelligence"
        />
        <DashboardGrid columns={4}>
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </DashboardGrid>
        <SkeletonCard />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Failed to load priority dashboard"
        description="Could not retrieve AI priority rankings from the API."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Governance Priority Dashboard"
        description="Explainable AI priority rankings for constituency development planning"
        actions={
          <PrimaryButton onClick={() => void handleRerank()} loading={rerankMutation.isPending}>
            <RefreshCw className="h-4 w-4" />
            Recalculate Priorities
          </PrimaryButton>
        }
      />

      {data.last_updated_at ? (
        <p className="text-sm text-muted-foreground">
          Last priority update: {formatDateTime(data.last_updated_at)}
        </p>
      ) : null}

      <DashboardGrid columns={4}>
        <KPICard label="Analyzed Clusters" value={data.total_analyzed_clusters} icon={BarChart3} />
        <KPICard label="Critical Issues" value={data.critical_clusters} icon={ShieldAlert} />
        <KPICard label="High Urgency" value={data.high_urgency_clusters} icon={AlertTriangle} />
        <KPICard
          label="Avg Priority Score"
          value={data.average_priority_score.toFixed(1)}
          icon={Target}
        />
      </DashboardGrid>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">Top 10 Priority Issues</h2>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.top_priorities.map((cluster) => (
            <PriorityClusterCardView key={cluster.id} cluster={cluster} />
          ))}
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <PriorityLeaderboard items={data.leaderboard} />
        <PriorityLeaderboard items={data.highest_impact_areas} title="Highest Impact Areas" />
      </div>

      {data.critical_issues.length > 0 ? (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold">Critical Complaints</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {data.critical_issues.map((cluster) => (
              <PriorityClusterCardView key={cluster.id} cluster={cluster} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="space-y-4">
        <h2 className="text-lg font-semibold">AI Recommendations</h2>
        <div className="grid gap-4 xl:grid-cols-2">
          {data.recommendations.map((recommendation) => (
            <PriorityRecommendationCard
              key={recommendation.cluster_id}
              recommendation={recommendation}
            />
          ))}
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <PriorityBreakdownTable title="Department-wise Priority" items={data.department_breakdown} />
        <PriorityBreakdownTable title="Village-wise Ranking" items={data.village_breakdown} />
      </div>
    </div>
  );
}
