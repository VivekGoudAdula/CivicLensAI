import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { DashboardChartsGrid } from "@/features/dashboard/components/charts/dashboard-charts-grid";
import { AIInsightsPanel } from "@/features/dashboard/components/insights/ai-insights-panel";
import { DashboardKPIGrid } from "@/features/dashboard/components/kpi/dashboard-kpi-grid";
import { useDashboardAnalytics } from "@/features/dashboard/hooks/use-dashboard";

export function DashboardAnalyticsPage() {
  const { data, isLoading, isError, refetch } = useDashboardAnalytics();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Analytics Overview" description="Constituency trends and distributions" />
        <SkeletonCard />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Failed to load analytics"
        description="Could not retrieve analytics overview."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Analytics Overview"
        description="Comprehensive charts for complaints, departments, villages, and AI priority trends"
      />
      <DashboardKPIGrid kpis={data.kpis} />
      <AIInsightsPanel insights={data.ai_insights} />
      <DashboardChartsGrid charts={data.charts} variant="analytics" />
    </div>
  );
}
