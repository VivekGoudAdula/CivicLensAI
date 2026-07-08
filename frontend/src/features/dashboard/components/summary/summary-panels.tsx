import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type {
  DashboardDepartmentSummary,
  DashboardVillageSummary,
} from "@/features/dashboard/types/dashboard";

interface DepartmentSummaryPanelProps {
  items: DashboardDepartmentSummary[];
}

export function DepartmentSummaryPanel({ items }: DepartmentSummaryPanelProps) {
  return (
    <Card className="border-border/60 shadow-sm">
      <CardHeader>
        <CardTitle className="text-base">Department Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No department data available.</p>
        ) : (
          items.map((item) => (
            <div
              key={item.department}
              className="flex items-center justify-between rounded-lg border bg-muted/20 px-3 py-2 text-sm"
            >
              <div>
                <p className="font-medium">{item.department}</p>
                <p className="text-xs text-muted-foreground">
                  {item.complaint_count} complaints · {item.cluster_count} clusters
                </p>
              </div>
              <span className="text-xs font-semibold text-primary">
                Avg P{item.average_priority_score}
              </span>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}

interface VillageSummaryPanelProps {
  items: DashboardVillageSummary[];
}

export function VillageSummaryPanel({ items }: VillageSummaryPanelProps) {
  return (
    <Card className="border-border/60 shadow-sm">
      <CardHeader>
        <CardTitle className="text-base">Village Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No village data available.</p>
        ) : (
          items.map((item) => (
            <div
              key={item.village_name}
              className="flex items-center justify-between rounded-lg border bg-muted/20 px-3 py-2 text-sm"
            >
              <div>
                <p className="font-medium">{item.village_name}</p>
                <p className="text-xs text-muted-foreground">
                  {item.complaint_count} complaints · {item.cluster_count} clusters
                </p>
              </div>
              <span className="text-xs font-semibold text-primary">
                Avg P{item.average_priority_score}
              </span>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
