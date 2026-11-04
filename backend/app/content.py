"""Paths to the content and curricula folders at the repo root."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"
