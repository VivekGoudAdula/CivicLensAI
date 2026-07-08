import { motion } from "framer-motion";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  Clock,
  Layers,
  MapPin,
  MessageSquareWarning,
  Sparkles,
  Target,
} from "lucide-react";

import { KPICard } from "@/components/charts/kpi-card";
import { DashboardGrid } from "@/components/layout/DashboardGrid";
import type { IntelligenceKPIs } from "@/features/analytics-intelligence/types/analytics";

interface AnalyticsKPIGridProps {
  kpis: IntelligenceKPIs;
}

export function AnalyticsKPIGrid({ kpis }: AnalyticsKPIGridProps) {
  const cards = [
    { label: "Total Complaints", value: kpis.total_complaints, icon: MessageSquareWarning },
    { label: "Resolved", value: kpis.resolved_complaints, icon: CheckCircle2 },
    { label: "Pending", value: kpis.pending_complaints, icon: Clock },
    { label: "Critical Issues", value: kpis.critical_issues, icon: AlertTriangle },
    { label: "Active Clusters", value: kpis.active_clusters, icon: Layers },
    { label: "Avg AI Priority", value: kpis.average_ai_priority.toFixed(1), icon: Target },
    { label: "Avg Severity", value: kpis.average_severity_score.toFixed(1), icon: Sparkles },
    {
      label: "Avg Resolution (days)",
      value: kpis.average_resolution_days.toFixed(1),
      icon: Clock,
    },
    { label: "Departments", value: kpis.departments_count, icon: Building2 },
    { label: "Villages", value: kpis.villages_count, icon: MapPin },
  ];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <DashboardGrid columns={5}>
        {cards.map((card) => (
          <KPICard
            key={card.label}
            label={card.label}
            value={card.value}
            icon={card.icon}
            className="shadow-sm transition-shadow hover:shadow-md"
          />
        ))}
      </DashboardGrid>
    </motion.div>
  );
}
