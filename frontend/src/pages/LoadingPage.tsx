import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

import { env } from "@/config/env";

export function LoadingPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col items-center gap-6"
      >
        <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
        <div className="text-center">
          <h1 className="text-xl font-semibold tracking-tight">
            Loading {env.appName}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Preparing your civic intelligence workspace...
          </p>
        </div>
      </motion.div>
    </div>
  );
}
