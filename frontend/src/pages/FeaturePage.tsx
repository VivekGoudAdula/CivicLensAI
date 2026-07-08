import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { Construction } from "lucide-react";

interface FeaturePageProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

export function FeaturePage({ title, description, icon: Icon }: FeaturePageProps) {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center py-12 text-center">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col items-center"
      >
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
          <Icon className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        <p className="mt-3 text-muted-foreground">{description}</p>
        <div className="mt-8 flex items-center gap-2 rounded-lg border bg-muted/50 px-4 py-3 text-sm text-muted-foreground">
          <Construction className="h-4 w-4" />
          <span>This module will be expanded in the next development phase.</span>
        </div>
      </motion.div>
    </div>
  );
}
