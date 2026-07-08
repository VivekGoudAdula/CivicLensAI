import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ActivityTimeline } from "@/features/dashboard/components/activity/activity-timeline";
import { ComplaintDetailDrawer } from "@/features/dashboard/components/drawers/complaint-detail-drawer";
import { ClusterDetailDrawer } from "@/features/dashboard/components/drawers/cluster-detail-drawer";
import { useDashboardActivities } from "@/features/dashboard/hooks/use-dashboard";
import type { DashboardActivityItem } from "@/features/dashboard/types/dashboard";
import { useState } from "react";

export function DashboardActivitiesPage() {
  const { data, isLoading, isError, refetch } = useDashboardActivities(200);
  const [complaintDrawerId, setComplaintDrawerId] = useState<string | null>(null);
  const [clusterDrawerId, setClusterDrawerId] = useState<string | null>(null);

  const handleSelect = (item: DashboardActivityItem) => {
    if (item.entity_type === "complaint") {
      setComplaintDrawerId(item.entity_id);
    } else if (item.entity_type === "cluster") {
      setClusterDrawerId(item.entity_id);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Recent Activities" description="Constituency activity timeline" />
        <SkeletonCard />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Failed to load activities"
        description="Could not retrieve activity feed."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Recent Activities"
        description="Chronological feed of complaints, AI analyses, clusters, and priority updates"
      />

      <Card className="border-border/60 shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">{data.total} recorded events</CardTitle>
        </CardHeader>
        <CardContent>
          <ActivityTimeline items={data.items} onSelect={handleSelect} />
        </CardContent>
      </Card>

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
    </div>
  );
}
