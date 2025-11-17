"""
Statistics helper for the fashion news bot.

This module records simple analytics about published articles, such as
the number of articles per source and per category.  The stats are
persisted in a JSON file defined in configuration.  Stats are not
critical for the bot to function but can help identify which
sources/categories are performing best.
"""

import logging
from typing import Dict

from .storage import load_stats, save_stats

logger = logging.getLogger(__name__)


def update_stats(source: str, category: str) -> None:
    """Increment counters for the given source and category."""
    stats: Dict[str, int] = load_stats()
    source_key = f"source:{source or 'unknown'}"
    category_key = f"category:{category or 'general'}"
    stats[source_key] = stats.get(source_key, 0) + 1
    stats[category_key] = stats.get(category_key, 0) + 1
    save_stats(stats)
    logger.info("Actualizadas estadísticas: %s=%d, %s=%d", source_key, stats[source_key], category_key, stats[category_key])