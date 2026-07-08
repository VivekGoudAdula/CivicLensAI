import { Lightbulb } from "lucide-react";

import { EmptyState } from "@/components/empty-states/empty-state";

export function NoRecommendationsEmptyState() {
  return (
    <EmptyState
      icon={Lightbulb}
      title="No recommendations available"
      description="AI-generated recommendations will appear after complaint clusters are analyzed and reviewed."
    />
  );
}
