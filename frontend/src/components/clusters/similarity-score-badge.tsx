import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export interface SimilarityScoreBadgeProps {
  score: number;
  className?: string;
}

function scoreVariant(score: number): "neutral" | "info" | "warning" | "error" {
  if (score >= 85) {
    return "error";
  }
  if (score >= 70) {
    return "warning";
  }
  if (score >= 40) {
    return "info";
  }
  return "neutral";
}

export function SimilarityScoreBadge({ score, className }: SimilarityScoreBadgeProps) {
  const rounded = Math.round(score);
  return (
    <Badge variant={scoreVariant(rounded)} className={cn("font-mono", className)}>
      {rounded}% match
    </Badge>
  );
}
