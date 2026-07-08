"""Priority dashboard business logic."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.models.domain.cluster import ClusterResponse
from app.models.schemas.priority_portal import (
    PriorityAnalyzeResponse,
    PriorityBreakdownItem,
    PriorityClusterCard,
    PriorityDashboardResponse,
    PriorityRecommendationPanel,
    PriorityRerankResponse,
)
from app.services.priority.priority_engine_service import PriorityEngineService
from app.services.priority.priority_repository import PriorityRepository
from app.services.priority.priority_scheduler import PriorityScheduler

logger = logging.getLogger(__name__)


def _to_priority_card(cluster: ClusterResponse) -> PriorityClusterCard:
    analysis = cluster.priority_analysis
    return PriorityClusterCard(
        id=cluster.id,
        title=cluster.title,
        category=cluster.category,
        status=cluster.status,
        village_name=cluster.village_name,
        department=cluster.department or cluster.recommended_department,
        complaint_count=cluster.complaint_count,
        priority_score=analysis.priority_score if analysis else int((cluster.priority_score or 0) * 100),
        impact_score=cluster.impact_score or (analysis.impact_score if analysis else 0),
        urgency_level=cluster.urgency_level or (analysis.urgency_level if analysis else None),
        risk_level=analysis.risk_level if analysis else None,
        priority_rank=cluster.priority_rank or (analysis.priority_rank if analysis else None),
        recommended_department=cluster.recommended_department,
        recommended_action=cluster.recommended_action,
        affected_population=cluster.affected_population,
        priority_confidence=cluster.priority_confidence,
        latest_complaint_date=cluster.latest_complaint_date,
        priority_updated_at=cluster.priority_updated_at,
    )


def _to_recommendation(cluster: ClusterResponse) -> PriorityRecommendationPanel | None:
    analysis = cluster.priority_analysis
    if analysis is None:
        return None
    return PriorityRecommendationPanel(
        cluster_id=cluster.id,
        cluster_title=cluster.title,
        priority_rank=cluster.priority_rank or analysis.priority_rank or 0,
        priority_score=analysis.priority_score,
        impact_score=analysis.impact_score,
        why_priority_ranked_high=analysis.why_priority_ranked_high,
        contributing_factors=analysis.contributing_factors,
        expected_impact=analysis.expected_impact,
        estimated_beneficiaries=analysis.estimated_beneficiaries,
        recommended_action=analysis.recommended_action,
        estimated_resolution_time=cluster.estimated_resolution_time,
        estimated_budget=cluster.estimated_budget,
        confidence_score=analysis.confidence_score,
        reasoning=analysis.reasoning,
    )


class PriorityPortalService:
    """Read and orchestration APIs for the priority intelligence dashboard."""

    def __init__(
        self,
        priority_repo: PriorityRepository,
        priority_engine: PriorityEngineService,
        priority_scheduler: PriorityScheduler,
        settings: Settings,
    ):
        self.priority_repo = priority_repo
        self.priority_engine = priority_engine
        self.priority_scheduler = priority_scheduler
        self.settings = settings

    def get_dashboard(self) -> PriorityDashboardResponse:
        ranked = self.priority_repo.list_ranked_clusters(limit=self.settings.priority_ranking_limit)
        analyzed = [cluster for cluster in ranked if cluster.priority_analysis is not None]

        if not analyzed:
            return PriorityDashboardResponse(
                total_analyzed_clusters=0,
                critical_clusters=0,
                high_urgency_clusters=0,
                average_priority_score=0.0,
                average_impact_score=0.0,
            )

        priority_scores = [c.priority_analysis.priority_score for c in analyzed if c.priority_analysis]
        impact_scores = [c.priority_analysis.impact_score for c in analyzed if c.priority_analysis]
        critical = sum(
            1
            for c in analyzed
            if c.priority_analysis
            and c.priority_analysis.risk_level.lower() in {"high", "critical"}
        )
        high_urgency = sum(
            1
            for c in analyzed
            if c.priority_analysis
            and c.priority_analysis.urgency_level.lower() in {"high", "critical"}
        )

        top10 = analyzed[:10]
        critical_issues = [
            c
            for c in analyzed
            if c.priority_analysis
            and (
                c.priority_analysis.risk_level.lower() == "critical"
                or c.priority_analysis.urgency_level.lower() == "critical"
            )
        ][:10]

        highest_impact = sorted(
            analyzed,
            key=lambda c: c.priority_analysis.impact_score if c.priority_analysis else 0,
            reverse=True,
        )[:10]

        dept_groups: dict[str, list[ClusterResponse]] = defaultdict(list)
        village_groups: dict[str, list[ClusterResponse]] = defaultdict(list)
        for cluster in analyzed:
            dept = cluster.recommended_department or cluster.department or "Unassigned"
            village = cluster.village_name or "Unknown"
            dept_groups[dept].append(cluster)
            village_groups[village].append(cluster)

        def _breakdown(groups: dict[str, list[ClusterResponse]]) -> list[PriorityBreakdownItem]:
            items: list[PriorityBreakdownItem] = []
            for label, clusters in groups.items():
                scores = [c.priority_analysis.priority_score for c in clusters if c.priority_analysis]
                impacts = [c.priority_analysis.impact_score for c in clusters if c.priority_analysis]
                items.append(
                    PriorityBreakdownItem(
                        label=label,
                        count=len(clusters),
                        average_priority_score=round(sum(scores) / len(scores), 1) if scores else 0.0,
                        average_impact_score=round(sum(impacts) / len(impacts), 1) if impacts else 0.0,
                    )
                )
            items.sort(key=lambda item: item.average_priority_score, reverse=True)
            return items[:10]

        recommendations = [
            rec
            for cluster in top10
            if (rec := _to_recommendation(cluster)) is not None
        ]

        last_updated = max(
            (c.priority_updated_at for c in analyzed if c.priority_updated_at),
            default=None,
        )

        return PriorityDashboardResponse(
            total_analyzed_clusters=len(analyzed),
            critical_clusters=critical,
            high_urgency_clusters=high_urgency,
            average_priority_score=round(sum(priority_scores) / len(priority_scores), 1),
            average_impact_score=round(sum(impact_scores) / len(impact_scores), 1),
            top_priorities=[_to_priority_card(c) for c in top10],
            leaderboard=[_to_priority_card(c) for c in analyzed[:20]],
            critical_issues=[_to_priority_card(c) for c in critical_issues],
            highest_impact_areas=[_to_priority_card(c) for c in highest_impact],
            department_breakdown=_breakdown(dept_groups),
            village_breakdown=_breakdown(village_groups),
            recommendations=recommendations,
            last_updated_at=last_updated,
        )

    def analyze_cluster(self, cluster_id: str, *, force: bool = False) -> PriorityAnalyzeResponse:
        if not self.settings.priority_engine_enabled:
            raise BadRequestError("Priority engine is disabled")
        cluster = self.priority_repo.get_cluster(cluster_id)
        updated = self.priority_engine.analyze_cluster(cluster_id, force=force)
        return PriorityAnalyzeResponse(
            success=updated.priority_analysis is not None,
            message="Priority analysis completed" if updated.priority_analysis else "Analysis failed",
            cluster_id=cluster_id,
            priority_analysis=updated.priority_analysis,
        )

    def rerun_all(self, *, force: bool = False) -> PriorityRerankResponse:
        if not self.settings.priority_engine_enabled:
            raise BadRequestError("Priority engine is disabled")
        result = self.priority_scheduler.run_full_recalculation(force=force)
        return PriorityRerankResponse(
            success=len(result.errors) == 0,
            message="Priority recalculation completed",
            clusters_analyzed=result.clusters_analyzed,
            clusters_skipped=result.clusters_skipped,
            ranks_updated=result.ranks_updated,
            errors=result.errors,
        )
