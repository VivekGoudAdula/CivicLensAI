"""Persistence layer for MP recommendation engine runs."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from app.models.domain.recommendation import RecommendationAIContent, RecommendationCreate
from app.models.enums.common import RecommendationPriority, RecommendationStatus
from app.models.schemas.ai_mp_recommendation import GeminiMpRecommendationOutput, MpDevelopmentWorkItem
from app.models.schemas.common import DocumentMetadataCreate
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.gemini import get_configured_model_name

logger = logging.getLogger(__name__)

RECOMMENDATION_ENGINE_ACTOR = "civiclens-recommendation-engine"

_URGENCY_TO_PRIORITY = {
    "critical": RecommendationPriority.URGENT,
    "urgent": RecommendationPriority.URGENT,
    "high": RecommendationPriority.HIGH,
    "medium": RecommendationPriority.MEDIUM,
    "low": RecommendationPriority.LOW,
}


class RecommendationEngineRepository:
    """Stores Gemini-generated MP development recommendations."""

    def __init__(self, recommendation_repo: RecommendationRepository):
        self.recommendation_repo = recommendation_repo
        self._last_context_hash: str | None = None
        self._last_output: GeminiMpRecommendationOutput | None = None
        self._last_generated_at: datetime | None = None

    @property
    def last_context_hash(self) -> str | None:
        return self._last_context_hash

    def get_cached_output(self, context_hash: str) -> GeminiMpRecommendationOutput | None:
        if self._last_context_hash == context_hash and self._last_output is not None:
            return self._last_output
        return None

    def _department_code(self, department: str) -> str:
        cleaned = "".join(ch for ch in department.upper() if ch.isalnum())[:12]
        return cleaned or "GENERAL"

    def _parse_budget_inr(self, budget: str) -> float | None:
        digits = "".join(ch for ch in budget if ch.isdigit())
        if not digits:
            return None
        value = float(digits)
        if "lakh" in budget.lower() or "lac" in budget.lower():
            return value * 100_000
        if "crore" in budget.lower() or "cr" in budget.lower():
            return value * 10_000_000
        return value

    def _parse_timeline_days(self, timeline: str) -> int | None:
        digits = "".join(ch for ch in timeline if ch.isdigit())
        if not digits:
            return None
        days = int(digits)
        if "week" in timeline.lower():
            return days * 7
        if "month" in timeline.lower():
            return days * 30
        return max(days, 1)

    def _to_create_model(
        self,
        item: MpDevelopmentWorkItem,
        *,
        constituency: str,
        district: str,
        state: str,
        model_version: str,
    ) -> RecommendationCreate:
        dept_code = self._department_code(item.department)
        now = datetime.now(UTC)
        return RecommendationCreate(
            title=item.project_title,
            description=item.detailed_explanation,
            priority=_URGENCY_TO_PRIORITY.get(item.urgency.lower(), RecommendationPriority.MEDIUM),
            cluster_ids=[item.cluster_id] if item.cluster_id else [],
            department_id=f"dept_{dept_code.lower()}",
            department_name=item.department,
            department_code=dept_code,
            village_ids=[],
            constituency=constituency,
            district=district,
            state=state,
            estimated_budget_inr=self._parse_budget_inr(item.estimated_budget),
            estimated_timeline_days=self._parse_timeline_days(item.estimated_resolution_time),
            ai_recommendation=RecommendationAIContent(
                rationale=item.reason,
                action_items=[item.recommended_action],
                expected_impact=item.expected_social_impact,
                risk_assessment=item.risk_if_ignored,
                confidence_score=item.ai_confidence,
                generated_at=now,
                model_version=model_version,
            ),
            metadata=DocumentMetadataCreate(
                created_by=RECOMMENDATION_ENGINE_ACTOR,
                updated_by=RECOMMENDATION_ENGINE_ACTOR,
            ),
        )

    def persist_engine_output(
        self,
        output: GeminiMpRecommendationOutput,
        *,
        context_hash: str,
        constituency: str,
        district: str,
        state: str,
        model_version: str,
    ) -> list[str]:
        ids: list[str] = []
        for item in output.recommendations:
            doc_id = f"engine_{context_hash}_{item.priority_rank:02d}"
            create_model = self._to_create_model(
                item,
                constituency=constituency,
                district=district,
                state=state,
                model_version=model_version,
            )
            existing = self.recommendation_repo.get_by_id(doc_id)
            if existing:
                from app.models.domain.recommendation import RecommendationUpdate

                self.recommendation_repo.update(
                    doc_id,
                    RecommendationUpdate(
                        title=create_model.title,
                        description=create_model.description,
                        priority=create_model.priority,
                        cluster_ids=create_model.cluster_ids,
                        department_id=create_model.department_id,
                        department_name=create_model.department_name,
                        department_code=create_model.department_code,
                        estimated_budget_inr=create_model.estimated_budget_inr,
                        estimated_timeline_days=create_model.estimated_timeline_days,
                        ai_recommendation=create_model.ai_recommendation,
                        status=RecommendationStatus.PENDING_REVIEW,
                        updated_by=RECOMMENDATION_ENGINE_ACTOR,
                    ),
                )
            else:
                self.recommendation_repo.create(create_model, document_id=doc_id)
            ids.append(doc_id)

        self._last_context_hash = context_hash
        self._last_output = output
        self._last_generated_at = datetime.now(UTC)
        logger.info("Persisted %s engine recommendations for context %s", len(ids), context_hash)
        return ids
