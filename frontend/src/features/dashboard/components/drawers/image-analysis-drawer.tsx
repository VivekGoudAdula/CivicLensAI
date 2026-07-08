import type { ComplaintDetail } from "@/types/complaint";
import { DashboardDrawer } from "@/features/dashboard/components/drawers/dashboard-drawer";
import { formatDateTime } from "@/lib/complaint-utils";

interface ImageAnalysisDrawerProps {
  complaint: ComplaintDetail | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ImageAnalysisDrawer({
  complaint,
  open,
  onOpenChange,
}: ImageAnalysisDrawerProps) {
  const analysis = complaint?.image_analysis;

  return (
    <DashboardDrawer
      open={open}
      onOpenChange={onOpenChange}
      title="Image Analysis"
      description={complaint?.title}
      size="lg"
    >
      {analysis ? (
        <div className="space-y-4 text-sm">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Primary Issue</p>
              <p className="font-medium">{analysis.primary_issue}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Severity</p>
              <p className="font-medium">{analysis.severity}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Suggested Department</p>
              <p className="font-medium">{analysis.suggested_department}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Confidence</p>
              <p className="font-medium">{Math.round(analysis.confidence_score * 100)}%</p>
            </div>
          </div>
          <div>
            <p className="font-medium">Description</p>
            <p className="mt-1 text-muted-foreground">{analysis.description}</p>
          </div>
          <div>
            <p className="font-medium">Immediate Action</p>
            <p className="mt-1 text-muted-foreground">{analysis.suggested_immediate_action}</p>
          </div>
          <div>
            <p className="font-medium">Reasoning</p>
            <p className="mt-1 text-muted-foreground">{analysis.reasoning}</p>
          </div>
          <p className="text-xs text-muted-foreground">
            Processed {formatDateTime(analysis.processed_at)} · {analysis.model_version}
          </p>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">Image analysis not available.</p>
      )}
    </DashboardDrawer>
  );
}
