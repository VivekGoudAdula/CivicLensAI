import { Link } from "react-router-dom";

import { DuplicateBadge } from "@/components/clusters/duplicate-badge";
import { SimilarityScoreBadge } from "@/components/clusters/similarity-score-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ClusterComplaintSummary } from "@/types/cluster";
import type { ComplaintStatus } from "@/types/complaint";
import { formatComplaintStatus, formatDateTime, statusToVariant } from "@/lib/complaint-utils";

export interface ClusterComplaintsListProps {
  complaints: ClusterComplaintSummary[];
  representativeComplaintId?: string | null;
  title?: string;
}

export function ClusterComplaintsList({
  complaints,
  representativeComplaintId,
  title = "Related Complaints",
}: ClusterComplaintsListProps) {
  if (complaints.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-muted-foreground">
          No related complaints in this cluster yet.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {complaints.map((complaint) => (
          <Link
            key={complaint.id}
            to={`/complaints/${complaint.id}`}
            className="block rounded-lg border p-4 transition-colors hover:bg-muted/50"
          >
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div className="space-y-1">
                <p className="font-medium">{complaint.title}</p>
                <p className="text-xs text-muted-foreground">
                  {complaint.village_name} · {formatDateTime(complaint.submitted_at)}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <StatusChip
                  label={formatComplaintStatus(complaint.status as ComplaintStatus)}
                  variant={statusToVariant(complaint.status as ComplaintStatus)}
                />
                {complaint.is_duplicate ? <DuplicateBadge /> : null}
                {complaint.duplicate_score != null && complaint.duplicate_score > 0 ? (
                  <SimilarityScoreBadge score={complaint.duplicate_score} />
                ) : null}
                {complaint.id === representativeComplaintId ? (
                  <span className="rounded-md bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                    Representative
                  </span>
                ) : null}
              </div>
            </div>
          </Link>
        ))}
      </CardContent>
    </Card>
  );
}
