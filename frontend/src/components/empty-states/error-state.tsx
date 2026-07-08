import { AlertTriangle } from "lucide-react";

import { PrimaryButton } from "@/components/ui/buttons";
import { EmptyState } from "@/components/empty-states/empty-state";

export function ErrorState({
  title = "Something went wrong",
  description = "An unexpected error occurred. Please try again or contact support if the problem persists.",
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <EmptyState
      icon={AlertTriangle}
      title={title}
      description={description}
      action={
        onRetry ? (
          <PrimaryButton onClick={onRetry}>Try Again</PrimaryButton>
        ) : undefined
      }
    />
  );
}
