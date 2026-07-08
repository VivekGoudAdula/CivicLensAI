import { motion } from "framer-motion";
import { ArrowDown, ArrowUp, Minus, Sparkles } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PredictiveAnalyticsCard } from "@/features/analytics-intelligence/types/analytics";
import { cn } from "@/lib/utils";

interface PredictiveAnalyticsPanelProps {
  cards: PredictiveAnalyticsCard[];
}

function TrendIcon({ direction }: { direction: string }) {
  if (direction === "up") return <ArrowUp className="h-4 w-4 text-rose-500" />;
  if (direction === "down") return <ArrowDown className="h-4 w-4 text-emerald-500" />;
  return <Minus className="h-4 w-4 text-muted-foreground" />;
}

export function PredictiveAnalyticsPanel({ cards }: PredictiveAnalyticsPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-primary" />
        <h2 className="text-lg font-semibold">Predictive Analytics</h2>
        <span className="rounded-full border px-2 py-0.5 text-xs text-muted-foreground">
          AI-ready · heuristic engine
        </span>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((card, index) => (
          <motion.div
            key={card.key}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.04 }}
          >
            <Card className="h-full border-border/60 shadow-sm transition-shadow hover:shadow-md">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {card.title}
                  </CardTitle>
                  <TrendIcon direction={card.trend_direction} />
                </div>
                <p className="text-xl font-bold tracking-tight">{card.value}</p>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p className="text-muted-foreground">{card.detail}</p>
                <p className={cn("text-xs font-medium text-primary")}>
                  Confidence {Math.round(card.confidence * 100)}% · {card.model_version}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
