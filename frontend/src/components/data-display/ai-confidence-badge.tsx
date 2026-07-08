import { Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export function AIConfidenceBadge({
  score,
  className,
}: {
  score: number;
  className?: string;
}) {
  const percentage = Math.round(score * 100);
  const variant =
    percentage >= 80 ? "success" : percentage >= 60 ? "info" : "warning";

  return (
    <Badge variant={variant} className={cn("gap-1", className)}>
      <Sparkles className="h-3 w-3" aria-hidden="true" />
      AI {percentage}%
    </Badge>
  );
}
