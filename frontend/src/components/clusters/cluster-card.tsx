import { Link } from "react-router-dom";

import { CategoryBadge } from "@/components/data-display/category-badge";
import { SeverityBadge } from "@/components/data-display/severity-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ClusterListItem } from "@/types/cluster";
import { formatDateTime } from "@/lib/complaint-utils";
import { cn } from "@/lib/utils";
import { MapPin, Users } from "lucide-react";

function statusVariant(
  status: ClusterListItem["status"],
): "success" | "warning" | "error" | "info" | "neutral" {
  switch (status) {
    case "open":
      return "info";
    case "analyzing":
      return "warning";
    case "assigned":
    case "recommended":
      return "success";
    case "resolved":
      return "neutral";
    default:
      return "neutral";
  }
}

function normalizeSeverity(value?: string | null): "low" | "medium" | "high" | "critical" {
  const normalized = (value ?? "medium").toLowerCase() as "low" | "medium" | "high" | "critical";
  if (["low", "medium", "high", "critical"].includes(normalized)) {
    return normalized;
  }
  return "medium";
}

export interface ClusterCardProps {
  cluster: ClusterListItem;
  className?: string;
}

export function ClusterCard({ cluster, className }: ClusterCardProps) {
  return (
    <Link to={`/civic-insights/clusters/${cluster.id}`} className={cn("block", className)}>
      <Card className="h-full transition-shadow hover:shadow-md">
        <CardHeader className="space-y-3">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <CardTitle className="text-base leading-snug">{cluster.title}</CardTitle>
            <StatusChip
              label={cluster.status.replace(/_/g, " ")}
              variant={statusVariant(cluster.status)}
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <CategoryBadge category={cluster.category.replace(/_/g, " ")} />
            {cluster.average_severity ? (
              <SeverityBadge severity={normalizeSeverity(cluster.average_severity)} />
            ) : null}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground line-clamp-2">
            {cluster.affected_area ?? cluster.theme}
          </p>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span>{cluster.complaint_count} complaints</span>
            </div>
            {cluster.village_name ? (
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <span className="truncate">{cluster.village_name}</span>
              </div>
            ) : null}
          </div>
          {cluster.latest_complaint_date ? (
            <p className="text-xs text-muted-foreground">
              Latest: {formatDateTime(cluster.latest_complaint_date)}
            </p>
          ) : null}
          <div className="flex flex-wrap gap-2">
            <span className="rounded-md bg-muted px-2 py-1 text-xs">
              Hotspot {(cluster.hotspot_score * 100).toFixed(0)}%
            </span>
            <span className="rounded-md bg-muted px-2 py-1 text-xs">
              Priority {(cluster.priority_score * 100).toFixed(0)}%
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
