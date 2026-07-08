import { Link } from "react-router-dom";
import { ExternalLink, Eye } from "lucide-react";

import { CategoryBadge } from "@/components/data-display/category-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { DashboardDrawer } from "@/features/dashboard/components/drawers/dashboard-drawer";
import type { GisClusterMarker, GisComplaintPin } from "@/features/gis/types/gis";
import { Button } from "@/components/ui/button";
import { useComplaint } from "@/hooks/use-complaints";
import { formatComplaintStatus, formatDateTime, statusToVariant, toDataUrl } from "@/lib/complaint-utils";

interface MapPinDrawerProps {
  complaint: GisComplaintPin | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function MapPinDrawer({ complaint, open, onOpenChange }: MapPinDrawerProps) {
  const { data: detail } = useComplaint(open && complaint ? complaint.id : undefined);
  const imageSrc =
    detail?.image_base64 && detail.image_mime_type
      ? toDataUrl(detail.image_base64, detail.image_mime_type)
      : null;

  return (
    <DashboardDrawer
      open={open}
      onOpenChange={onOpenChange}
      title={complaint?.title ?? "Complaint"}
      description={complaint?.village_name}
      size="xl"
    >
      {complaint ? (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <StatusChip
              label={formatComplaintStatus(complaint.status as never)}
              variant={statusToVariant(complaint.status as never)}
            />
            <CategoryBadge category={complaint.category} />
            <span className="rounded-full border px-2 py-0.5 text-xs capitalize">
              {complaint.priority} priority
            </span>
            {complaint.severity ? (
              <span className="rounded-full border px-2 py-0.5 text-xs">
                {complaint.severity} severity
              </span>
            ) : null}
          </div>

          <p className="text-sm text-muted-foreground">{complaint.description}</p>

          <div className="grid gap-2 text-sm sm:grid-cols-2">
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Department</p>
              <p className="font-medium">{complaint.department}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Cluster</p>
              <p className="font-medium">{complaint.cluster_title ?? "Unclustered"}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Coordinates</p>
              <p className="font-mono text-xs">
                {complaint.latitude.toFixed(5)}, {complaint.longitude.toFixed(5)}
              </p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Submitted</p>
              <p className="font-medium">{formatDateTime(complaint.submitted_at)}</p>
            </div>
          </div>

          {complaint.address ? (
            <p className="text-sm">
              <span className="font-medium">Address: </span>
              {complaint.address}
            </p>
          ) : null}

          {complaint.ai_summary ? (
            <div className="rounded-xl border bg-muted/30 p-4">
              <p className="text-sm font-medium">AI Summary</p>
              <p className="mt-1 text-sm text-muted-foreground">{complaint.ai_summary}</p>
              {complaint.ai_confidence != null ? (
                <p className="mt-2 text-xs text-muted-foreground">
                  Confidence: {Math.round(complaint.ai_confidence * 100)}%
                </p>
              ) : null}
            </div>
          ) : null}

          {imageSrc ? (
            <img
              src={imageSrc}
              alt="Complaint evidence"
              className="max-h-48 w-full rounded-lg border object-cover"
            />
          ) : null}

          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link to={`/complaints/${complaint.id}`} onClick={() => onOpenChange(false)}>
                <ExternalLink className="h-4 w-4" />
                Open Complaint
              </Link>
            </Button>
            <Button variant="default" size="sm" asChild>
              <Link
                to={`/dashboard/complaints/${complaint.id}`}
                onClick={() => onOpenChange(false)}
              >
                <Eye className="h-4 w-4" />
                Quick View
              </Link>
            </Button>
          </div>
        </div>
      ) : null}
    </DashboardDrawer>
  );
}

interface MapClusterDrawerProps {
  cluster: GisClusterMarker | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function MapClusterDrawer({ cluster, open, onOpenChange }: MapClusterDrawerProps) {
  return (
    <DashboardDrawer
      open={open}
      onOpenChange={onOpenChange}
      title={cluster?.title ?? "Cluster"}
      description={`${cluster?.complaint_count ?? 0} complaints`}
      size="lg"
    >
      {cluster ? (
        <div className="space-y-3 text-sm">
          <div className="grid gap-2 sm:grid-cols-2">
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Average Priority</p>
              <p className="text-lg font-semibold">{cluster.average_priority}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Cluster Score</p>
              <p className="text-lg font-semibold">{cluster.cluster_score}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Highest Severity</p>
              <p className="font-medium">{cluster.highest_severity ?? "Unknown"}</p>
            </div>
            <div className="rounded-lg border p-3">
              <p className="text-muted-foreground">Village</p>
              <p className="font-medium">{cluster.village_name ?? "Multiple"}</p>
            </div>
          </div>
          <Button variant="outline" size="sm" asChild>
            <Link to={`/civic-insights/clusters/${cluster.id}`} onClick={() => onOpenChange(false)}>
              View Cluster Intelligence
            </Link>
          </Button>
        </div>
      ) : null}
    </DashboardDrawer>
  );
}
