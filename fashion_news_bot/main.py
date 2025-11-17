"""
Entry point for the fashion news bot.

This script orchestrates the entire workflow: it fetches fresh
articles, classifies them, rewrites them using OpenAI, generates
images, publishes the results to WordPress and updates the stored
state.  It should be run periodically (e.g. via cron) to keep
publishing new fashion content.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, List

from .config import settings
from .scraper import get_fresh_fashion_articles
from .writer import generate_article_text
from .image_generator import generate_fashion_image
from .publisher import WordPressPublisher
from .classifier import classify_article
from .storage import load_published_hashes, save_published_hashes
from .stats import update_stats


def setup_logging() -> None:
    """Configure logging for the bot."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # File handler
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    fh = RotatingFileHandler(
        os.path.join(log_dir, "bot.log"), maxBytes=2 * 1024 * 1024, backupCount=3
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def run_once() -> None:
    """Run a single iteration of the publishing pipeline."""
    logger = logging.getLogger(__name__)
    logger.info("===== INICIO EJECUCIÓN BOT MODA =====")
    articles = get_fresh_fashion_articles()
    if not articles:
        logger.info("No hay artículos nuevos.")
        return
    published_hashes = load_published_hashes()
    wp = WordPressPublisher()
    for art in articles:
        try:
            logger.info("Procesando artículo: %s", art.get("title"))
            # Classify article
            category_label = classify_article(art)
            logger.info("Clasificación: %s", category_label)
            # Generate text
            article_text = generate_article_text(art)
            # Generate image
            image_path = generate_fashion_image(art)
            # Upload image
            media_id: Optional[int] = None
            if image_path:
                media_id = wp.upload_media(image_path)
            # Determine category IDs to assign
            category_ids: Optional[List[int]] = None
            if settings.category_ids and category_label in settings.category_ids:
                category_ids = [settings.category_ids[category_label]]
            # Create post
            post_id = wp.create_post(
                title=article_text["magazine_title"],
                content_html=article_text["body_html"],
                excerpt=article_text["meta_description"],
                categories=category_ids,
                featured_media=media_id,
            )
            logger.info("Publicado post ID %s para hash %s", post_id, art["hash"])
            published_hashes.add(art["hash"])
            # Update stats
            update_stats(art.get("source"), category_label)
        except Exception as e:
            logger.exception("Error procesando artículo '%s': %s", art.get("title"), e)
    # Save state
    save_published_hashes(published_hashes)
    logger.info("===== FIN EJECUCIÓN BOT MODA =====")


if __name__ == "__main__":
    setup_logging()
    run_once()