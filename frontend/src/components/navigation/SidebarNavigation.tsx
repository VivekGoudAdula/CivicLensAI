import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import { Landmark } from "lucide-react";

import { useSidebar } from "@/components/layout/sidebar-context";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  mainNavItems,
  type NavItem,
} from "@/config/navigation";
import { cn } from "@/lib/utils";

interface SidebarNavigationProps {
  onNavigate?: () => void;
}

function NavSection({
  label,
  items,
  collapsed,
  onNavigate,
}: {
  label: string;
  items: NavItem[];
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  return (
    <div className="space-y-1">
      {!collapsed ? (
        <p className="px-3 pb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {label}
        </p>
      ) : null}
      {items.map((item) => {
        const link = (
          <NavLink
            key={item.href}
            to={item.href}
            end={item.href === "/"}
            onClick={onNavigate}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                collapsed && "justify-center px-2",
                isActive &&
                  "bg-sidebar-accent text-sidebar-accent-foreground",
              )
            }
          >
            <item.icon className="h-4 w-4 shrink-0" aria-hidden="true" />
            {!collapsed ? <span>{item.title}</span> : null}
          </NavLink>
        );

        if (collapsed) {
          return (
            <Tooltip key={item.href} delayDuration={0}>
              <TooltipTrigger asChild>{link}</TooltipTrigger>
              <TooltipContent side="right">{item.title}</TooltipContent>
            </Tooltip>
          );
        }

        return link;
      })}
    </div>
  );
}

export function SidebarNavigation({ onNavigate }: SidebarNavigationProps) {
  const { collapsed } = useSidebar();

  return (
    <ScrollArea className="flex-1 px-3 py-4">
      <nav aria-label="Main navigation">
        <NavSection
          label="Main"
          items={mainNavItems}
          collapsed={collapsed}
          onNavigate={onNavigate}
        />
      </nav>
    </ScrollArea>
  );
}

export function SidebarBrand({ collapsed }: { collapsed: boolean }) {
  return (
    <motion.div
      layout
      className="flex h-16 items-center gap-3 border-b border-sidebar-border px-4"
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
        <Landmark className="h-5 w-5" aria-hidden="true" />
      </div>
      {!collapsed ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="min-w-0"
        >
          <p className="truncate text-sm font-semibold">CivicLens AI</p>
          <p className="truncate text-xs text-muted-foreground">Amethi Constituency</p>
        </motion.div>
      ) : null}
    </motion.div>
  );
}
