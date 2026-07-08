import { motion } from "framer-motion";
import {
  Brain,
  Camera,
  FilePlus2,
  GitBranchPlus,
  Layers,
  Sparkles,
  Target,
} from "lucide-react";

import { formatDateTime } from "@/lib/complaint-utils";
import type { ActivityType, DashboardActivityItem } from "@/features/dashboard/types/dashboard";
import { cn } from "@/lib/utils";

const ACTIVITY_ICONS: Record<ActivityType, typeof Brain> = {
  complaint_submitted: FilePlus2,
  ai_analysis_completed: Brain,
  image_analysis_completed: Camera,
  cluster_created: GitBranchPlus,
  cluster_updated: Layers,
  priority_updated: Target,
  recommendation_generated: Sparkles,
};

const ACTIVITY_COLORS: Record<ActivityType, string> = {
  complaint_submitted: "bg-blue-500/10 text-blue-600",
  ai_analysis_completed: "bg-violet-500/10 text-violet-600",
  image_analysis_completed: "bg-cyan-500/10 text-cyan-600",
  cluster_created: "bg-amber-500/10 text-amber-600",
  cluster_updated: "bg-orange-500/10 text-orange-600",
  priority_updated: "bg-rose-500/10 text-rose-600",
  recommendation_generated: "bg-emerald-500/10 text-emerald-600",
};

interface ActivityTimelineProps {
  items: DashboardActivityItem[];
  onSelect?: (item: DashboardActivityItem) => void;
  compact?: boolean;
}

export function ActivityTimeline({ items, onSelect, compact = false }: ActivityTimelineProps) {
  if (items.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No recent activity recorded yet.
      </p>
    );
  }

  return (
    <div className="relative space-y-0">
      <div className="absolute bottom-2 left-[18px] top-2 w-px bg-border" aria-hidden />
      {items.map((activity, index) => {
        const Icon = ACTIVITY_ICONS[activity.type];
        return (
          <motion.button
            key={activity.id}
            type="button"
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.03 }}
            onClick={() => onSelect?.(activity)}
            className={cn(
              "relative flex w-full gap-4 rounded-xl p-3 text-left transition-colors hover:bg-muted/50",
              onSelect && "cursor-pointer",
            )}
          >
            <div
              className={cn(
                "relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border bg-background shadow-sm",
                ACTIVITY_COLORS[activity.type],
              )}
            >
              <Icon className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-sm font-medium">{activity.title}</p>
                <span className="text-xs text-muted-foreground">
                  {formatDateTime(activity.occurred_at)}
                </span>
              </div>
              <p className={cn("mt-0.5 text-sm text-muted-foreground", compact && "line-clamp-1")}>
                {activity.description}
              </p>
            </div>
          </motion.button>
        );
      })}
    </div>
  );
}
