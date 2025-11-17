"""
Storage helpers for the fashion news bot.

This module provides functions for reading and writing the persistent
state used by the bot.  It stores hashes of already published
articles to avoid duplication and simple statistics about which
sources and categories have been published.
"""

import json
import os
from typing import Set, Dict

from .config import settings


def _ensure_dirs() -> None:
    """Ensure that the data directory exists."""
    os.makedirs(os.path.dirname(settings.published_db_path), exist_ok=True)


def load_published_hashes() -> Set[str]:
    """Load the set of article hashes that have already been published."""
    _ensure_dirs()
    if not os.path.exists(settings.published_db_path):
        return set()
    try:
        with open(settings.published_db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("hashes", []))
    except Exception:
        return set()


def save_published_hashes(hashes: Set[str]) -> None:
    """Persist the set of article hashes that have been published."""
    _ensure_dirs()
    with open(settings.published_db_path, "w", encoding="utf-8") as f:
        json.dump({"hashes": list(hashes)}, f, ensure_ascii=False, indent=2)


def load_stats() -> Dict[str, int]:
    """Load statistics about published articles.

    Returns a dict with keys like `source:category` and integer counts.  If
    the file does not exist, returns an empty dict.
    """
    _ensure_dirs()
    if not os.path.exists(settings.stats_db_path):
        return {}
    try:
        with open(settings.stats_db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_stats(stats: Dict[str, int]) -> None:
    """Save statistics dictionary to disk."""
    _ensure_dirs()
    with open(settings.stats_db_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)