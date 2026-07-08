import { motion } from "framer-motion";
import { Eye, Layers, MapPin } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDateTime } from "@/lib/complaint-utils";
import type { DashboardClusterSummary } from "@/features/dashboard/types/dashboard";

interface ClusterCardsGridProps {
  clusters: DashboardClusterSummary[];
  onQuickView?: (clusterId: string) => void;
}

export function ClusterCardsGrid({ clusters, onQuickView }: ClusterCardsGridProps) {
  if (clusters.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">No active clusters found.</p>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {clusters.map((cluster, index) => (
        <motion.div
          key={cluster.id}
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.04 }}
        >
          <Card className="h-full border-border/60 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="line-clamp-2 text-base">{cluster.title}</CardTitle>
                <span className="shrink-0 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary">
                  P{cluster.priority_score}
                </span>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center gap-4 text-muted-foreground">
                <span className="inline-flex items-center gap-1">
                  <Layers className="h-3.5 w-3.5" />
                  {cluster.complaint_count} complaints
                </span>
                {cluster.average_severity ? (
                  <span className="capitalize">{cluster.average_severity} severity</span>
                ) : null}
              </div>
              <div className="flex items-center gap-1 text-muted-foreground">
                <MapPin className="h-3.5 w-3.5" />
                {cluster.village_name ?? "Multiple villages"}
              </div>
              <p className="text-xs text-muted-foreground">
                Dept: {cluster.department ?? "Unassigned"}
              </p>
              {cluster.latest_complaint_date ? (
                <p className="text-xs text-muted-foreground">
                  Latest: {formatDateTime(cluster.latest_complaint_date)}
                </p>
              ) : null}
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => onQuickView?.(cluster.id)}
              >
                <Eye className="h-3.5 w-3.5" />
                Quick View
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
