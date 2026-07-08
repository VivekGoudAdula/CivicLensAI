import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { AlertTriangle } from "lucide-react";

export interface PriorityBadgeProps {
  score: number;
  rank?: number | null;
  className?: string;
}

function variantForScore(score: number): "neutral" | "info" | "warning" | "error" {
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

export function PriorityBadge({ score, rank, className }: PriorityBadgeProps) {
  return (
    <Badge variant={variantForScore(score)} className={cn("gap-1 font-mono", className)}>
      P{score}
      {rank ? ` · #${rank}` : ""}
    </Badge>
  );
}

export interface RiskBadgeProps {
  level?: string | null;
  className?: string;
}

function variantForRisk(level?: string | null): "neutral" | "info" | "warning" | "error" {
  const normalized = (level ?? "medium").toLowerCase();
  if (normalized === "critical") {
    return "error";
  }
  if (normalized === "high") {
    return "warning";
  }
  if (normalized === "medium") {
    return "info";
  }
  return "neutral";
}

export function RiskBadge({ level, className }: RiskBadgeProps) {
  return (
    <Badge variant={variantForRisk(level)} className={cn("gap-1 capitalize", className)}>
      <AlertTriangle className="h-3 w-3" aria-hidden="true" />
      {level ?? "Unknown"} Risk
    </Badge>
  );
}

export interface ImpactScoreBadgeProps {
  score: number;
  className?: string;
}

export function ImpactScoreBadge({ score, className }: ImpactScoreBadgeProps) {
  return (
    <Badge variant={variantForScore(score)} className={cn("font-mono", className)}>
      Impact {score}
    </Badge>
  );
}
