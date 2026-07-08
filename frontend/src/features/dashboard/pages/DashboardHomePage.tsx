import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Sparkles } from "lucide-react";

import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { PriorityRecommendationCard } from "@/components/priority/priority-recommendation-panel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ActivityTimeline } from "@/features/dashboard/components/activity/activity-timeline";
import { DashboardChartsGrid } from "@/features/dashboard/components/charts/dashboard-charts-grid";
import { ClusterCardsGrid } from "@/features/dashboard/components/clusters/cluster-cards-grid";
import { ClusterDetailDrawer } from "@/features/dashboard/components/drawers/cluster-detail-drawer";
import { ComplaintDetailDrawer } from "@/features/dashboard/components/drawers/complaint-detail-drawer";
import { PriorityDetailDrawer } from "@/features/dashboard/components/drawers/priority-detail-drawer";
import { AIInsightsPanel } from "@/features/dashboard/components/insights/ai-insights-panel";
import { DashboardKPIGrid } from "@/features/dashboard/components/kpi/dashboard-kpi-grid";
import { AIPrioritySection } from "@/features/dashboard/components/priority/ai-priority-section";
import { ComplaintHeatSummary } from "@/features/dashboard/components/summary/complaint-heat-summary";
import {
  DepartmentSummaryPanel,
  VillageSummaryPanel,
} from "@/features/dashboard/components/summary/summary-panels";
import { useDashboardHome } from "@/features/dashboard/hooks/use-dashboard";
import { formatDateTime } from "@/lib/complaint-utils";
import type { PriorityClusterCard } from "@/types/priority";

export function DashboardHomePage() {
  const { data, isLoading, isError, refetch } = useDashboardHome();
  const [complaintDrawerId, setComplaintDrawerId] = useState<string | null>(null);
  const [clusterDrawerId, setClusterDrawerId] = useState<string | null>(null);
  const [priorityCluster, setPriorityCluster] = useState<PriorityClusterCard | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="MP Command Center"
          description="AI-powered decision intelligence for constituency governance"
        />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Failed to load command center"
        description="Could not retrieve dashboard intelligence from the API."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="MP Command Center"
        description="Real-time constituency intelligence — complaints, clusters, priorities, and AI recommendations"
        actions={
          <Button variant="outline" asChild>
            <Link to="/dashboard/analytics">
              Analytics Overview
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        }
      />

      <p className="text-sm text-muted-foreground">
        Last updated {formatDateTime(data.last_updated_at)}
      </p>

      <DashboardKPIGrid kpis={data.kpis} />

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">AI Priority Overview</h2>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/dashboard/priority">View all</Link>
            </Button>
          </div>
          <AIPrioritySection
            priorities={data.top_priorities}
            onViewPriority={(id) => {
            setPriorityCluster(data.top_priorities.find((item) => item.id === id) ?? null);
          }}
          />
        </div>
        <AIInsightsPanel insights={data.ai_insights} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="min-h-[320px]">
          <ComplaintHeatSummary data={data.charts.village_wise_complaints} />
        </div>
        <Card className="border-border/60 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Recent Complaints</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/dashboard/complaints">View all</Link>
            </Button>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.recent_complaints.map((complaint) => (
              <button
                key={complaint.id}
                type="button"
                onClick={() => setComplaintDrawerId(complaint.id)}
                className="flex w-full items-start justify-between rounded-lg border p-3 text-left transition-colors hover:bg-muted/40"
              >
                <div className="min-w-0 pr-4">
                  <p className="truncate text-sm font-medium">{complaint.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {complaint.village_name} · {complaint.category_name}
                  </p>
                </div>
                <span className="shrink-0 text-xs capitalize text-muted-foreground">
                  {complaint.status.replace(/_/g, " ")}
                </span>
              </button>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border/60 shadow-sm">
          <CardHeader className="flex flex-row items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <CardTitle className="text-base">Recent AI Recommendations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {data.recommendations.map((recommendation) => (
              <PriorityRecommendationCard
                key={recommendation.cluster_id}
                recommendation={recommendation}
              />
            ))}
          </CardContent>
        </Card>
        <Card className="border-border/60 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Recent Activities</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/dashboard/activities">View timeline</Link>
            </Button>
          </CardHeader>
          <CardContent>
            <ActivityTimeline items={data.recent_activities} compact />
          </CardContent>
        </Card>
      </div>

      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Cluster Summary</h2>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/dashboard/clusters">View all</Link>
          </Button>
        </div>
        <ClusterCardsGrid
          clusters={data.cluster_summary}
          onQuickView={setClusterDrawerId}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <DepartmentSummaryPanel items={data.department_summary} />
        <VillageSummaryPanel items={data.village_summary} />
      </div>

      <DashboardChartsGrid charts={data.charts} variant="home" />

      <ComplaintDetailDrawer
        complaintId={complaintDrawerId}
        open={Boolean(complaintDrawerId)}
        onOpenChange={(open) => !open && setComplaintDrawerId(null)}
      />
      <ClusterDetailDrawer
        clusterId={clusterDrawerId}
        open={Boolean(clusterDrawerId)}
        onOpenChange={(open) => !open && setClusterDrawerId(null)}
      />
      <PriorityDetailDrawer
        cluster={priorityCluster}
        open={Boolean(priorityCluster)}
        onOpenChange={(open) => !open && setPriorityCluster(null)}
      />
    </div>
  );
}
