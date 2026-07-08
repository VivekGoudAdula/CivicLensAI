import type { StatusVariant } from "@/design-system/tokens";
import { statusColors } from "@/design-system/tokens";
import { cn } from "@/lib/utils";

export interface StatusChipProps {
  label: string;
  variant?: StatusVariant;
  dot?: boolean;
  className?: string;
}

export function StatusChip({
  label,
  variant = "neutral",
  dot = true,
  className,
}: StatusChipProps) {
  const colors = statusColors[variant];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        colors.bg,
        colors.text,
        colors.border,
        className,
      )}
    >
      {dot ? (
        <span className={cn("h-1.5 w-1.5 rounded-full", colors.dot)} aria-hidden="true" />
      ) : null}
      {label}
    </span>
  );
}
