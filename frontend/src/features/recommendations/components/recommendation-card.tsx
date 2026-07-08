import { motion } from "framer-motion";
import { AlertTriangle, Building2, MapPin, Sparkles, Target, Users } from "lucide-react";

import { AIConfidenceBadge } from "@/components/data-display/ai-confidence-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { MpDevelopmentWorkItem } from "@/features/recommendations/types/recommendation";
import { cn } from "@/lib/utils";

interface RecommendationCardProps {
  item: MpDevelopmentWorkItem;
  onQuickAction?: (item: MpDevelopmentWorkItem) => void;
}

function urgencyColor(urgency: string) {
  const key = urgency.toLowerCase();
  if (key === "critical" || key === "urgent") return "border-rose-500/40 bg-rose-500/5";
  if (key === "high") return "border-orange-500/40 bg-orange-500/5";
  if (key === "medium") return "border-amber-500/40 bg-amber-500/5";
  return "border-emerald-500/40 bg-emerald-500/5";
}

export function RecommendationCard({ item, onQuickAction }: RecommendationCardProps) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
    >
      <Card className={cn("h-full border shadow-sm transition-shadow hover:shadow-md", urgencyColor(item.urgency))}>
        <CardHeader className="space-y-3 pb-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="rounded-full bg-primary px-2.5 py-0.5 text-xs font-bold text-primary-foreground">
              #{item.priority_rank}
            </span>
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">P{item.priority_score}</span>
              <AIConfidenceBadge score={item.ai_confidence} />
            </div>
          </div>
          <CardTitle className="text-base leading-snug">{item.project_title}</CardTitle>
          <p className="text-sm text-muted-foreground">{item.executive_summary}</p>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div className="grid gap-2 sm:grid-cols-2">
            <div className="flex items-center gap-2 text-muted-foreground">
              <MapPin className="h-3.5 w-3.5" />
              {item.village}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Building2 className="h-3.5 w-3.5" />
              {item.department}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Target className="h-3.5 w-3.5" />
              Impact {item.impact_score}
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Users className="h-3.5 w-3.5" />
              {item.estimated_beneficiaries}
            </div>
          </div>

          <div className="rounded-lg border bg-background/70 p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">AI Reasoning</p>
            <p className="mt-1">{item.reason}</p>
          </div>

          <div className="grid gap-2 sm:grid-cols-2">
            <div>
              <p className="text-xs text-muted-foreground">Budget</p>
              <p className="font-medium">{item.estimated_budget}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Timeline</p>
              <p className="font-medium">{item.estimated_resolution_time}</p>
            </div>
          </div>

          <div className="flex items-start gap-2 rounded-lg border border-rose-500/20 bg-rose-500/5 p-3">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-rose-500" />
            <div>
              <p className="text-xs font-semibold text-rose-600">Risk if Ignored</p>
              <p className="mt-0.5 text-muted-foreground">{item.risk_if_ignored}</p>
            </div>
          </div>

          <Button variant="outline" size="sm" className="w-full" onClick={() => onQuickAction?.(item)}>
            <Sparkles className="h-4 w-4" />
            {item.recommended_action}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}
