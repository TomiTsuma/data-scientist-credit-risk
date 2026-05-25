"""Configuration for the Sunculture AI assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from src.config.config import Config as ProjectConfig

PROJECT = ProjectConfig()


@dataclass(frozen=True)
class AiPlatformConfig:
    root_dir: Path = PROJECT.root_dir
    workspace_root: Path = PROJECT.root_dir / "workspace"
    sessions_dir: Path = field(init=False)
    workspace_dir: Path = field(init=False)  # legacy alias → sessions_dir
    processed_dir: Path = PROJECT.processed_dir
    models_dir: Path = PROJECT.models_dir
    reports_dir: Path = PROJECT.reports_dir

    provider: str = field(
        default_factory=lambda: os.getenv("SUNAI_PROVIDER", "openai")
    )
    model: str = field(
        default_factory=lambda: os.getenv("SUNAI_MODEL", "gpt-4o-mini")
    )
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_base_url: str = field(
        default_factory=lambda: os.getenv(
            "OPENAI_BASE_URL", "https://api.openai.com/v1"
        ).rstrip("/")
    )
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        ).rstrip("/")
    )
    max_tool_iterations: int = field(
        default_factory=lambda: int(os.getenv("SUNAI_MAX_ITERATIONS", "25"))
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "sessions_dir", self.workspace_root / "sessions")
        object.__setattr__(self, "workspace_dir", self.sessions_dir)

    @property
    def customer_features_path(self) -> Path:
        return self.processed_dir / "customer_features_base.parquet"

    @property
    def customer_segments_path(self) -> Path:
        return self.processed_dir / "customer_segments.parquet"


AI_CONFIG = AiPlatformConfig()
