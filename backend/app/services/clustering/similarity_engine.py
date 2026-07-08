"""Heuristic similarity scoring and candidate filtering for duplicate detection."""

from __future__ import annotations

import logging
import math
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.core.config import Settings
from app.models.domain.complaint import ComplaintResponse
from app.repositories.complaint_repository import ComplaintRepository
from app.repositories.village_repository import VillageRepository

logger = logging.getLogger(__name__)

WARD_PATTERN = re.compile(r"\bward\s*[#:]?\s*(\d+|[a-z]+)\b", re.IGNORECASE)

SEVERITY_WEIGHTS = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "critical": 4.0,
}


@dataclass(frozen=True)
class CandidateScore:
    """Heuristic similarity result for a candidate complaint."""

    complaint: ComplaintResponse
    heuristic_score: float
    distance_km: float | None
    keyword_overlap: int
    department_match: bool
    pin_code_match: bool
    ward_match: bool


class ComparisonCache:
    """In-memory TTL cache for Gemini comparison results."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, object]] = {}

    def get(self, key: str) -> object | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: object) -> None:
        self._store[key] = (time.time() + self._ttl, value)


_comparison_cache = ComparisonCache()


def get_comparison_cache() -> ComparisonCache:
    return _comparison_cache


def haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Calculate great-circle distance between two GPS points in kilometers."""
    radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def extract_ward(text: str | None) -> str | None:
    """Extract ward identifier from landmark or address text."""
    if not text:
        return None
    match = WARD_PATTERN.search(text)
    if match:
        return match.group(1).lower()
    return None


def _normalize_tokens(values: list[str]) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for token in re.split(r"[^a-z0-9]+", value.lower()):
            if len(token) >= 3:
                tokens.add(token)
    return tokens


def _severity_value(complaint: ComplaintResponse) -> float:
    if complaint.image_analysis and complaint.image_analysis.severity:
        return SEVERITY_WEIGHTS.get(complaint.image_analysis.severity.lower(), 2.0)
    if complaint.ai_analysis and complaint.ai_analysis.severity:
        return SEVERITY_WEIGHTS.get(complaint.ai_analysis.severity.lower(), 2.0)
    return 2.0


class SimilarityEngine:
    """Filters and ranks candidate complaints before Gemini matching."""

    def __init__(
        self,
        complaint_repo: ComplaintRepository,
        village_repo: VillageRepository,
        settings: Settings,
    ):
        self.complaint_repo = complaint_repo
        self.village_repo = village_repo
        self.settings = settings

    def _resolve_pin_code(self, complaint: ComplaintResponse) -> str | None:
        if complaint.village_id == "citizen_portal":
            return None
        village = self.village_repo.get_by_id(complaint.village_id)
        if village and village.pin_code:
            return village.pin_code
        return None

    def _department(self, complaint: ComplaintResponse) -> str:
        if complaint.ai_analysis and complaint.ai_analysis.responsible_department:
            return complaint.ai_analysis.responsible_department.strip().lower()
        if complaint.ai_analysis and complaint.ai_analysis.required_department:
            return complaint.ai_analysis.required_department.strip().lower()
        return ""

    def _keywords(self, complaint: ComplaintResponse) -> set[str]:
        tokens: set[str] = set()
        if complaint.ai_analysis:
            tokens |= _normalize_tokens(complaint.ai_analysis.keywords)
            tokens |= _normalize_tokens(complaint.ai_analysis.tags)
            tokens |= _normalize_tokens([complaint.ai_analysis.category, complaint.ai_analysis.sub_category])
        if complaint.image_analysis:
            tokens |= _normalize_tokens(complaint.image_analysis.detected_objects)
            tokens |= _normalize_tokens(complaint.image_analysis.duplicate_indicators)
            tokens |= _normalize_tokens([complaint.image_analysis.primary_issue])
        tokens |= _normalize_tokens([complaint.title, complaint.description])
        if complaint.landmark:
            tokens |= _normalize_tokens([complaint.landmark])
        return tokens

    def _score_candidate(
        self,
        source: ComplaintResponse,
        candidate: ComplaintResponse,
        *,
        source_pin: str | None,
        source_ward: str | None,
        source_keywords: set[str],
        source_department: str,
    ) -> CandidateScore | None:
        if candidate.id == source.id:
            return None

        distance_km: float | None = None
        if source.location and candidate.location:
            distance_km = haversine_km(
                source.location.latitude,
                source.location.longitude,
                candidate.location.latitude,
                candidate.location.longitude,
            )
            if distance_km > self.settings.clustering_radius_km:
                return None

        candidate_department = self._department(candidate)
        department_match = bool(
            source_department
            and candidate_department
            and (
                source_department in candidate_department
                or candidate_department in source_department
            )
        )
        if source_department and candidate_department and not department_match:
            return None

        candidate_pin = self._resolve_pin_code(candidate)
        pin_code_match = bool(source_pin and candidate_pin and source_pin == candidate_pin)

        candidate_ward = extract_ward(candidate.landmark) or extract_ward(
            candidate.location.address if candidate.location else None
        )
        ward_match = bool(source_ward and candidate_ward and source_ward == candidate_ward)

        if source.village_id != "citizen_portal" and candidate.village_id != source.village_id:
            if distance_km is None or distance_km > self.settings.clustering_radius_km * 0.5:
                if not pin_code_match:
                    return None

        candidate_keywords = self._keywords(candidate)
        keyword_overlap = len(source_keywords & candidate_keywords)

        title_similarity = 0.0
        source_title = source.title.lower()
        candidate_title = candidate.title.lower()
        if source_title == candidate_title:
            title_similarity = 1.0
        elif source_title in candidate_title or candidate_title in source_title:
            title_similarity = 0.7
        else:
            source_title_tokens = _normalize_tokens([source.title])
            candidate_title_tokens = _normalize_tokens([candidate.title])
            if source_title_tokens & candidate_title_tokens:
                title_similarity = 0.4

        distance_score = 0.0
        if distance_km is not None:
            distance_score = max(0.0, 1.0 - (distance_km / self.settings.clustering_radius_km))

        image_match = 0.0
        if source.image_analysis and candidate.image_analysis:
            if (
                source.image_analysis.primary_issue.lower()
                == candidate.image_analysis.primary_issue.lower()
                and source.image_analysis.primary_issue.lower() != "unknown"
            ):
                image_match = 0.25
            shared_objects = set(source.image_analysis.detected_objects) & set(
                candidate.image_analysis.detected_objects
            )
            if shared_objects:
                image_match += min(0.15, len(shared_objects) * 0.05)

        severity_delta = abs(_severity_value(source) - _severity_value(candidate))
        severity_score = max(0.0, 1.0 - (severity_delta / 3.0))

        keyword_score = min(1.0, keyword_overlap / 5.0)

        heuristic_score = (
            (title_similarity * 0.25)
            + (keyword_score * 0.25)
            + (distance_score * 0.2)
            + (severity_score * 0.1)
            + (image_match)
            + (0.1 if department_match else 0.0)
            + (0.05 if pin_code_match else 0.0)
            + (0.05 if ward_match else 0.0)
        )

        if heuristic_score < self.settings.clustering_min_heuristic_score:
            return None

        return CandidateScore(
            complaint=candidate,
            heuristic_score=round(heuristic_score, 4),
            distance_km=distance_km,
            keyword_overlap=keyword_overlap,
            department_match=department_match,
            pin_code_match=pin_code_match,
            ward_match=ward_match,
        )

    def find_candidates(self, complaint: ComplaintResponse) -> list[CandidateScore]:
        """Retrieve and rank candidate complaints for Gemini duplicate matching."""
        from app.db.pagination import PaginationParams
        from app.models.domain.complaint import ComplaintSearchFilters

        cutoff = datetime.now(UTC) - timedelta(days=self.settings.clustering_recent_days)
        filters = ComplaintSearchFilters(
            category=complaint.category,
            submitted_after=cutoff,
        )
        if complaint.village_id != "citizen_portal":
            filters.village_id = complaint.village_id
        else:
            filters.district = complaint.district

        pagination = PaginationParams(
            limit=min(200, self.settings.clustering_candidate_pool_size),
            order_by="submitted_at",
            order_direction="desc",
        )
        result = self.complaint_repo.list(filters=filters, pagination=pagination)

        source_pin = self._resolve_pin_code(complaint)
        source_ward = extract_ward(complaint.landmark) or extract_ward(
            complaint.location.address if complaint.location else None
        )
        source_keywords = self._keywords(complaint)
        source_department = self._department(complaint)

        scored: list[CandidateScore] = []
        for candidate in result.items:
            score = self._score_candidate(
                complaint,
                candidate,
                source_pin=source_pin,
                source_ward=source_ward,
                source_keywords=source_keywords,
                source_department=source_department,
            )
            if score is not None:
                scored.append(score)

        scored.sort(key=lambda item: item.heuristic_score, reverse=True)
        top = scored[: self.settings.clustering_max_candidates]
        logger.info(
            "Similarity engine found %s candidates (top %s) for complaint %s",
            len(scored),
            len(top),
            complaint.id,
        )
        return top
