"""Shared test fixture initialization."""

from pathlib import Path

from archive_insight.preview import warm_preview_profile

PREVIEW_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "release-preview.link"
warm_preview_profile(PREVIEW_FIXTURE)
