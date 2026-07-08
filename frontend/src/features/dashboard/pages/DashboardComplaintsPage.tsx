import { useMemo, useState } from "react";

import { ErrorState } from "@/components/empty-states/error-state";
import { NoComplaintsEmptyState } from "@/components/empty-states/no-complaints";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonTable } from "@/components/loading/skeleton-table";
import { DashboardComplaintsTable } from "@/features/dashboard/components/complaints/dashboard-complaints-table";
import {
  AIAnalysisDrawer,
} from "@/features/dashboard/components/drawers/ai-analysis-drawer";
import { ComplaintDetailDrawer } from "@/features/dashboard/components/drawers/complaint-detail-drawer";
import {
  ImageAnalysisDrawer,
} from "@/features/dashboard/components/drawers/image-analysis-drawer";
import { useComplaint, useComplaints } from "@/hooks/use-complaints";

export function DashboardComplaintsPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);
  const [imageDrawerOpen, setImageDrawerOpen] = useState(false);

  const { data, isLoading, isError, refetch } = useComplaints({
    page: 1,
    page_size: 100,
  });

  const { data: selectedComplaint } = useComplaint(selectedId ?? undefined);

  const complaints = useMemo(() => data?.items ?? [], [data?.items]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Complaints Registry"
          description="Enterprise complaint intelligence with search, filters, and quick actions"
        />
        <SkeletonTable />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load complaints"
        description="Could not retrieve complaint registry."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Complaints Registry"
        description="Search, filter, and triage constituency complaints with AI-enriched metadata"
      />

      {complaints.length === 0 ? (
        <NoComplaintsEmptyState />
      ) : (
        <DashboardComplaintsTable
          complaints={complaints}
          pageSize={12}
          onViewDetails={(id) => setSelectedId(id)}
        />
      )}

      <ComplaintDetailDrawer
        complaintId={selectedId}
        open={Boolean(selectedId)}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedId(null);
          }
        }}
      />

      {selectedComplaint ? (
        <>
          <AIAnalysisDrawer
            complaint={selectedComplaint}
            open={aiDrawerOpen}
            onOpenChange={setAiDrawerOpen}
          />
          <ImageAnalysisDrawer
            complaint={selectedComplaint}
            open={imageDrawerOpen}
            onOpenChange={setImageDrawerOpen}
          />
        </>
      ) : null}
    </div>
  );
}
