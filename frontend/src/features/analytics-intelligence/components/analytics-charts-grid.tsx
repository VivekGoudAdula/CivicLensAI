import { memo } from "react";

import { BarChartWrapper } from "@/components/charts/bar-chart";
import { LineChartWrapper } from "@/components/charts/line-chart";
import { PieChartWrapper } from "@/components/charts/pie-chart";
import type { IntelligenceCharts } from "@/features/analytics-intelligence/types/analytics";

function toLine(points: { date: string; count: number }[]) {
  return points.map((p) => ({ name: p.date, value: p.count }));
}

interface AnalyticsChartsGridProps {
  charts: IntelligenceCharts;
  chartRefs?: Record<string, (el: HTMLDivElement | null) => void>;
}

export const AnalyticsChartsGrid = memo(function AnalyticsChartsGrid({
  charts,
  chartRefs,
}: AnalyticsChartsGridProps) {
  const wrap = (id: string, node: React.ReactNode) => (
    <div
      ref={chartRefs?.[id]}
      data-chart-id={id}
      className="min-h-[280px] rounded-xl border bg-card p-1 shadow-sm"
    >
      {node}
    </div>
  );

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {wrap(
        "trend-daily",
        <LineChartWrapper title="Complaint Trend (Daily)" data={toLine(charts.complaint_trend_daily)} />,
      )}
      {wrap(
        "trend-weekly",
        <LineChartWrapper title="Complaint Trend (Weekly)" data={toLine(charts.complaint_trend_weekly)} />,
      )}
      {wrap(
        "trend-monthly",
        <LineChartWrapper title="Complaint Trend (Monthly)" data={toLine(charts.complaint_trend_monthly)} />,
      )}
      {wrap(
        "categories",
        <BarChartWrapper title="Complaint Categories" data={charts.complaint_categories} />,
      )}
      {wrap(
        "departments",
        <BarChartWrapper title="Department Distribution" data={charts.department_distribution} />,
      )}
      {wrap(
        "villages",
        <BarChartWrapper title="Village Comparison" data={charts.village_comparison} color="hsl(var(--chart-3))" />,
      )}
      {wrap(
        "priority",
        <PieChartWrapper title="Priority Distribution" data={charts.priority_distribution} />,
      )}
      {wrap(
        "severity",
        <PieChartWrapper title="Severity Distribution" data={charts.severity_distribution} />,
      )}
      {wrap(
        "cluster-size",
        <BarChartWrapper title="Cluster Size Distribution" data={charts.cluster_size_distribution} />,
      )}
      {wrap(
        "resolution",
        <PieChartWrapper title="Resolution Status" data={charts.resolution_status} />,
      )}
      {wrap("top-villages", <BarChartWrapper title="Top Villages" data={charts.top_villages} />)}
      {wrap(
        "top-departments",
        <BarChartWrapper title="Top Departments" data={charts.top_departments} />,
      )}
      {wrap(
        "timeline",
        <LineChartWrapper title="Complaint Timeline (Cumulative)" data={toLine(charts.complaint_timeline)} />,
      )}
      {wrap(
        "ai-confidence",
        <BarChartWrapper
          title="AI Confidence Distribution"
          data={charts.ai_confidence_distribution}
          color="hsl(var(--chart-2))"
        />,
      )}
    </div>
  );
});
