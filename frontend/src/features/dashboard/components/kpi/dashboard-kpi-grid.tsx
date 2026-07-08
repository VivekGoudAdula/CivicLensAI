import { motion } from "framer-motion";
import {
  AlertTriangle,
  Brain,
  Building2,
  CheckCircle2,
  Layers,
  MapPin,
  MessageSquareWarning,
  Sparkles,
  Target,
} from "lucide-react";

import { KPICard } from "@/components/charts/kpi-card";
import { DashboardGrid } from "@/components/layout/DashboardGrid";
import type { DashboardKPIs } from "@/features/dashboard/types/dashboard";

interface DashboardKPIGridProps {
  kpis: DashboardKPIs;
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.04 },
  },
};

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

export function DashboardKPIGrid({ kpis }: DashboardKPIGridProps) {
  const cards = [
    { label: "Total Complaints", value: kpis.total_complaints, icon: MessageSquareWarning },
    { label: "Open Complaints", value: kpis.open_complaints, icon: AlertTriangle },
    { label: "Resolved", value: kpis.resolved_complaints, icon: CheckCircle2 },
    { label: "Active Clusters", value: kpis.active_clusters, icon: Layers },
    { label: "Critical Issues", value: kpis.critical_issues, icon: Target },
    {
      label: "Avg AI Priority",
      value: kpis.average_ai_priority_score.toFixed(1),
      icon: Sparkles,
    },
    { label: "Departments", value: kpis.departments_involved, icon: Building2 },
    { label: "Villages Covered", value: kpis.villages_covered, icon: MapPin },
    { label: "Today's Complaints", value: kpis.todays_complaints, icon: MessageSquareWarning },
    { label: "Today's AI Analyses", value: kpis.todays_ai_analyses, icon: Brain },
  ];

  return (
    <motion.div variants={container} initial="hidden" animate="show">
      <DashboardGrid columns={5}>
        {cards.map((card) => (
          <motion.div key={card.label} variants={item}>
            <KPICard
              label={card.label}
              value={card.value}
              icon={card.icon}
              className="h-full border-border/60 shadow-sm transition-shadow hover:shadow-md"
            />
          </motion.div>
        ))}
      </DashboardGrid>
    </motion.div>
  );
}
