import { WifiOff } from "lucide-react";

import { EmptyState } from "@/components/empty-states/empty-state";
import { Button } from "@/components/ui/button";

interface NoInternetEmptyStateProps {
  onRetry?: () => void;
}

export function NoInternetEmptyState({ onRetry }: NoInternetEmptyStateProps) {
  return (
    <EmptyState
      icon={WifiOff}
      title="No internet connection"
      description="Please check your network connection and try again. CivicLens AI requires connectivity for live constituency data."
      action={
        onRetry ? (
          <Button variant="outline" onClick={onRetry}>
            Retry Connection
          </Button>
        ) : undefined
      }
    />
  );
}
