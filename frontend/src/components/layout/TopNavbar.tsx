import { Menu, LogOut } from "lucide-react";

import { NotificationMenu } from "@/components/navigation/NotificationMenu";
import { UserMenu } from "@/components/navigation/UserMenu";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { GlobalSearchBar } from "@/features/search/components/global-search-bar";
import { Button } from "@/components/ui/button";

interface TopNavbarProps {
  onMenuClick?: () => void;
}

export function TopNavbar({ onMenuClick }: TopNavbarProps) {
  const token = localStorage.getItem("civiclens_token");

  const handleSignOut = () => {
    localStorage.removeItem("civiclens_token");
    window.location.href = "/";
  };

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60 md:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={onMenuClick}
        aria-label="Open navigation menu"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <div className="flex flex-1 items-center gap-4">
        <GlobalSearchBar className="hidden max-w-md md:block" />
      </div>

      <div className="flex items-center gap-2">
        <ThemeToggle />
        <NotificationMenu />
        <UserMenu />
        {token && (
          <Button variant="ghost" size="icon" onClick={handleSignOut} aria-label="Sign out" className="text-muted-foreground hover:text-foreground">
            <LogOut className="h-5 w-5" />
          </Button>
        )}
      </div>
    </header>
  );
}
