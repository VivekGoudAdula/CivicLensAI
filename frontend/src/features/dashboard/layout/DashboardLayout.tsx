import { useState } from "react";
import { Link, Outlet } from "react-router-dom";
import { ArrowLeft, Menu, Radio, LogOut } from "lucide-react";
import { motion } from "framer-motion";

import { ContentWrapper } from "@/components/layout/ContentWrapper";
import { SidebarProvider } from "@/components/layout/sidebar-context";
import { PageTransition } from "@/components/motion/page-transition";
import { DashboardFiltersProvider } from "@/features/dashboard/context/dashboard-filters-context";
import { useFirestoreRealtime } from "@/features/dashboard/hooks/use-firestore-realtime";
import { DashboardSidebar } from "@/features/dashboard/layout/DashboardSidebar";
import { DashboardFiltersBar } from "@/features/dashboard/components/filters/dashboard-filters-bar";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { isFirebaseConfigured } from "@/lib/firebase";
import { cn } from "@/lib/utils";

function DashboardRealtimeIndicator() {
  useFirestoreRealtime();

  if (!isFirebaseConfigured()) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex items-center gap-2 rounded-full border bg-card px-3 py-1.5 text-xs font-medium text-muted-foreground shadow-sm"
    >
      <span className="relative flex h-2 w-2">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
      </span>
      <Radio className="h-3.5 w-3.5" />
      Live
    </motion.div>
  );
}

export function DashboardLayout() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const handleSignOut = () => {
    localStorage.removeItem("civiclens_token");
    window.location.href = "/";
  };

  return (
    <SidebarProvider>
      <DashboardFiltersProvider>
        <div className="flex min-h-screen w-full bg-gradient-to-br from-background via-background to-muted/30">
          <div className="hidden lg:flex">
            <DashboardSidebar />
          </div>

          <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
            <SheetContent side="left" className="w-72 p-0">
              <DashboardSidebar onNavigate={() => setMobileNavOpen(false)} />
            </SheetContent>
          </Sheet>

          <div className="flex min-h-screen flex-1 flex-col">
            <header className="sticky top-0 z-30 border-b bg-background/80 backdrop-blur-md">
              <div className="flex h-16 items-center justify-between gap-4 px-4 lg:px-6">
                <div className="flex items-center gap-3">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="lg:hidden"
                    onClick={() => setMobileNavOpen(true)}
                    aria-label="Open dashboard navigation"
                  >
                    <Menu className="h-5 w-5" />
                  </Button>
                </div>
                <div className="flex items-center gap-4">
                  <DashboardRealtimeIndicator />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleSignOut}
                    className="gap-2 text-muted-foreground hover:text-foreground"
                  >
                    <LogOut className="h-4 w-4" />
                    Logout
                  </Button>
                </div>
              </div>
              <div className={cn("border-t px-4 py-3 lg:px-6")}>
                <DashboardFiltersBar />
              </div>
            </header>

            <main className="flex-1 overflow-auto p-4 lg:p-6">
              <ContentWrapper maxWidth="full">
                <PageTransition>
                  <Outlet />
                </PageTransition>
              </ContentWrapper>
            </main>
          </div>
        </div>
      </DashboardFiltersProvider>
    </SidebarProvider>
  );
}
