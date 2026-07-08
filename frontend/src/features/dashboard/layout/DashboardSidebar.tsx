import { motion } from "framer-motion";
import { NavLink } from "react-router-dom";
import { Landmark, PanelLeftClose, PanelLeftOpen } from "lucide-react";

import { useSidebar } from "@/components/layout/sidebar-context";
import { dashboardNavItems } from "@/features/dashboard/layout/dashboard-navigation";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

interface DashboardSidebarProps {
  onNavigate?: () => void;
  className?: string;
}

export function DashboardSidebar({ onNavigate, className }: DashboardSidebarProps) {
  const { collapsed, toggle } = useSidebar();

  return (
    <motion.aside
      layout
      className={cn(
        "flex h-full flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground",
        collapsed ? "w-[68px]" : "w-64",
        className,
      )}
      aria-label="MP Dashboard sidebar"
    >
      <motion.div
        layout
        className="flex h-16 items-center gap-3 border-b border-sidebar-border px-4"
      >
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
          <Landmark className="h-5 w-5" />
        </div>
        {!collapsed ? (
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold">MP Command Center</p>
            <p className="truncate text-xs text-muted-foreground">Decision Intelligence</p>
          </div>
        ) : null}
      </motion.div>

      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-1" aria-label="Dashboard navigation">
          {!collapsed ? (
            <p className="px-3 pb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Intelligence
            </p>
          ) : null}
          {dashboardNavItems.map((item) => {
            const link = (
              <NavLink
                key={item.href}
                to={item.href}
                end={item.href === "/dashboard"}
                onClick={onNavigate}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                    collapsed && "justify-center px-2",
                    isActive &&
                      "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm",
                  )
                }
              >
                <item.icon className="h-4 w-4 shrink-0" />
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
        </nav>
      </ScrollArea>

      <div className="mt-auto border-t border-sidebar-border p-3">
        <Button
          variant="ghost"
          size={collapsed ? "icon" : "default"}
          onClick={toggle}
          className={cn("w-full", collapsed && "justify-center")}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <PanelLeftOpen className="h-4 w-4" />
          ) : (
            <>
              <PanelLeftClose className="h-4 w-4" />
              <span>Collapse</span>
            </>
          )}
        </Button>
      </div>
    </motion.aside>
  );
}
