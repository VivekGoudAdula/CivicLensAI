"""Architecture-ready scheduler for batch priority recalculation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.config import Settings
from app.services.priority.priority_engine_service import PriorityEngineService
from app.services.priority.priority_repository import PriorityRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PrioritySchedulerResult:
    """Result of a scheduled priority recalculation run."""

    started_at: datetime
    completed_at: datetime
    clusters_analyzed: int
    clusters_skipped: int
    ranks_updated: int
    errors: list[str]


class PriorityScheduler:
    """
    Batch priority recalculation orchestrator.

    Designed for future cron/worker integration. Currently supports manual
    invocation via API for full constituency re-prioritization.
    """

    def __init__(
        self,
        priority_engine: PriorityEngineService,
        priority_repo: PriorityRepository,
        settings: Settings,
    ):
        self.priority_engine = priority_engine
        self.priority_repo = priority_repo
        self.settings = settings

    def run_full_recalculation(self, *, force: bool = False) -> PrioritySchedulerResult:
        """Re-analyze all clusters and refresh global ranks."""
        started_at = datetime.now(UTC)
        analyzed = 0
        skipped = 0
        errors: list[str] = []

        clusters = self.priority_repo.list_all_clusters(limit=self.settings.priority_ranking_limit)
        for cluster in clusters:
            try:
                complaints = self.priority_repo.get_cluster_complaints(cluster)
                if not complaints:
                    skipped += 1
                    continue
                if not force:
                    context = self.priority_engine.calculator.build_context(cluster, complaints)
                    if (
                        cluster.priority_analysis_hash == context.analysis_hash
                        and cluster.priority_analysis
                    ):
                        skipped += 1
                        continue
                self.priority_engine.analyze_cluster(
                    cluster.id,
                    force=force,
                    recalculate_ranks=False,
                )
                analyzed += 1
            except Exception as exc:
                logger.exception("Scheduled priority analysis failed for %s", cluster.id)
                errors.append(f"{cluster.id}: {exc}")

        ranks_updated = self.priority_engine.recalculate_global_ranks()
        completed_at = datetime.now(UTC)
        logger.info(
            "Priority scheduler completed: analyzed=%s skipped=%s ranks=%s errors=%s",
            analyzed,
            skipped,
            ranks_updated,
            len(errors),
        )
        return PrioritySchedulerResult(
            started_at=started_at,
            completed_at=completed_at,
            clusters_analyzed=analyzed,
            clusters_skipped=skipped,
            ranks_updated=ranks_updated,
            errors=errors,
        )
