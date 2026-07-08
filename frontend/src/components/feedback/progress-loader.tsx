import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

export interface ProgressLoaderProps {
  value: number;
  label?: string;
  className?: string;
}

export function ProgressLoader({ value, label, className }: ProgressLoaderProps) {
  return (
    <div className={cn("space-y-2", className)} role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
      {label ? (
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">{label}</span>
          <span className="font-medium">{value}%</span>
        </div>
      ) : null}
      <Progress value={value} />
    </div>
  );
}
