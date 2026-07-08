import { ArrowLeft, MapPin, Users } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { ClusterComplaintsList } from "@/components/clusters/cluster-complaints-list";
import { PriorityRecommendationCard } from "@/components/priority/priority-recommendation-panel";
import { ImpactScoreBadge, PriorityBadge, RiskBadge } from "@/components/priority/priority-badges";
import { CategoryBadge } from "@/components/data-display/category-badge";
import { DepartmentBadge } from "@/components/data-display/department-badge";
import { SeverityBadge } from "@/components/data-display/severity-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { SecondaryButton } from "@/components/ui/buttons";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GoogleMapView } from "@/components/maps/google-map-view";
import { useCluster } from "@/hooks/use-clusters";
import { formatDateTime } from "@/lib/complaint-utils";

function normalizeSeverity(value?: string | null): "low" | "medium" | "high" | "critical" {
  const normalized = (value ?? "medium").toLowerCase() as "low" | "medium" | "high" | "critical";
  if (["low", "medium", "high", "critical"].includes(normalized)) {
    return normalized;
  }
  return "medium";
}

export function ClusterDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const { data: cluster, isLoading, isError, refetch } = useCluster(id);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <PageHeader title="Cluster Details" />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (isError || !cluster) {
    return (
      <div className="mx-auto max-w-5xl">
        <ErrorState
          title="Cluster not found"
          description="The requested cluster could not be loaded."
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <PageHeader
        title={cluster.title}
        description={cluster.description}
        actions={
          <SecondaryButton asChild>
            <Link to="/civic-insights">
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
          </SecondaryButton>
        }
      />

      <div className="flex flex-wrap gap-2">
        <CategoryBadge category={cluster.category.replace(/_/g, " ")} />
        <StatusChip label={cluster.status.replace(/_/g, " ")} variant="info" />
        {cluster.average_severity ? (
          <SeverityBadge severity={normalizeSeverity(cluster.average_severity)} />
        ) : null}
        {cluster.department ? <DepartmentBadge name={cluster.department} /> : null}
        {cluster.priority_rank ? (
          <PriorityBadge
            score={cluster.priority_analysis?.priority_score ?? Math.round(cluster.priority_score * 100)}
            rank={cluster.priority_rank}
          />
        ) : null}
        {cluster.impact_score ? <ImpactScoreBadge score={cluster.impact_score} /> : null}
        {cluster.priority_analysis?.risk_level ? (
          <RiskBadge level={cluster.priority_analysis.risk_level} />
        ) : null}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <Users className="h-5 w-5 text-primary" />
            <div>
              <p className="text-xs text-muted-foreground">Complaints</p>
              <p className="text-xl font-semibold">{cluster.complaint_count}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Hotspot Score</p>
            <p className="text-xl font-semibold">{(cluster.hotspot_score * 100).toFixed(0)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Priority Score</p>
            <p className="text-xl font-semibold">{(cluster.priority_score * 100).toFixed(0)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Avg Confidence</p>
            <p className="text-xl font-semibold">
              {cluster.average_confidence != null
                ? `${(cluster.average_confidence * 100).toFixed(0)}%`
                : "—"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Cluster Overview</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div>
            <p className="text-xs text-muted-foreground">Theme</p>
            <p className="mt-1">{cluster.theme}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Affected Area</p>
            <p className="mt-1">{cluster.affected_area ?? "—"}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Village</p>
            <p className="mt-1 flex items-center gap-1">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              {cluster.village_name ?? (cluster.village_names.join(", ") || "—")}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Latest Complaint</p>
            <p className="mt-1">
              {cluster.latest_complaint_date
                ? formatDateTime(cluster.latest_complaint_date)
                : "—"}
            </p>
          </div>
          <div className="sm:col-span-2">
            <p className="text-xs text-muted-foreground">Location</p>
            <p className="mt-1">
              {cluster.constituency}, {cluster.district}, {cluster.state}
            </p>
          </div>
        </CardContent>
      </Card>

      {cluster.coordinates ? (
        <Card>
          <CardHeader>
            <CardTitle>Cluster Map</CardTitle>
          </CardHeader>
          <CardContent>
            <GoogleMapView
              latitude={cluster.coordinates.latitude}
              longitude={cluster.coordinates.longitude}
              height={280}
              zoom={13}
            />
          </CardContent>
        </Card>
      ) : null}

      {cluster.priority_analysis ? (
        <PriorityRecommendationCard
          recommendation={{
            cluster_id: cluster.id,
            cluster_title: cluster.title,
            priority_rank: cluster.priority_rank ?? cluster.priority_analysis.priority_rank ?? 0,
            priority_score: cluster.priority_analysis.priority_score,
            impact_score: cluster.priority_analysis.impact_score,
            why_priority_ranked_high: cluster.priority_analysis.why_priority_ranked_high,
            contributing_factors: cluster.priority_analysis.contributing_factors,
            expected_impact: cluster.priority_analysis.expected_impact,
            estimated_beneficiaries: cluster.priority_analysis.estimated_beneficiaries,
            recommended_action: cluster.priority_analysis.recommended_action,
            estimated_resolution_time: cluster.estimated_resolution_time,
            estimated_budget: cluster.estimated_budget,
            confidence_score: cluster.priority_analysis.confidence_score,
            reasoning: cluster.priority_analysis.reasoning,
          }}
        />
      ) : null}

      <ClusterComplaintsList
        complaints={cluster.related_complaints}
        representativeComplaintId={cluster.representative_complaint_id}
      />
    </div>
  );
}
