import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

import { PriorityBadge } from "@/components/priority/priority-badges";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PriorityClusterCard } from "@/types/priority";

interface AIPrioritySectionProps {
  priorities: PriorityClusterCard[];
  onViewPriority?: (clusterId: string) => void;
}

export function AIPrioritySection({ priorities, onViewPriority }: AIPrioritySectionProps) {
  if (priorities.length === 0) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-sm text-muted-foreground">
          No AI priority rankings available yet. Priorities are generated after cluster analysis.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {priorities.slice(0, 6).map((item, index) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.04 }}
        >
          <Card className="overflow-hidden border-border/60 shadow-sm transition-shadow hover:shadow-md">
            <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0 pb-3">
              <div className="min-w-0">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <PriorityBadge score={item.priority_score} rank={item.priority_rank} />
                  {item.urgency_level ? (
                    <span className="rounded-full border px-2 py-0.5 text-xs capitalize">
                      {item.urgency_level}
                    </span>
                  ) : null}
                </div>
                <CardTitle className="text-base leading-snug">{item.title}</CardTitle>
                <p className="mt-1 text-sm text-muted-foreground">
                  {item.village_name ?? "Unknown village"} · {item.department ?? "Unassigned"}
                </p>
              </div>
              <div className="text-right text-sm">
                <p className="font-semibold">{item.priority_score}</p>
                <p className="text-xs text-muted-foreground">Priority</p>
                <p className="mt-2 font-medium">{item.impact_score}</p>
                <p className="text-xs text-muted-foreground">Impact</p>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 pt-0">
              {item.recommended_action ? (
                <p className="text-sm leading-relaxed text-muted-foreground line-clamp-2">
                  {item.recommended_action}
                </p>
              ) : null}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs text-muted-foreground">
                  Confidence:{" "}
                  {item.priority_confidence
                    ? `${Math.round(item.priority_confidence * 100)}%`
                    : "N/A"}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onViewPriority?.(item.id)}
                >
                  Quick Action
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
