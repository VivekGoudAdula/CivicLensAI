import { Link } from "react-router-dom";

import { SkeletonCard } from "@/components/loading/skeleton-card";
import { PriorityRecommendationCard } from "@/components/priority/priority-recommendation-panel";
import { DashboardDrawer } from "@/features/dashboard/components/drawers/dashboard-drawer";
import { useCluster } from "@/hooks/use-clusters";

interface ClusterDetailDrawerProps {
  clusterId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ClusterDetailDrawer({
  clusterId,
  open,
  onOpenChange,
}: ClusterDetailDrawerProps) {
  const { data, isLoading } = useCluster(open && clusterId ? clusterId : undefined);

  return (
    <DashboardDrawer
      open={open}
      onOpenChange={onOpenChange}
      title={data?.title ?? "Cluster Details"}
      description={data ? `${data.complaint_count} linked complaints` : undefined}
      size="xl"
    >
      {isLoading ? (
        <SkeletonCard />
      ) : data ? (
        <div className="space-y-4">
          <p className="text-sm leading-relaxed text-muted-foreground">{data.description}</p>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border p-3 text-sm">
              <p className="text-muted-foreground">Village</p>
              <p className="font-medium">{data.village_name ?? data.village_names.join(", ")}</p>
            </div>
            <div className="rounded-lg border p-3 text-sm">
              <p className="text-muted-foreground">Department</p>
              <p className="font-medium">{data.recommended_department ?? data.department ?? "Unassigned"}</p>
            </div>
          </div>
          {data.priority_analysis ? (
            <PriorityRecommendationCard
              recommendation={{
                cluster_id: data.id,
                cluster_title: data.title,
                priority_rank: data.priority_analysis.priority_rank ?? 0,
                priority_score: data.priority_analysis.priority_score,
                impact_score: data.priority_analysis.impact_score,
                why_priority_ranked_high: data.priority_analysis.why_priority_ranked_high,
                contributing_factors: data.priority_analysis.contributing_factors,
                expected_impact: data.priority_analysis.expected_impact,
                estimated_beneficiaries: data.priority_analysis.estimated_beneficiaries,
                recommended_action: data.priority_analysis.recommended_action,
                estimated_resolution_time: data.priority_analysis.estimated_resolution_time,
                estimated_budget: data.priority_analysis.estimated_budget_range,
                confidence_score: data.priority_analysis.confidence_score,
                reasoning: data.priority_analysis.reasoning,
              }}
            />
          ) : null}
          <Link
            to={`/civic-insights/clusters/${data.id}`}
            className="text-sm font-medium text-primary hover:underline"
            onClick={() => onOpenChange(false)}
          >
            Open cluster intelligence page →
          </Link>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">Cluster not found.</p>
      )}
    </DashboardDrawer>
  );
}
