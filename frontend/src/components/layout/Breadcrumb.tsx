import { ChevronRight, Home } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

import { cn } from "@/lib/utils";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbProps {
  items?: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  const location = useLocation();
  const segments = location.pathname.split("/").filter(Boolean);

  const autoItems: BreadcrumbItem[] =
    items ??
    [
      { label: "Home", href: "/" },
      ...segments.map((segment, index) => ({
        label: segment.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        href:
          index < segments.length - 1
            ? `/${segments.slice(0, index + 1).join("/")}`
            : undefined,
      })),
    ];

  return (
    <nav aria-label="Breadcrumb" className={cn("flex items-center", className)}>
      <ol className="flex flex-wrap items-center gap-1.5 text-sm text-muted-foreground">
        {autoItems.map((item, index) => (
          <li key={`${item.label}-${index}`} className="flex items-center gap-1.5">
            {index > 0 ? (
              <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
            ) : null}
            {item.href ? (
              <Link
                to={item.href}
                className="inline-flex items-center gap-1 transition-colors hover:text-foreground"
              >
                {index === 0 ? <Home className="h-3.5 w-3.5" /> : null}
                <span>{item.label}</span>
              </Link>
            ) : (
              <span className="font-medium text-foreground" aria-current="page">
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
