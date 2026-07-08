import { memo } from "react";

import { BarChartWrapper } from "@/components/charts/bar-chart";
import { LineChartWrapper } from "@/components/charts/line-chart";
import { PieChartWrapper } from "@/components/charts/pie-chart";
import type { DashboardCharts } from "@/features/dashboard/types/dashboard";

interface DashboardChartsGridProps {
  charts: DashboardCharts;
  variant?: "home" | "analytics";
}

function toLineData(points: { date: string; count: number }[]) {
  return points.map((point) => ({ name: point.date, value: point.count }));
}

export const DashboardChartsGrid = memo(function DashboardChartsGrid({
  charts,
  variant = "home",
}: DashboardChartsGridProps) {
  const showAll = variant === "analytics";

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <div className="min-h-[280px]">
        <BarChartWrapper
          title="Complaints by Category"
          data={charts.complaints_by_category}
          color="hsl(var(--chart-1))"
        />
      </div>
      <div className="min-h-[280px]">
        <BarChartWrapper
          title="Complaints by Department"
          data={charts.complaints_by_department}
          color="hsl(var(--chart-2))"
        />
      </div>
      <div className="min-h-[280px]">
        <PieChartWrapper
          title="Priority Distribution"
          data={charts.priority_distribution}
        />
      </div>
      <div className="min-h-[280px]">
        <PieChartWrapper
          title="Severity Distribution"
          data={charts.severity_distribution}
        />
      </div>
      <div className="min-h-[280px]">
        <BarChartWrapper
          title="Village-wise Complaints"
          data={charts.village_wise_complaints}
          color="hsl(var(--chart-3))"
        />
      </div>
      <div className="min-h-[280px]">
        <BarChartWrapper
          title="Department Workload"
          data={charts.department_workload}
          color="hsl(var(--chart-4))"
        />
      </div>

      {showAll ? (
        <>
          <div className="min-h-[280px] md:col-span-2 xl:col-span-3">
            <LineChartWrapper
              title="Complaint Trend (Daily)"
              data={toLineData(charts.complaint_trend_daily)}
            />
          </div>
          <div className="min-h-[280px]">
            <LineChartWrapper
              title="Weekly Trend"
              data={toLineData(charts.complaint_trend_weekly)}
            />
          </div>
          <div className="min-h-[280px]">
            <LineChartWrapper
              title="Monthly Trend"
              data={toLineData(charts.complaint_trend_monthly)}
            />
          </div>
          <div className="min-h-[280px]">
            <BarChartWrapper title="Top Categories" data={charts.top_categories} />
          </div>
          <div className="min-h-[280px]">
            <BarChartWrapper title="Top Villages" data={charts.top_villages} />
          </div>
          <div className="min-h-[280px]">
            <BarChartWrapper title="Top Departments" data={charts.top_departments} />
          </div>
        </>
      ) : (
        <div className="min-h-[280px] md:col-span-2">
          <LineChartWrapper
            title="Complaint Trend (14 Days)"
            data={toLineData(charts.complaint_trend_daily)}
          />
        </div>
      )}
    </div>
  );
});
