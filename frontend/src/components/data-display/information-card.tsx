import type { LucideIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface InformationCardProps {
  title: string;
  content: string;
  icon?: LucideIcon;
  footer?: string;
}

export function InformationCard({
  title,
  content,
  icon: Icon,
  footer,
}: InformationCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-3">
        {Icon ? (
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-info/10">
            <Icon className="h-4 w-4 text-info" aria-hidden="true" />
          </div>
        ) : null}
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-relaxed text-muted-foreground">{content}</p>
        {footer ? (
          <p className="mt-3 text-xs text-muted-foreground">{footer}</p>
        ) : null}
      </CardContent>
    </Card>
  );
}
