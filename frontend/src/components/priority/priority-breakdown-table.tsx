import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PriorityBreakdownItem } from "@/types/priority";

export interface PriorityBreakdownTableProps {
  title: string;
  items: PriorityBreakdownItem[];
}

export function PriorityBreakdownTable({ title, items }: PriorityBreakdownTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No breakdown data available.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Name</th>
                  <th className="pb-2 pr-4 font-medium">Clusters</th>
                  <th className="pb-2 pr-4 font-medium">Avg Priority</th>
                  <th className="pb-2 font-medium">Avg Impact</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.label} className="border-b last:border-0">
                    <td className="py-3 pr-4 font-medium">{item.label}</td>
                    <td className="py-3 pr-4">{item.count}</td>
                    <td className="py-3 pr-4 font-mono">{item.average_priority_score}</td>
                    <td className="py-3 font-mono">{item.average_impact_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
