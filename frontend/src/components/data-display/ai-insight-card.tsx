import { Sparkles } from "lucide-react";
import { motion } from "framer-motion";

import { AIConfidenceBadge } from "@/components/data-display/ai-confidence-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface AIInsightCardProps {
  title: string;
  summary: string;
  confidence: number;
  themes?: string[];
}

export function AIInsightCard({
  title,
  summary,
  confidence,
  themes = [],
}: AIInsightCardProps) {
  return (
    <motion.div whileHover={{ scale: 1.01 }} transition={{ duration: 0.2 }}>
      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
        <CardHeader className="flex flex-row items-start justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <Sparkles className="h-4 w-4 text-primary" aria-hidden="true" />
            </div>
            <CardTitle className="text-base">{title}</CardTitle>
          </div>
          <AIConfidenceBadge score={confidence} />
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm leading-relaxed text-muted-foreground">{summary}</p>
          {themes.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {themes.map((theme) => (
                <span
                  key={theme}
                  className="rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                >
                  {theme}
                </span>
              ))}
            </div>
          ) : null}
        </CardContent>
      </Card>
    </motion.div>
  );
}
