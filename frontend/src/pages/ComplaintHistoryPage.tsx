import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Eye, Plus, Search, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";

import { CategoryBadge } from "@/components/data-display/category-badge";
import { Pagination } from "@/components/data-display/pagination";
import { StatusChip } from "@/components/data-display/status-chip";
import { ConfirmationModal } from "@/components/feedback/confirmation-modal";
import { showErrorToast, showSuccessToast } from "@/components/feedback/toast";
import { NoComplaintsEmptyState } from "@/components/empty-states/no-complaints";
import { NoSearchResultsEmptyState } from "@/components/empty-states/no-search-results";
import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonTable } from "@/components/loading/skeleton-table";
import { PrimaryButton } from "@/components/ui/buttons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCategories } from "@/hooks/use-categories";
import { useComplaints, useDeleteComplaint } from "@/hooks/use-complaints";
import { ApiError } from "@/lib/api-client";
import {
  formatComplaintStatus,
  formatDateTime,
  statusToVariant,
} from "@/lib/complaint-utils";
import type { Category, ComplaintListItem, ComplaintStatus } from "@/types/complaint";

const STATUS_OPTIONS: Array<{ value: ComplaintStatus | "all"; label: string }> = [
  { value: "all", label: "All Statuses" },
  { value: "pending", label: "Pending" },
  { value: "submitted", label: "Submitted" },
  { value: "under_review", label: "Under Review" },
  { value: "in_progress", label: "In Progress" },
  { value: "resolved", label: "Resolved" },
  { value: "rejected", label: "Rejected" },
  { value: "closed", label: "Closed" },
];

export function ComplaintHistoryPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [categoryId, setCategoryId] = useState<string>("all");
  const [status, setStatus] = useState<ComplaintStatus | "all">("all");
  const [deleteTarget, setDeleteTarget] = useState<ComplaintListItem | null>(null);

  const pageSize = 10;
  const { data: categoriesData } = useCategories();
  const deleteMutation = useDeleteComplaint();

  const queryParams = useMemo(
    () => ({
      page,
      page_size: pageSize,
      search: search || undefined,
      category_id: categoryId === "all" ? undefined : categoryId,
      status: status === "all" ? undefined : status,
    }),
    [page, search, categoryId, status],
  );

  const { data, isLoading, isError, refetch } = useComplaints(queryParams);

  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / pageSize));
  const categories = categoriesData?.items ?? [];

  const handleDelete = async () => {
    if (!deleteTarget) {
      return;
    }
    try {
      await deleteMutation.mutateAsync(deleteTarget.id);
      showSuccessToast("Complaint deleted");
      setDeleteTarget(null);
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Failed to delete complaint";
      showErrorToast("Delete failed", message);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <PageHeader
        title="Complaint History"
        description="View, search, and manage all submitted citizen complaints."
        actions={
          <PrimaryButton asChild>
            <Link to="/complaints/submit">
              <Plus className="h-4 w-4" />
              Submit Complaint
            </Link>
          </PrimaryButton>
        }
      />

      <div className="flex flex-col gap-3 rounded-xl border bg-card p-4 lg:flex-row lg:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                setSearch(searchInput.trim());
                setPage(1);
              }
            }}
            placeholder="Search complaints by title or description..."
            className="pl-9"
            aria-label="Search complaints"
          />
        </div>
        <Button
          variant="outline"
          onClick={() => {
            setSearch(searchInput.trim());
            setPage(1);
          }}
        >
          Search
        </Button>
        <Select
          value={categoryId}
          onValueChange={(value) => {
            setCategoryId(value);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-full lg:w-48" aria-label="Filter by category">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((category: Category) => (
              <SelectItem key={category.id} value={category.id}>
                {category.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={status}
          onValueChange={(value) => {
            setStatus(value as ComplaintStatus | "all");
            setPage(1);
          }}
        >
          <SelectTrigger className="w-full lg:w-44" aria-label="Filter by status">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? <SkeletonTable rows={6} columns={5} /> : null}

      {isError ? (
        <ErrorState
          title="Failed to load complaints"
          description="Could not fetch complaint history. Please check that the backend is running."
          onRetry={() => void refetch()}
        />
      ) : null}

      {!isLoading && !isError && data?.items.length === 0 ? (
        search || categoryId !== "all" || status !== "all" ? (
          <NoSearchResultsEmptyState query={search || "selected filters"} />
        ) : (
          <NoComplaintsEmptyState />
        )
      ) : null}

      {!isLoading && !isError && data && data.items.length > 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="overflow-hidden rounded-xl border"
        >
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b bg-muted/40 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">Category</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Submitted</th>
                  <th className="px-4 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((complaint) => (
                  <tr key={complaint.id} className="border-b last:border-0">
                    <td className="px-4 py-4">
                      <p className="font-medium">{complaint.title}</p>
                      <p className="mt-1 line-clamp-1 text-muted-foreground">
                        {complaint.description}
                      </p>
                    </td>
                    <td className="px-4 py-4">
                      <CategoryBadge category={complaint.category_name} />
                    </td>
                    <td className="px-4 py-4">
                      <StatusChip
                        label={formatComplaintStatus(complaint.status)}
                        variant={statusToVariant(complaint.status)}
                      />
                    </td>
                    <td className="px-4 py-4 text-muted-foreground">
                      {formatDateTime(complaint.submitted_at)}
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/complaints/${complaint.id}`}>
                            <Eye className="h-4 w-4" />
                            View
                          </Link>
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteTarget(complaint)}
                          aria-label={`Delete complaint ${complaint.title}`}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      ) : null}

      {!isLoading && data && data.total > 0 ? (
        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      ) : null}

      <ConfirmationModal
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete complaint?"
        description={`This will permanently delete "${deleteTarget?.title}". This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        loading={deleteMutation.isPending}
        onConfirm={() => void handleDelete()}
      />
    </div>
  );
}
