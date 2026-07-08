import { Badge } from "@/components/ui/badge";

export type PriorityLevel = "low" | "medium" | "high" | "critical" | "urgent";

const priorityVariant: Record<PriorityLevel, "neutral" | "info" | "warning" | "error"> = {
  low: "neutral",
  medium: "info",
  high: "warning",
  critical: "error",
  urgent: "error",
};

export function PriorityBadge({ priority }: { priority: PriorityLevel }) {
  return (
    <Badge variant={priorityVariant[priority]} className="capitalize">
      {priority}
    </Badge>
  );
}
