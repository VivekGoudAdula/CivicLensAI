import { motion } from "framer-motion";

import { Spinner } from "@/components/feedback/spinner";
import { cn } from "@/lib/utils";

export interface FullPageLoaderProps {
  message?: string;
  className?: string;
}

export function FullPageLoader({
  message = "Loading CivicLens AI...",
  className,
}: FullPageLoaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={cn(
        "fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm",
        className,
      )}
      role="alert"
      aria-busy="true"
      aria-live="polite"
    >
      <Spinner size="lg" />
      <p className="mt-4 text-sm font-medium text-muted-foreground">{message}</p>
    </motion.div>
  );
}
