import { AIConfidenceBadge } from "@/components/data-display/ai-confidence-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PriorityRecommendationPanel } from "@/types/priority";
import { PriorityBadge } from "@/components/priority/priority-badges";

export interface PriorityRecommendationCardProps {
  recommendation: PriorityRecommendationPanel;
}

export function PriorityRecommendationCard({ recommendation }: PriorityRecommendationCardProps) {
  return (
    <Card>
      <CardHeader className="space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle className="text-base">
            #{recommendation.priority_rank} {recommendation.cluster_title}
          </CardTitle>
          <PriorityBadge
            score={recommendation.priority_score}
            rank={recommendation.priority_rank}
          />
        </div>
        <AIConfidenceBadge score={recommendation.confidence_score} />
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Why This Is Priority #{recommendation.priority_rank}
          </p>
          <p className="mt-1 leading-relaxed">{recommendation.why_priority_ranked_high}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Contributing Factors
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {recommendation.contributing_factors.map((factor) => (
              <span
                key={factor}
                className="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground"
              >
                {factor}
              </span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Recommended Action
          </p>
          <p className="mt-1 text-muted-foreground">{recommendation.recommended_action}</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Expected Impact
            </p>
            <p className="mt-1">{recommendation.expected_impact}</p>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Estimated Beneficiaries
            </p>
            <p className="mt-1">{recommendation.estimated_beneficiaries}</p>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {recommendation.estimated_resolution_time ? (
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Resolution Time
              </p>
              <p className="mt-1">{recommendation.estimated_resolution_time}</p>
            </div>
          ) : null}
          {recommendation.estimated_budget ? (
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Budget Range
              </p>
              <p className="mt-1">{recommendation.estimated_budget}</p>
            </div>
          ) : null}
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            AI Reasoning
          </p>
          <p className="mt-1 leading-relaxed text-muted-foreground">{recommendation.reasoning}</p>
        </div>
      </CardContent>
    </Card>
  );
}
