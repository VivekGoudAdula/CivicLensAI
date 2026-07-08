import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ChartContainer } from "@/components/charts/chart-container";
import type { ChartDataPoint } from "@/features/dashboard/types/dashboard";

const HEAT_COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
];

interface ComplaintHeatSummaryProps {
  data: ChartDataPoint[];
}

export function ComplaintHeatSummary({ data }: ComplaintHeatSummaryProps) {
  const topData = data.slice(0, 8);

  return (
    <ChartContainer
      title="Complaint Heat Summary"
      description="Geographic concentration by village"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={topData} layout="vertical" margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
          <XAxis type="number" tick={{ fontSize: 12 }} />
          <YAxis
            type="category"
            dataKey="name"
            width={100}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--popover))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
            }}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {topData.map((entry, index) => (
              <Cell key={entry.name} fill={HEAT_COLORS[index % HEAT_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
}
