import { useMemo } from "react";
import { Eye } from "lucide-react";
import { Link } from "react-router-dom";

import { CategoryBadge } from "@/components/data-display/category-badge";
import { DataTable, type ColumnDef } from "@/components/data-display/data-table";
import { StatusChip } from "@/components/data-display/status-chip";
import { Button } from "@/components/ui/button";
import { useDashboardFilters } from "@/features/dashboard/context/dashboard-filters-context";
import { formatComplaintStatus, formatDateTime, statusToVariant } from "@/lib/complaint-utils";
import type { ComplaintListItem } from "@/types/complaint";

interface DashboardComplaintsTableProps {
  complaints: ComplaintListItem[];
  onViewDetails?: (complaintId: string) => void;
  pageSize?: number;
}

type ComplaintRow = ComplaintListItem & Record<string, unknown>;

function matchesFilters(
  complaint: ComplaintListItem,
  filters: ReturnType<typeof useDashboardFilters>["filters"],
): boolean {
  if (filters.search) {
    const query = filters.search.toLowerCase();
    const haystack = [
      complaint.title,
      complaint.address,
      complaint.constituency,
      complaint.category_name,
      complaint.status,
    ]
      .join(" ")
      .toLowerCase();
    if (!haystack.includes(query)) {
      return false;
    }
  }
  if (filters.village) {
    const villageHaystack = [complaint.address, complaint.constituency, complaint.landmark]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    if (!villageHaystack.includes(filters.village.toLowerCase())) {
      return false;
    }
  }
  if (filters.category) {
    if (!complaint.category_name.toLowerCase().includes(filters.category.toLowerCase())) {
      return false;
    }
  }
  if (filters.status && complaint.status !== filters.status) {
    return false;
  }
  if (filters.priority && complaint.priority !== filters.priority) {
    return false;
  }
  if (filters.dateFrom) {
    const from = new Date(filters.dateFrom);
    if (new Date(complaint.submitted_at) < from) {
      return false;
    }
  }
  if (filters.dateTo) {
    const to = new Date(filters.dateTo);
    to.setHours(23, 59, 59, 999);
    if (new Date(complaint.submitted_at) > to) {
      return false;
    }
  }
  return true;
}

export function DashboardComplaintsTable({
  complaints,
  onViewDetails,
  pageSize = 10,
}: DashboardComplaintsTableProps) {
  const { filters } = useDashboardFilters();

  const filtered = useMemo(
    () => complaints.filter((complaint) => matchesFilters(complaint, filters)),
    [complaints, filters],
  );

  const columns: ColumnDef<ComplaintRow>[] = [
    {
      key: "title",
      header: "Complaint",
      render: (row) => (
        <div className="min-w-[200px]">
          <p className="font-medium">{row.title}</p>
          <p className="text-xs text-muted-foreground">
            {row.address ?? row.constituency}
          </p>
        </div>
      ),
    },
    {
      key: "category_name",
      header: "Category",
      render: (row) => (
        <CategoryBadge category={row.category_name} />
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (row) => (
        <StatusChip label={formatComplaintStatus(row.status)} variant={statusToVariant(row.status)} />
      ),
    },
    {
      key: "priority",
      header: "Priority",
      render: (row) => <span className="capitalize">{row.priority}</span>,
    },
    {
      key: "submitted_at",
      header: "Submitted",
      render: (row) => formatDateTime(row.submitted_at),
    },
    {
      key: "id",
      header: "Actions",
      sortable: false,
      render: (row) => (
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => onViewDetails?.(row.id)}>
            <Eye className="h-4 w-4" />
            View
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <Link to={`/dashboard/complaints/${row.id}`}>Details</Link>
          </Button>
        </div>
      ),
    },
  ];

  return (
    <DataTable
      data={filtered as ComplaintRow[]}
      columns={columns}
      pageSize={pageSize}
      searchKeys={["title", "address", "constituency", "category_name", "status"]}
    />
  );
}
