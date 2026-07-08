import { Link } from "react-router-dom";

import { CategoryBadge } from "@/components/data-display/category-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { DashboardDrawer } from "@/features/dashboard/components/drawers/dashboard-drawer";
import { useComplaint } from "@/hooks/use-complaints";
import {
  formatComplaintStatus,
  formatDateTime,
  statusToVariant,
} from "@/lib/complaint-utils";

interface ComplaintDetailDrawerProps {
  complaintId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ComplaintDetailDrawer({
  complaintId,
  open,
  onOpenChange,
}: ComplaintDetailDrawerProps) {
  const { data, isLoading } = useComplaint(open && complaintId ? complaintId : undefined);

  return (
    <DashboardDrawer
      open={open}
      onOpenChange={onOpenChange}
      title={data?.title ?? "Complaint Details"}
      description={data ? `${data.village_name} · ${formatDateTime(data.submitted_at)}` : undefined}
      size="xl"
    >
      {isLoading ? (
        <SkeletonCard />
      ) : data ? (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <StatusChip
              label={formatComplaintStatus(data.status)}
              variant={statusToVariant(data.status)}
            />
            <CategoryBadge category={data.category_name} />
            <span className="rounded-full border px-2 py-0.5 text-xs capitalize">
              {data.priority} priority
            </span>
          </div>
          <p className="text-sm leading-relaxed text-muted-foreground">{data.description}</p>
          {data.ai_analysis ? (
            <div className="rounded-xl border bg-muted/30 p-4">
              <p className="text-sm font-medium">AI Summary</p>
              <p className="mt-2 text-sm">{data.ai_analysis.summary}</p>
              <p className="mt-2 text-xs text-muted-foreground">
                Department: {data.ai_analysis.responsible_department} · Confidence:{" "}
                {Math.round(data.ai_analysis.confidence_score * 100)}%
              </p>
            </div>
          ) : null}
          <Link
            to={`/dashboard/complaints/${data.id}`}
            className="text-sm font-medium text-primary hover:underline"
            onClick={() => onOpenChange(false)}
          >
            Open full complaint page →
          </Link>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">Complaint not found.</p>
      )}
    </DashboardDrawer>
  );
}
