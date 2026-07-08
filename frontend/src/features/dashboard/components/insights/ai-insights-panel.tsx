import { motion } from "framer-motion";
import {
  AlertCircle,
  Lightbulb,
  Sparkles,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardAIInsights } from "@/features/dashboard/types/dashboard";

interface AIInsightsPanelProps {
  insights: DashboardAIInsights;
}

export function AIInsightsPanel({ insights }: AIInsightsPanelProps) {
  const sections = [
    {
      title: "Highest Risk Area",
      value: insights.highest_risk_area,
      icon: AlertCircle,
      color: "text-rose-600",
    },
    {
      title: "Most Common Issue",
      value: insights.most_common_issue,
      icon: TrendingUp,
      color: "text-amber-600",
    },
    {
      title: "Department Overload",
      value: insights.department_overload,
      icon: Users,
      color: "text-blue-600",
    },
    {
      title: "Fastest Growing Cluster",
      value: insights.fastest_growing_cluster ?? "No cluster data",
      icon: Zap,
      color: "text-violet-600",
    },
  ];

  return (
    <Card className="border-border/60 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Sparkles className="h-5 w-5 text-primary" />
          AI Insights
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-3 sm:grid-cols-2">
          {sections.map((section, index) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="rounded-xl border bg-muted/20 p-4"
            >
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <section.icon className={`h-4 w-4 ${section.color}`} />
                {section.title}
              </div>
              <p className="mt-2 text-sm font-semibold leading-snug">{section.value}</p>
            </motion.div>
          ))}
        </div>

        {insights.trending_complaints.length > 0 ? (
          <div>
            <p className="mb-2 text-sm font-medium text-muted-foreground">Trending Complaints</p>
            <div className="flex flex-wrap gap-2">
              {insights.trending_complaints.map((item) => (
                <span
                  key={item}
                  className="rounded-full border bg-background px-3 py-1 text-xs font-medium"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ) : null}

        {insights.suggested_actions.length > 0 ? (
          <div>
            <p className="mb-2 flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Lightbulb className="h-4 w-4" />
              AI Suggested Actions
            </p>
            <ul className="space-y-2">
              {insights.suggested_actions.map((action) => (
                <li
                  key={action}
                  className="rounded-lg border-l-2 border-primary bg-muted/30 px-3 py-2 text-sm"
                >
                  {action}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div>
          <p className="mb-2 text-sm font-medium text-muted-foreground">Today&apos;s Highlights</p>
          <ul className="space-y-1.5">
            {insights.todays_highlights.map((highlight) => (
              <li key={highlight} className="text-sm text-foreground/90">
                • {highlight}
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
