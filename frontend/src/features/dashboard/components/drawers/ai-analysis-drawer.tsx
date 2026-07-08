import type { ComplaintDetail } from "@/types/complaint";
import { DashboardDrawer } from "@/features/dashboard/components/drawers/dashboard-drawer";
import { formatDateTime } from "@/lib/complaint-utils";

interface AIAnalysisDrawerProps {
  complaint: ComplaintDetail | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AIAnalysisDrawer({ complaint, open, onOpenChange }: AIAnalysisDrawerProps) {
  const analysis = complaint?.ai_analysis;

  return (
    <DashboardDrawer
      open={open}
      onOpenChange={onOpenChange}
      title="AI Analysis"
      description={complaint?.title}
      size="lg"
    >
      {analysis ? (
        <div className="space-y-4 text-sm">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Department</p>
              <p className="font-medium">{analysis.responsible_department}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Confidence</p>
              <p className="font-medium">{Math.round(analysis.confidence_score * 100)}%</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Severity</p>
              <p className="font-medium capitalize">{analysis.severity}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Urgency</p>
              <p className="font-medium capitalize">{analysis.urgency}</p>
            </div>
          </div>
          <div>
            <p className="font-medium">Summary</p>
            <p className="mt-1 text-muted-foreground">{analysis.summary}</p>
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
        <p className="text-sm text-muted-foreground">AI analysis not available for this complaint.</p>
      )}
    </DashboardDrawer>
  );
}
