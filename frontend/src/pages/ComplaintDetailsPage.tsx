import { useMemo, useState } from "react";
import { ArrowLeft, MapPin, Mic, Trash2 } from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ComplaintAIInsightsPanel } from "@/components/complaints/complaint-ai-insights-panel";
import { ComplaintImageIntelligencePanel } from "@/components/complaints/complaint-image-intelligence-panel";
import { DuplicateBadge } from "@/components/clusters/duplicate-badge";
import { SimilarityScoreBadge } from "@/components/clusters/similarity-score-badge";
import { GoogleMapView } from "@/components/maps/google-map-view";

import { CategoryBadge } from "@/components/data-display/category-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { ConfirmationModal } from "@/components/feedback/confirmation-modal";
import { showErrorToast, showSuccessToast } from "@/components/feedback/toast";
import { ErrorState } from "@/components/empty-states/error-state";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonCard } from "@/components/loading/skeleton-card";
import { DangerButton, SecondaryButton } from "@/components/ui/buttons";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalyzeComplaint, useAnalyzeComplaintImage, useComplaint, useDeleteComplaint } from "@/hooks/use-complaints";
import { ApiError } from "@/lib/api-client";
import {
  formatComplaintStatus,
  formatDateTime,
  statusToVariant,
  toDataUrl,
} from "@/lib/complaint-utils";

function DetailMap({
  latitude,
  longitude,
}: {
  latitude: number;
  longitude: number;
}) {
  return <GoogleMapView latitude={latitude} longitude={longitude} height={280} zoom={15} />;
}

export function ComplaintDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showDelete, setShowDelete] = useState(false);

  const { data: complaint, isLoading, isError, refetch } = useComplaint(id);
  const deleteMutation = useDeleteComplaint();
  const analyzeMutation = useAnalyzeComplaint();
  const analyzeImageMutation = useAnalyzeComplaintImage();

  const audioSrc = useMemo(() => {
    if (!complaint?.audio_base64 || !complaint.audio_mime_type) {
      return null;
    }
    return toDataUrl(complaint.audio_base64, complaint.audio_mime_type);
  }, [complaint]);

  const handleAnalyze = async (force = false) => {
    if (!id) {
      return;
    }
    try {
      const response = await analyzeMutation.mutateAsync({ id, force });
      if (response.success) {
        showSuccessToast("AI analysis complete", response.message);
      } else {
        showErrorToast("AI analysis failed", response.message);
      }
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Failed to analyze complaint";
      showErrorToast("AI analysis failed", message);
    }
  };

  const handleAnalyzeImage = async (force = false) => {
    if (!id) {
      return;
    }
    try {
      const response = await analyzeImageMutation.mutateAsync({ id, force });
      if (response.success) {
        showSuccessToast("Image analysis complete", response.message);
      } else {
        showErrorToast("Image analysis failed", response.message);
      }
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Failed to analyze complaint image";
      showErrorToast("Image analysis failed", message);
    }
  };

  const handleDelete = async () => {
    if (!id) {
      return;
    }
    try {
      await deleteMutation.mutateAsync(id);
      showSuccessToast("Complaint deleted");
      navigate("/complaints");
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Failed to delete complaint";
      showErrorToast("Delete failed", message);
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-6">
        <PageHeader title="Complaint Details" />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (isError || !complaint) {
    return (
      <div className="mx-auto max-w-4xl">
        <ErrorState
          title="Complaint not found"
          description="The requested complaint could not be loaded."
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <PageHeader
        title={complaint.title}
        description={`Submitted on ${formatDateTime(complaint.submitted_at)}`}
        actions={
          <div className="flex gap-2">
            <SecondaryButton asChild>
              <Link to="/complaints">
                <ArrowLeft className="h-4 w-4" />
                Back
              </Link>
            </SecondaryButton>
            <DangerButton onClick={() => setShowDelete(true)}>
              <Trash2 className="h-4 w-4" />
              Delete
            </DangerButton>
          </div>
        }
      />

      <div className="flex flex-wrap gap-2">
        <CategoryBadge category={complaint.category_name} />
        <StatusChip
          label={formatComplaintStatus(complaint.status)}
          variant={statusToVariant(complaint.status)}
        />
        {complaint.is_duplicate ? <DuplicateBadge /> : null}
        {complaint.duplicate_score != null && complaint.duplicate_score > 0 ? (
          <SimilarityScoreBadge score={complaint.duplicate_score} />
        ) : null}
      </div>

      {complaint.cluster_id ? (
        <Card>
          <CardHeader>
            <CardTitle>Complaint Cluster</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              This complaint has been grouped into an AI-managed cluster for duplicate detection
              and hotspot analysis.
            </p>
            {complaint.duplicate_reason ? (
              <p className="text-sm">{complaint.duplicate_reason}</p>
            ) : null}
            <SecondaryButton asChild>
              <Link to={`/civic-insights/clusters/${complaint.cluster_id}`}>
                View Cluster
              </Link>
            </SecondaryButton>
          </CardContent>
        </Card>
      ) : null}

      <ComplaintAIInsightsPanel
        complaint={complaint}
        onRetry={() => void handleAnalyze(complaint.analysis_status === "failed")}
        isRetrying={analyzeMutation.isPending}
      />

      <ComplaintImageIntelligencePanel
        complaint={complaint}
        onRetry={() =>
          void handleAnalyzeImage(complaint.image_analysis_status === "failed")
        }
        isRetrying={analyzeImageMutation.isPending}
      />

      <Card>
        <CardHeader>
          <CardTitle>Description</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap text-muted-foreground">{complaint.description}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Location</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {complaint.location ? (
            <>
              <DetailMap
                latitude={complaint.location.latitude}
                longitude={complaint.location.longitude}
              />
              <div className="flex items-start gap-2 text-sm">
                <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                <div>
                  <p>{complaint.location.address ?? "Address not available"}</p>
                  {complaint.landmark ? (
                    <p className="mt-1 text-muted-foreground">
                      Landmark: {complaint.landmark}
                    </p>
                  ) : null}
                  <p className="mt-2 font-mono text-xs text-muted-foreground">
                    {complaint.location.latitude.toFixed(6)},{" "}
                    {complaint.location.longitude.toFixed(6)}
                  </p>
                </div>
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">No location data available.</p>
          )}
        </CardContent>
      </Card>

      {audioSrc ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mic className="h-5 w-5" />
              Voice Recording
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <audio controls src={audioSrc} className="w-full">
              Your browser does not support audio playback.
            </audio>
            {complaint.audio_duration_seconds ? (
              <p className="text-sm text-muted-foreground">
                Duration: {Math.round(complaint.audio_duration_seconds)} seconds
              </p>
            ) : null}
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Status & Contact</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Status</p>
            <p className="mt-1">{formatComplaintStatus(complaint.status)}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Constituency</p>
            <p className="mt-1">
              {complaint.village_name}, {complaint.constituency}, {complaint.district}
            </p>
          </div>
          {!complaint.is_anonymous ? (
            <>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Contact Name</p>
                <p className="mt-1">{complaint.citizen_name ?? "—"}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Mobile</p>
                <p className="mt-1">{complaint.citizen_phone ?? "—"}</p>
              </div>
            </>
          ) : (
            <div className="sm:col-span-2">
              <p className="text-sm text-muted-foreground">Submitted anonymously</p>
            </div>
          )}
          {complaint.resolved_at ? (
            <div>
              <p className="text-sm font-medium text-muted-foreground">Resolved</p>
              <p className="mt-1">{formatDateTime(complaint.resolved_at)}</p>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <ConfirmationModal
        open={showDelete}
        onOpenChange={setShowDelete}
        title="Delete complaint?"
        description="This will permanently delete this complaint. This action cannot be undone."
        confirmLabel="Delete"
        loading={deleteMutation.isPending}
        onConfirm={() => void handleDelete()}
      />
    </div>
  );
}
