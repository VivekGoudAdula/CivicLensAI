import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Copy } from "lucide-react";

export interface DuplicateBadgeProps {
  className?: string;
}

export function DuplicateBadge({ className }: DuplicateBadgeProps) {
  return (
    <Badge variant="warning" className={cn("gap-1", className)}>
      <Copy className="h-3 w-3" aria-hidden="true" />
      Duplicate
    </Badge>
  );
}
