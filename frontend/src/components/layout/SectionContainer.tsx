import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface SectionContainerProps {
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}

export function SectionContainer({
  title,
  description,
  children,
  className,
  action,
}: SectionContainerProps) {
  return (
    <section className={cn("space-y-4", className)} aria-labelledby={title ? "section-title" : undefined}>
      {(title || action) && (
        <div className="flex items-center justify-between gap-4">
          <div>
            {title ? (
              <h2 id="section-title" className="text-lg font-semibold tracking-tight">
                {title}
              </h2>
            ) : null}
            {description ? (
              <p className="mt-1 text-sm text-muted-foreground">{description}</p>
            ) : null}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
