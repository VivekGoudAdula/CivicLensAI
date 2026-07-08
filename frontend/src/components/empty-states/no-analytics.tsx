import { BarChart3 } from "lucide-react";

import { EmptyState } from "@/components/empty-states/empty-state";

export function NoAnalyticsEmptyState() {
  return (
    <EmptyState
      icon={BarChart3}
      title="No analytics data"
      description="Analytics reports are generated periodically from complaints and recommendations. Check back after the next snapshot run."
    />
  );
}
