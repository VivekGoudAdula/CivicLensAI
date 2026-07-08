import { Link } from "react-router-dom";

import { DepartmentBadge } from "@/components/data-display/department-badge";
import { PriorityBadge, ImpactScoreBadge } from "@/components/priority/priority-badges";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PriorityClusterCard } from "@/types/priority";

export interface PriorityLeaderboardProps {
  items: PriorityClusterCard[];
  title?: string;
}

export function PriorityLeaderboard({
  items,
  title = "Priority Leaderboard",
}: PriorityLeaderboardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No ranked clusters yet.</p>
        ) : (
          items.map((item) => (
            <Link
              key={item.id}
              to={`/civic-insights/clusters/${item.id}`}
              className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-3 transition-colors hover:bg-muted/50"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm text-muted-foreground">
                    #{item.priority_rank ?? "—"}
                  </span>
                  <p className="truncate font-medium">{item.title}</p>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {item.village_name ?? "Unknown village"} · {item.complaint_count} complaints
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <PriorityBadge score={item.priority_score} />
                <ImpactScoreBadge score={item.impact_score} />
                {item.department ? <DepartmentBadge name={item.department} /> : null}
              </div>
            </Link>
          ))
        )}
      </CardContent>
    </Card>
  );
}
