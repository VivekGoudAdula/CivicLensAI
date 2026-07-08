import type { PriorityClusterCard } from "@/types/priority";
import { PriorityRecommendationCard } from "@/components/priority/priority-recommendation-panel";
import { DashboardDrawer } from "@/features/dashboard/components/drawers/dashboard-drawer";
import { ImpactScoreBadge, PriorityBadge, RiskBadge } from "@/components/priority/priority-badges";

interface PriorityDetailDrawerProps {
  cluster: PriorityClusterCard | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function PriorityDetailDrawer({
  cluster,
  open,
  onOpenChange,
}: PriorityDetailDrawerProps) {
  return (
    <DashboardDrawer
      open={open}
      onOpenChange={onOpenChange}
      title={cluster?.title ?? "Priority Details"}
      description="AI-ranked constituency priority intelligence"
      size="xl"
    >
      {cluster ? (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <PriorityBadge score={cluster.priority_score} rank={cluster.priority_rank} />
            <ImpactScoreBadge score={cluster.impact_score} />
            <RiskBadge level={cluster.risk_level} />
          </div>
          <PriorityRecommendationCard
            recommendation={{
              cluster_id: cluster.id,
              cluster_title: cluster.title,
              priority_rank: cluster.priority_rank ?? 0,
              priority_score: cluster.priority_score,
              impact_score: cluster.impact_score,
              why_priority_ranked_high: cluster.recommended_action ?? "",
              contributing_factors: [],
              expected_impact: cluster.affected_population ?? "",
              estimated_beneficiaries: cluster.affected_population ?? "",
              recommended_action: cluster.recommended_action ?? "",
              estimated_resolution_time: null,
              estimated_budget: null,
              confidence_score: cluster.priority_confidence ?? 0,
              reasoning: "",
            }}
          />
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">No priority data selected.</p>
      )}
    </DashboardDrawer>
  );
}
