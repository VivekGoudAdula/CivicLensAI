import type { LucideIcon } from "lucide-react";
import {
  BarChart3,
  ClipboardList,
  FileSearch,
  Home,
  Landmark,
  LayoutDashboard,
  Map,
  MessageSquare,
  Palette,
  PlusCircle,
  Search,
  Settings,
  Shield,
  Sparkles,
} from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  badge?: string;
}

export const mainNavItems: NavItem[] = [
  { title: "Home", href: "/submit", icon: Home },
  { title: "Submit Complaint", href: "/complaints/submit", icon: PlusCircle },
  { title: "Complaint History", href: "/complaints", icon: ClipboardList },
  { title: "Public Forum", href: "/public-forum", icon: MessageSquare },
];

export const adminNavItems: NavItem[] = [
  { title: "MP Command Center", href: "/dashboard", icon: LayoutDashboard, badge: "Live" },
  { title: "Governance", href: "/governance", icon: Landmark },
  { title: "Compliance", href: "/compliance", icon: Shield },
  { title: "Settings", href: "/settings", icon: Settings },
];

export const systemNavItems: NavItem[] = [
  { title: "Design System", href: "/design-system", icon: Palette },
];
