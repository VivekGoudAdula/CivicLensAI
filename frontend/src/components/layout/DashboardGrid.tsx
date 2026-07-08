import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface DashboardGridProps {
  children: ReactNode;
  columns?: 1 | 2 | 3 | 4 | 5;
  className?: string;
}

const columnMap = {
  1: "grid-cols-1",
  2: "grid-cols-1 md:grid-cols-2",
  3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
  4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4",
  5: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5",
};

export function DashboardGrid({
  children,
  columns = 3,
  className,
}: DashboardGridProps) {
  return (
    <div className={cn("grid gap-4 md:gap-6", columnMap[columns], className)}>
      {children}
    </div>
  );
}
