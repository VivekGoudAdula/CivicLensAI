import { motion } from "framer-motion";

import { PriorityBadge, type PriorityLevel } from "@/components/data-display/priority-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface PriorityCardProps {
  title: string;
  description: string;
  priority: PriorityLevel;
  count?: number;
}

export function PriorityCard({
  title,
  description,
  priority,
  count,
}: PriorityCardProps) {
  return (
    <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">{title}</CardTitle>
          <PriorityBadge priority={priority} />
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{description}</p>
          {count !== undefined ? (
            <p className="mt-3 text-2xl font-bold">{count}</p>
          ) : null}
        </CardContent>
      </Card>
    </motion.div>
  );
}
