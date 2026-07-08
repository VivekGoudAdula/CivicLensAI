import type { LucideIcon } from "lucide-react";
import { TrendingDown, TrendingUp } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export interface KPICardProps {
  label: string;
  value: string | number;
  change?: number;
  icon?: LucideIcon;
  className?: string;
}

export function KPICard({ label, value, change, icon: Icon, className }: KPICardProps) {
  const isPositive = change !== undefined && change >= 0;

  return (
    <Card className={cn(className)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          {Icon ? <Icon className="h-4 w-4 text-muted-foreground" /> : null}
        </div>
        <p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
        {change !== undefined ? (
          <div
            className={cn(
              "mt-2 flex items-center gap-1 text-xs font-medium",
              isPositive ? "text-success" : "text-destructive",
            )}
          >
            {isPositive ? (
              <TrendingUp className="h-3.5 w-3.5" />
            ) : (
              <TrendingDown className="h-3.5 w-3.5" />
            )}
            {isPositive ? "+" : ""}
            {change}% from last period
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
