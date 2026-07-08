import { SkeletonCards } from "@/components/loading/skeleton-card";
import { SkeletonTable } from "@/components/loading/skeleton-table";
import { Skeleton } from "@/components/ui/skeleton";

export function SkeletonDashboard() {
  return (
    <div className="space-y-6" role="status" aria-label="Loading dashboard">
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>
      <SkeletonCards count={4} />
      <SkeletonTable rows={6} columns={5} />
    </div>
  );
}
