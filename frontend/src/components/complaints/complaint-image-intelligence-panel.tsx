import { AIConfidenceBadge } from "@/components/data-display/ai-confidence-badge";
import { DepartmentBadge } from "@/components/data-display/department-badge";
import { SeverityBadge } from "@/components/data-display/severity-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { Spinner } from "@/components/feedback/spinner";
import { PrimaryButton } from "@/components/ui/buttons";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type {
  AnalysisStatus,
  ComplaintDetail,
  ComplaintImageAnalysis,
} from "@/types/complaint";
import { formatDateTime, toDataUrl } from "@/lib/complaint-utils";
import { cn } from "@/lib/utils";
import {
  AlertTriangle,
  Camera,
  Car,
  RefreshCw,
  ShieldAlert,
  User,
} from "lucide-react";
import type { ComponentType } from "react";

function analysisStatusVariant(
  status: AnalysisStatus,
): "success" | "warning" | "error" | "info" | "neutral" {
  switch (status) {
    case "completed":
      return "success";
    case "processing":
    case "pending":
      return "warning";
    case "failed":
      return "error";
    default:
      return "neutral";
  }
}

function normalizeSeverity(value: string): "low" | "medium" | "high" | "critical" {
  const normalized = value.toLowerCase() as "low" | "medium" | "high" | "critical";
  if (["low", "medium", "high", "critical"].includes(normalized)) {
    return normalized;
  }
  return "medium";
}

function formatAnalysisStatus(status: AnalysisStatus): string {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export interface ComplaintImageIntelligencePanelProps {
  complaint: ComplaintDetail;
  onRetry?: () => void;
  isRetrying?: boolean;
  className?: string;
}

function InsightRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="space-y-1">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <p className="text-sm leading-relaxed">{value}</p>
    </div>
  );
}

function FlagPill({
  label,
  active,
  icon: Icon,
}: {
  label: string;
  active: boolean;
  icon: ComponentType<{ className?: string }>;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium",
        active
          ? "bg-destructive/10 text-destructive"
          : "bg-muted text-muted-foreground",
      )}
    >
      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
      {label}: {active ? "Yes" : "No"}
    </span>
  );
}

function ImageAnalysisContent({
  analysis,
  imageSrc,
  processingTimeMs,
  visionModel,
  visionPromptVersion,
  visionCompletedAt,
}: {
  analysis: ComplaintImageAnalysis;
  imageSrc: string;
  processingTimeMs?: number | null;
  visionModel?: string | null;
  visionPromptVersion?: string | null;
  visionCompletedAt?: string | null;
}) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Uploaded Image</CardTitle>
        </CardHeader>
        <CardContent>
          <img
            src={imageSrc}
            alt="Complaint evidence analyzed by Gemini Vision"
            className="max-h-96 w-full rounded-lg border object-contain"
          />
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Primary Issue</p>
            <p className="mt-1 font-medium">{analysis.primary_issue}</p>
            {analysis.secondary_issue ? (
              <p className="mt-1 text-sm text-muted-foreground">
                Secondary: {analysis.secondary_issue}
              </p>
            ) : null}
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Severity</p>
            <div className="mt-2">
              <SeverityBadge severity={normalizeSeverity(analysis.severity)} />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Confidence</p>
            <div className="mt-2">
              <AIConfidenceBadge score={analysis.confidence_score} />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Suggested Department</p>
            <div className="mt-2">
              <DepartmentBadge name={analysis.suggested_department} />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Visual Assessment</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <InsightRow label="Description" value={analysis.description} />
          <InsightRow label="Visible Damage" value={analysis.visible_damage} />
          <InsightRow
            label="Estimated Area Affected"
            value={analysis.estimated_area_affected}
          />
          <InsightRow label="Safety Risk" value={analysis.safety_risk} />
          <div className="flex flex-wrap gap-2">
            <FlagPill label="Human Presence" active={analysis.human_presence} icon={User} />
            <FlagPill label="Vehicles Present" active={analysis.vehicles_present} icon={Car} />
            <FlagPill
              label="Urgent Attention"
              active={analysis.requires_urgent_attention}
              icon={ShieldAlert}
            />
          </div>
        </CardContent>
      </Card>

      {analysis.detected_objects.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Detected Objects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {analysis.detected_objects.map((object) => (
                <span
                  key={object}
                  className="rounded-md bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary"
                >
                  {object}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Immediate Action</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {analysis.suggested_immediate_action}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Long-Term Action</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {analysis.suggested_long_term_action}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Impact & Risk Analysis</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <InsightRow label="Public Impact" value={analysis.possible_public_impact} />
          <InsightRow label="Environmental Risk" value={analysis.environmental_risk} />
          <InsightRow label="Road Safety Risk" value={analysis.road_safety_risk} />
          <div className="sm:col-span-2">
            <InsightRow label="AI Reasoning" value={analysis.reasoning} />
          </div>
          {analysis.duplicate_indicators.length > 0 ? (
            <div className="sm:col-span-2">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Duplicate Indicators
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                {analysis.duplicate_indicators.map((indicator) => (
                  <span
                    key={indicator}
                    className="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground"
                  >
                    {indicator}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
          <p className="sm:col-span-2 text-xs text-muted-foreground">
            Processed {formatDateTime(analysis.processed_at)}
            {visionCompletedAt ? ` · Completed ${formatDateTime(visionCompletedAt)}` : ""}
            {visionModel ? ` · ${visionModel}` : ""}
            {visionPromptVersion ? ` · prompt v${visionPromptVersion}` : ""}
            {processingTimeMs ? ` · ${processingTimeMs}ms` : ""}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export function ComplaintImageIntelligencePanel({
  complaint,
  onRetry,
  isRetrying = false,
  className,
}: ComplaintImageIntelligencePanelProps) {
  const hasImage = Boolean(complaint.image_base64 && complaint.image_mime_type);
  const status = complaint.image_analysis_status ?? "pending";
  const analysis = complaint.image_analysis;

  const imageSrc =
    hasImage && complaint.image_base64 && complaint.image_mime_type
      ? toDataUrl(complaint.image_base64, complaint.image_mime_type)
      : null;

  if (!hasImage) {
    return null;
  }

  return (
    <section
      className={cn("space-y-4", className)}
      aria-labelledby="image-intelligence-heading"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Camera className="h-4 w-4 text-primary" aria-hidden="true" />
          </div>
          <div>
            <h2 id="image-intelligence-heading" className="text-lg font-semibold">
              Image Intelligence
            </h2>
            <p className="text-sm text-muted-foreground">
              Gemini Vision analysis of the uploaded civic issue photograph
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <StatusChip
            label={formatAnalysisStatus(status)}
            variant={analysisStatusVariant(status)}
          />
          {onRetry ? (
            <PrimaryButton
              size="sm"
              onClick={onRetry}
              loading={isRetrying}
              disabled={isRetrying || status === "processing"}
            >
              <RefreshCw className="h-4 w-4" />
              {status === "failed" ? "Retry Vision Analysis" : "Re-analyze Image"}
            </PrimaryButton>
          ) : null}
        </div>
      </div>

      {status === "processing" || status === "pending" ? (
        <Card>
          <CardContent className="flex items-center gap-3 py-10">
            <Spinner />
            <div>
              <p className="font-medium">Image analysis in progress</p>
              <p className="text-sm text-muted-foreground">
                Gemini Vision is inspecting the photograph for civic infrastructure issues.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {status === "failed" ? (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardContent className="flex items-start gap-3 py-6">
            <AlertTriangle className="mt-0.5 h-5 w-5 text-destructive" />
            <div>
              <p className="font-medium text-destructive">Image analysis failed</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {complaint.vision_error_message ??
                  "Gemini Vision could not analyze this image. The original complaint is preserved."}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {status === "completed" && analysis && imageSrc ? (
        <ImageAnalysisContent
          analysis={analysis}
          imageSrc={imageSrc}
          processingTimeMs={complaint.vision_processing_time_ms}
          visionModel={complaint.vision_model}
          visionPromptVersion={complaint.vision_prompt_version}
          visionCompletedAt={complaint.vision_completed_at}
        />
      ) : null}
    </section>
  );
}
