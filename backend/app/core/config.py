"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _parse_cors_origins(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    return value


class Settings(BaseSettings):
    """Centralized application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="CivicLens AI", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        alias="ENVIRONMENT",
    )
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    cors_origins: Annotated[
        list[str],
        NoDecode,
        BeforeValidator(_parse_cors_origins),
    ] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://civiclensai-buildwithai.vercel.app",
        ],
        alias="CORS_ORIGINS",
    )

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    gemini_max_retries: int = Field(default=3, alias="GEMINI_MAX_RETRIES")
    gemini_prompt_version: str = Field(default="1.0.0", alias="GEMINI_PROMPT_VERSION")
    ai_analysis_enabled: bool = Field(default=True, alias="AI_ANALYSIS_ENABLED")
    vision_analysis_enabled: bool = Field(default=True, alias="VISION_ANALYSIS_ENABLED")
    vision_prompt_version: str = Field(default="1.0.0", alias="VISION_PROMPT_VERSION")
    vision_max_image_dimension: int = Field(default=1600, alias="VISION_MAX_IMAGE_DIMENSION")
    vision_jpeg_quality: int = Field(default=85, alias="VISION_JPEG_QUALITY")
    clustering_enabled: bool = Field(default=True, alias="CLUSTERING_ENABLED")
    clustering_prompt_version: str = Field(default="1.0.0", alias="CLUSTERING_PROMPT_VERSION")
    clustering_max_candidates: int = Field(default=8, alias="CLUSTERING_MAX_CANDIDATES")
    clustering_candidate_pool_size: int = Field(default=100, alias="CLUSTERING_CANDIDATE_POOL_SIZE")
    clustering_radius_km: float = Field(default=2.0, alias="CLUSTERING_RADIUS_KM")
    clustering_recent_days: int = Field(default=90, alias="CLUSTERING_RECENT_DAYS")
    clustering_min_heuristic_score: float = Field(default=0.2, alias="CLUSTERING_MIN_HEURISTIC_SCORE")
    clustering_duplicate_threshold: int = Field(default=70, alias="CLUSTERING_DUPLICATE_THRESHOLD")
    clustering_comparison_cache_ttl: int = Field(default=3600, alias="CLUSTERING_COMPARISON_CACHE_TTL")
    priority_engine_enabled: bool = Field(default=True, alias="PRIORITY_ENGINE_ENABLED")
    priority_prompt_version: str = Field(default="1.0.0", alias="PRIORITY_PROMPT_VERSION")
    priority_cache_ttl: int = Field(default=3600, alias="PRIORITY_CACHE_TTL")
    priority_ranking_limit: int = Field(default=500, alias="PRIORITY_RANKING_LIMIT")
    recommendation_engine_enabled: bool = Field(default=True, alias="RECOMMENDATION_ENGINE_ENABLED")
    recommendation_prompt_version: str = Field(default="1.0.0", alias="RECOMMENDATION_PROMPT_VERSION")
    recommendation_cache_ttl: int = Field(default=3600, alias="RECOMMENDATION_CACHE_TTL")

    admin_email: str = Field(default="admin@civiclens.ai", alias="ADMIN_EMAIL")
    admin_password: str = Field(default="admin123", alias="ADMIN_PASSWORD")
    jwt_secret: str = Field(default="super-secret-jwt-key-civiclens-ai-2026", alias="JWT_SECRET")

    firebase_service_account_path: str | None = Field(
        default=None,
        alias="FIREBASE_SERVICE_ACCOUNT_PATH",
    )
    firebase_service_account_json: str | None = Field(
        default=None,
        alias="FIREBASE_SERVICE_ACCOUNT_JSON",
    )
    firestore_emulator_host: str | None = Field(
        default=None,
        alias="FIRESTORE_EMULATOR_HOST",
    )

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
