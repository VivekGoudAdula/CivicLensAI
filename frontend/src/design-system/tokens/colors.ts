export type StatusVariant = "success" | "warning" | "error" | "info" | "neutral";

export const statusColors: Record<
  StatusVariant,
  { bg: string; text: string; border: string; dot: string }
> = {
  success: {
    bg: "bg-success/10",
    text: "text-success",
    border: "border-success/20",
    dot: "bg-success",
  },
  warning: {
    bg: "bg-warning/10",
    text: "text-warning",
    border: "border-warning/20",
    dot: "bg-warning",
  },
  error: {
    bg: "bg-destructive/10",
    text: "text-destructive",
    border: "border-destructive/20",
    dot: "bg-destructive",
  },
  info: {
    bg: "bg-info/10",
    text: "text-info",
    border: "border-info/20",
    dot: "bg-info",
  },
  neutral: {
    bg: "bg-muted",
    text: "text-muted-foreground",
    border: "border-border",
    dot: "bg-muted-foreground",
  },
};

export const colors = {
  brand: {
    primary: "hsl(var(--primary))",
    secondary: "hsl(var(--secondary))",
    accent: "hsl(var(--accent))",
  },
  surface: {
    background: "hsl(var(--background))",
    card: "hsl(var(--card))",
    muted: "hsl(var(--muted))",
  },
  status: statusColors,
} as const;
