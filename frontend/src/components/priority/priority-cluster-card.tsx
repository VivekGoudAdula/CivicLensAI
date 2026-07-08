import { Link } from "react-router-dom";

import { DepartmentBadge } from "@/components/data-display/department-badge";
import { SeverityBadge } from "@/components/data-display/severity-badge";
import {
  ImpactScoreBadge,
  PriorityBadge,
  RiskBadge,
} from "@/components/priority/priority-badges";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PriorityClusterCard } from "@/types/priority";
import { formatDateTime } from "@/lib/complaint-utils";
import { cn } from "@/lib/utils";
import { MapPin, Users } from "lucide-react";

function normalizeSeverity(value?: string | null): "low" | "medium" | "high" | "critical" {
  const normalized = (value ?? "medium").toLowerCase() as "low" | "medium" | "high" | "critical";
  if (["low", "medium", "high", "critical"].includes(normalized)) {
    return normalized;
  }
  return "medium";
}

export interface PriorityClusterCardViewProps {
  cluster: PriorityClusterCard;
  className?: string;
}

export function PriorityClusterCardView({ cluster, className }: PriorityClusterCardViewProps) {
  return (
    <Link to={`/civic-insights/clusters/${cluster.id}`} className={cn("block", className)}>
      <Card className="h-full transition-shadow hover:shadow-md">
        <CardHeader className="space-y-3">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <CardTitle className="text-base leading-snug">{cluster.title}</CardTitle>
            <PriorityBadge score={cluster.priority_score} rank={cluster.priority_rank} />
          </div>
          <div className="flex flex-wrap gap-2">
            <ImpactScoreBadge score={cluster.impact_score} />
            {cluster.urgency_level ? (
              <SeverityBadge severity={normalizeSeverity(cluster.urgency_level)} />
            ) : null}
            {cluster.risk_level ? <RiskBadge level={cluster.risk_level} /> : null}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {cluster.recommended_action ? (
            <p className="text-sm text-muted-foreground line-clamp-3">
              {cluster.recommended_action}
            </p>
          ) : null}
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
          {cluster.department ? (
            <DepartmentBadge name={cluster.department} />
          ) : null}
          {cluster.priority_updated_at ? (
            <p className="text-xs text-muted-foreground">
              Updated {formatDateTime(cluster.priority_updated_at)}
            </p>
          ) : null}
        </CardContent>
      </Card>
    </Link>
  );
}
