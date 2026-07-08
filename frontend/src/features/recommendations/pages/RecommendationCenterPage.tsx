import { RefreshCw, Sparkles } from "lucide-react";

import { ErrorState } from "@/components/empty-states/error-state";
import { NoRecommendationsEmptyState } from "@/components/empty-states/no-recommendations";
import { showErrorToast, showSuccessToast } from "@/components/feedback/toast";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { PrimaryButton } from "@/components/ui/buttons";
import { DecisionTimeline, ExecutiveBrief } from "@/features/recommendations/components/decision-timeline";
import { RecommendationCard } from "@/features/recommendations/components/recommendation-card";
import {
  useGenerateRecommendations,
  useRecommendationCenter,
} from "@/features/recommendations/hooks/use-recommendations";
import { formatDateTime } from "@/lib/complaint-utils";

export function RecommendationCenterPage() {
  const { data, isLoading, isError, refetch } = useRecommendationCenter();
  const generateMutation = useGenerateRecommendations();

  const handleGenerate = async () => {
    try {
      const response = await generateMutation.mutateAsync(false);
      if (response.success) {
        showSuccessToast("AI recommendations updated", response.message);
        void refetch();
      } else {
        showErrorToast("Generation failed", response.message);
      }
    } catch {
      showErrorToast("Failed to generate recommendations");
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="AI Recommendation Center" description="MP decision support powered by Gemini" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
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
        title="Failed to load recommendation center"
        description="Could not retrieve AI decision intelligence."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="AI Recommendation Center"
        description="What should the MP prioritize today? — Explainable Gemini-powered development recommendations"
        actions={
          <PrimaryButton onClick={() => void handleGenerate()} loading={generateMutation.isPending}>
            <RefreshCw className="h-4 w-4" />
            Generate Recommendations
          </PrimaryButton>
        }
      />

      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <span className="inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5">
          <Sparkles className="h-3.5 w-3.5" />
          {data.engine} · {data.model_version}
        </span>
        <span>Updated {formatDateTime(data.generated_at)}</span>
        {data.from_cache ? <span>Cached analysis</span> : null}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ExecutiveBrief brief={data.executive_brief} />
        </div>
        <DecisionTimeline summary={data.decision_timeline_summary} />
      </div>

      {data.recommendations.length === 0 ? (
        <NoRecommendationsEmptyState />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.recommendations.map((item) => (
            <RecommendationCard key={item.priority_rank} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
