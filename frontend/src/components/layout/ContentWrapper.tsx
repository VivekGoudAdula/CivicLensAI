import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface ContentWrapperProps {
  children: ReactNode;
  className?: string;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl" | "full";
}

const maxWidthMap = {
  sm: "max-w-2xl",
  md: "max-w-4xl",
  lg: "max-w-6xl",
  xl: "max-w-7xl",
  "2xl": "max-w-[1400px]",
  full: "max-w-full",
};

export function ContentWrapper({
  children,
  className,
  maxWidth = "2xl",
}: ContentWrapperProps) {
  return (
    <div className={cn("mx-auto w-full", maxWidthMap[maxWidth], className)}>
      {children}
    </div>
  );
}
