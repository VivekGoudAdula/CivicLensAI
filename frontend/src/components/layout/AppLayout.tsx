import { useState } from "react";
import { Outlet } from "react-router-dom";

import { ContentWrapper } from "@/components/layout/ContentWrapper";
import { Sidebar } from "@/components/layout/Sidebar";
import { SidebarProvider } from "@/components/layout/sidebar-context";
import { TopNavbar } from "@/components/layout/TopNavbar";
import { PageTransition } from "@/components/motion/page-transition";
import { MobileNavigation } from "@/components/navigation/MobileNavigation";

export function AppLayout() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background">
        <div className="hidden md:flex">
          <Sidebar />
        </div>

        <MobileNavigation
          open={mobileNavOpen}
          onOpenChange={setMobileNavOpen}
        />

        <div className="flex min-h-screen flex-1 flex-col">
          <TopNavbar onMenuClick={() => setMobileNavOpen(true)} />
          <main className="flex-1 overflow-auto p-4 md:p-6">
            <ContentWrapper>
              <PageTransition>
                <Outlet />
              </PageTransition>
            </ContentWrapper>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
