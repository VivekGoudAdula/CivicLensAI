import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

import { ComplaintAIInsightsPanel } from "@/components/complaints/complaint-ai-insights-panel";
import { ComplaintImageIntelligencePanel } from "@/components/complaints/complaint-image-intelligence-panel";
import { CategoryBadge } from "@/components/data-display/category-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useComplaint } from "@/hooks/use-complaints";
import {
  formatComplaintStatus,
  formatDateTime,
  statusToVariant,
} from "@/lib/complaint-utils";

export function DashboardComplaintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: complaint, isLoading, isError, refetch } = useComplaint(id);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (isError || !complaint) {
    return (
      <ErrorState
        title="Complaint not found"
        description="The requested complaint could not be loaded."
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" asChild className="mb-2">
        <Link to="/dashboard/complaints">
          <ArrowLeft className="h-4 w-4" />
          Back to Registry
        </Link>
      </Button>

      <PageHeader
        title={complaint.title}
        description={`${complaint.village_name} · Submitted ${formatDateTime(complaint.submitted_at)}`}
      />

      <div className="flex flex-wrap gap-2">
        <StatusChip
          label={formatComplaintStatus(complaint.status)}
          variant={statusToVariant(complaint.status)}
        />
        <CategoryBadge category={complaint.category_name} />
        <span className="rounded-full border px-2 py-0.5 text-xs capitalize">
          {complaint.priority} priority
        </span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Citizen Report</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed text-muted-foreground">{complaint.description}</p>
        </CardContent>
      </Card>

      <ComplaintAIInsightsPanel complaint={complaint} />
      <ComplaintImageIntelligencePanel complaint={complaint} />
    </div>
  );
}
