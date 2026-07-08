import { Calendar, Sparkles } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface DecisionTimelineProps {
  summary: string;
}

export function DecisionTimeline({ summary }: DecisionTimelineProps) {
  const phases = summary.split(".").map((part) => part.trim()).filter(Boolean);

  return (
    <Card className="border-border/60 shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Calendar className="h-4 w-4 text-primary" />
          Decision Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="space-y-3">
          {phases.map((phase, index) => (
            <li key={phase} className="flex gap-3 text-sm">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                {index + 1}
              </span>
              <span className="text-muted-foreground">{phase}.</span>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}

interface ExecutiveBriefProps {
  brief: string;
}

export function ExecutiveBrief({ brief }: ExecutiveBriefProps) {
  return (
    <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-background shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-4 w-4 text-primary" />
          Executive Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm leading-relaxed text-muted-foreground">{brief}</p>
      </CardContent>
    </Card>
  );
}
