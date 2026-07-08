import { Sheet, SheetContent } from "@/components/ui/sheet";
import {
  SidebarBrand,
  SidebarNavigation,
} from "@/components/navigation/SidebarNavigation";

export interface MobileNavigationProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function MobileNavigation({ open, onOpenChange }: MobileNavigationProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-72 p-0">
        <aside className="flex h-full flex-col bg-sidebar text-sidebar-foreground">
          <SidebarBrand collapsed={false} />
          <SidebarNavigation onNavigate={() => onOpenChange(false)} />
        </aside>
      </SheetContent>
    </Sheet>
  );
}
