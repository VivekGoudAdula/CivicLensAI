import { AIConfidenceBadge } from "@/components/data-display/ai-confidence-badge";
import { AIInsightCard } from "@/components/data-display/ai-insight-card";
import { DepartmentBadge } from "@/components/data-display/department-badge";
import { PriorityBadge } from "@/components/data-display/priority-badge";
import { SeverityBadge } from "@/components/data-display/severity-badge";
import { StatusChip } from "@/components/data-display/status-chip";
import { Spinner } from "@/components/feedback/spinner";
import { PrimaryButton } from "@/components/ui/buttons";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisStatus, ComplaintAIAnalysis, ComplaintDetail, ComplaintPriority } from "@/types/complaint";
import { formatDateTime } from "@/lib/complaint-utils";
import { cn } from "@/lib/utils";
import { AlertTriangle, RefreshCw, Sparkles } from "lucide-react";

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

function normalizeLevel(value: string): "low" | "medium" | "high" | "critical" {
  const normalized = value.toLowerCase() as "low" | "medium" | "high" | "critical";
  if (["low", "medium", "high", "critical"].includes(normalized)) {
    return normalized;
  }
  return "medium";
}

function normalizePriority(value: string): ComplaintPriority {
  const normalized = value.toLowerCase() as ComplaintPriority;
  if (["low", "medium", "high", "critical"].includes(normalized)) {
    return normalized;
  }
  return "medium";
}

function formatAnalysisStatus(status: AnalysisStatus): string {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export interface ComplaintAIInsightsPanelProps {
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

function AnalysisContent({
  analysis,
  processingTimeMs,
}: {
  analysis: ComplaintAIAnalysis;
  processingTimeMs?: number | null;
}) {
  return (
    <div className="space-y-6">
      <AIInsightCard
        title="AI Civic Intelligence Summary"
        summary={analysis.summary}
        confidence={analysis.confidence_score}
        themes={analysis.keywords}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">AI Category</p>
            <p className="mt-1 font-medium">{analysis.category}</p>
            <p className="text-sm text-muted-foreground">{analysis.sub_category}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Department</p>
            <div className="mt-2">
              <DepartmentBadge name={analysis.responsible_department} />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Urgency / Severity</p>
            <div className="mt-2 flex flex-wrap gap-2">
              <SeverityBadge severity={normalizeLevel(analysis.urgency)} />
              <SeverityBadge severity={normalizeLevel(analysis.severity)} />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Priority</p>
            <div className="mt-2">
              <PriorityBadge priority={normalizePriority(analysis.priority_level)} />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Detailed Explanation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm leading-relaxed text-muted-foreground">
            {analysis.detailed_explanation}
          </p>
          <InsightRow label="Reasoning" value={analysis.reasoning} />
          <InsightRow
            label="Affected Infrastructure"
            value={analysis.affected_infrastructure}
          />
          {analysis.affected_citizens_estimate ? (
            <InsightRow
              label="Affected Citizens (Estimate)"
              value={analysis.affected_citizens_estimate}
            />
          ) : null}
          {analysis.government_scheme ? (
            <InsightRow label="Government Scheme" value={analysis.government_scheme} />
          ) : null}
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Suggested Immediate Action</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {analysis.suggested_immediate_action}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Suggested Long-term Action</CardTitle>
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
          <CardTitle className="text-base">Routing & Metadata</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <InsightRow label="Required Department" value={analysis.required_department} />
          <InsightRow label="Required Team" value={analysis.required_team} />
          <InsightRow label="Language Detected" value={analysis.language_detected} />
          <div className="space-y-1">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Duplicate Possibility
            </p>
            <AIConfidenceBadge score={analysis.duplicate_possibility} />
          </div>
          {analysis.translated_english ? (
            <div className="sm:col-span-2">
              <InsightRow label="English Translation" value={analysis.translated_english} />
            </div>
          ) : null}
          {analysis.voice_transcript ? (
            <div className="sm:col-span-2">
              <InsightRow label="Voice Transcript" value={analysis.voice_transcript} />
            </div>
          ) : null}
          {analysis.tags.length > 0 ? (
            <div className="sm:col-span-2 flex flex-wrap gap-2">
              {analysis.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground"
                >
                  #{tag}
                </span>
              ))}
            </div>
          ) : null}
          <p className="sm:col-span-2 text-xs text-muted-foreground">
            Processed {formatDateTime(analysis.processed_at)} · {analysis.model_version} ·
            prompt v{analysis.prompt_version}
            {processingTimeMs ? ` · ${processingTimeMs}ms` : ""}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export function ComplaintAIInsightsPanel({
  complaint,
  onRetry,
  isRetrying = false,
  className,
}: ComplaintAIInsightsPanelProps) {
  const { ai_analysis: analysis, analysis_status: status } = complaint;

  return (
    <section className={cn("space-y-4", className)} aria-labelledby="ai-insights-heading">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Sparkles className="h-4 w-4 text-primary" aria-hidden="true" />
          </div>
          <div>
            <h2 id="ai-insights-heading" className="text-lg font-semibold">
              AI Insights
            </h2>
            <p className="text-sm text-muted-foreground">
              Gemini-powered civic intelligence for this complaint
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
              {status === "failed" ? "Retry Analysis" : "Re-analyze"}
            </PrimaryButton>
          ) : null}
        </div>
      </div>

      {status === "processing" || status === "pending" ? (
        <Card>
          <CardContent className="flex items-center gap-3 py-10">
            <Spinner />
            <div>
              <p className="font-medium">AI analysis in progress</p>
              <p className="text-sm text-muted-foreground">
                Gemini is analyzing the complaint details and attachments.
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
              <p className="font-medium text-destructive">AI analysis failed</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {complaint.analysis_error_message ??
                  "Gemini could not complete analysis. The original complaint is preserved."}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {status === "completed" && analysis ? (
        <AnalysisContent
          analysis={analysis}
          processingTimeMs={complaint.analysis_processing_time_ms}
        />
      ) : null}
    </section>
  );
}
