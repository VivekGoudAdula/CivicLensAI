import { Badge } from "@/components/ui/badge";

export type SeverityLevel = "low" | "medium" | "high" | "critical";

const severityVariant: Record<SeverityLevel, "neutral" | "info" | "warning" | "error"> = {
  low: "neutral",
  medium: "info",
  high: "warning",
  critical: "error",
};

export function SeverityBadge({ severity }: { severity: SeverityLevel }) {
  return (
    <Badge variant={severityVariant[severity]} className="capitalize">
      {severity}
    </Badge>
  );
}
