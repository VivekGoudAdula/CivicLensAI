export const AMETHI_CENTER: [number, number] = [26.1539, 81.8139];
export const DEFAULT_ZOOM = 11;

export const PIN_COLORS = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
  resolved: "#3b82f6",
  default: "#6b7280",
} as const;

export function getComplaintPinColor(priority: string, status: string): string {
  if (status === "resolved" || status === "closed") {
    return PIN_COLORS.resolved;
  }
  const key = priority.toLowerCase() as keyof typeof PIN_COLORS;
  return PIN_COLORS[key] ?? PIN_COLORS.default;
}

export function getClusterPinColor(score: number): string {
  if (score >= 85) return PIN_COLORS.critical;
  if (score >= 70) return PIN_COLORS.high;
  if (score >= 40) return PIN_COLORS.medium;
  return PIN_COLORS.low;
}

export const DEPARTMENT_COLORS = [
  "#3b82f6",
  "#8b5cf6",
  "#ec4899",
  "#f97316",
  "#14b8a6",
  "#eab308",
  "#6366f1",
  "#ef4444",
] as const;

export function departmentColor(department: string): string {
  let hash = 0;
  for (let i = 0; i < department.length; i += 1) {
    hash = department.charCodeAt(i) + ((hash << 5) - hash);
  }
  return DEPARTMENT_COLORS[Math.abs(hash) % DEPARTMENT_COLORS.length];
}
