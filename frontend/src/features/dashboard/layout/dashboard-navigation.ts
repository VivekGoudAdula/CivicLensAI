import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BarChart3,
  ClipboardList,
  FileSearch,
  LayoutDashboard,
  Layers,
  Map,
  Search,
  Sparkles,
  Target,
  Landmark,
  Shield,
  Settings,
} from "lucide-react";

export interface DashboardNavItem {
  title: string;
  href: string;
  icon: LucideIcon;
  description?: string;
}

export const dashboardNavItems: DashboardNavItem[] = [
  {
    title: "Command Center",
    href: "/dashboard",
    icon: LayoutDashboard,
    description: "Executive overview and live KPIs",
  },
  {
    title: "Complaints",
    href: "/dashboard/complaints",
    icon: ClipboardList,
    description: "Searchable complaint registry",
  },
  {
    title: "Priority Center",
    href: "/dashboard/priority",
    icon: Target,
    description: "AI-ranked constituency priorities",
  },
  {
    title: "GIS Map",
    href: "/dashboard/map",
    icon: Map,
    description: "Interactive geospatial analysis",
  },
  {
    title: "Analytics Overview",
    href: "/dashboard/analytics",
    icon: BarChart3,
    description: "Charts and trend intelligence",
  },
  {
    title: "Analytics Intelligence",
    href: "/dashboard/analytics-intelligence",
    icon: BarChart3,
    description: "Constituency analytics and predictive insights",
  },
  {
    title: "AI Recommendations",
    href: "/dashboard/recommendations",
    icon: Sparkles,
    description: "Gemini development work recommendations",
  },
  {
    title: "Global Search",
    href: "/dashboard/search",
    icon: Search,
    description: "Enterprise search across all data",
  },
  {
    title: "Policy Analysis",
    href: "/dashboard/policy-analysis",
    icon: FileSearch,
    description: "Analyze civic policies and legislation",
  },
  {
    title: "Civic Insights",
    href: "/dashboard/civic-insights",
    icon: BarChart3,
    description: "Constituency insights and clusters",
  },
  {
    title: "Clusters",
    href: "/dashboard/clusters",
    icon: Layers,
    description: "Duplicate clusters and hotspots",
  },
  {
    title: "Activities",
    href: "/dashboard/activities",
    icon: Activity,
    description: "Real-time constituency timeline",
  },
  {
    title: "Governance",
    href: "/dashboard/governance",
    icon: Landmark,
    description: "Local government rules and settings",
  },
  {
    title: "Compliance",
    href: "/dashboard/compliance",
    icon: Shield,
    description: "Regulatory compliance and accountability",
  },
  {
    title: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
    description: "Dashboard preferences and profile",
  },
];
