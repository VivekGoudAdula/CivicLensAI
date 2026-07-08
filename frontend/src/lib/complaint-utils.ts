import type { StatusVariant } from "@/design-system/tokens";
import type { ComplaintStatus } from "@/types/complaint";

export function formatComplaintStatus(status: ComplaintStatus): string {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function statusToVariant(status: ComplaintStatus): StatusVariant {
  switch (status) {
    case "resolved":
    case "closed":
      return status === "resolved" ? "success" : "neutral";
    case "rejected":
      return "error";
    case "pending":
    case "submitted":
      return "warning";
    case "under_review":
    case "clustered":
    case "in_progress":
      return "info";
    default:
      return "neutral";
  }
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function toDataUrl(base64: string, mimeType: string): string {
  if (base64.startsWith("data:")) {
    return base64;
  }
  return `data:${mimeType};base64,${base64}`;
}
