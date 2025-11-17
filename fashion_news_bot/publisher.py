"""
Publisher module for posting articles to WordPress.

This module wraps the WordPress REST API to upload media and create
posts.  Categories and excerpts can be set when creating a post.
"""

import logging
import os
from typing import Optional, List

import requests

from .config import settings

logger = logging.getLogger(__name__)


class WordPressPublisher:
    """A simple wrapper around the WordPress REST API for posting articles."""

    def __init__(self) -> None:
        if not settings.wp_base_url:
            raise ValueError("WP_BASE_URL no configurada")
        self.base_url = settings.wp_base_url.rstrip("/")
        self.user = settings.wp_user
        self.app_password = settings.wp_app_password
        if not self.user or not self.app_password:
            raise ValueError("WP_USER o WP_APP_PASSWORD no configurados")

    def _auth(self) -> tuple:
        return (self.user, self.app_password)

    def upload_media(self, image_path: str) -> Optional[int]:
        """Upload an image to WordPress and return the media ID.

        Returns None if the upload fails.
        """
        if not image_path or not os.path.exists(image_path):
            logger.warning("Imagen no encontrada: %s", image_path)
            return None
        url = f"{self.base_url}/wp-json/wp/v2/media"
        filename = os.path.basename(image_path)
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
        with open(image_path, "rb") as f:
            files = {"file": (filename, f, "image/png")}
            logger.info("Subiendo media a WordPress…")
            resp = requests.post(url, headers=headers, files=files, auth=self._auth(), timeout=60)
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error("Error subiendo media: %s", e)
            return None
        media_id = resp.json().get("id")
        logger.info("Media subida. ID: %s", media_id)
        return media_id

    def create_post(
        self,
        title: str,
        content_html: str,
        excerpt: str = "",
        categories: Optional[List[int]] = None,
        featured_media: Optional[int] = None,
    ) -> int:
        """Create a new WordPress post and return its ID."""
        url = f"{self.base_url}/wp-json/wp/v2/posts"
        payload = {
            "title": title,
            "content": content_html,
            "status": "publish",
        }
        if excerpt:
            payload["excerpt"] = excerpt
        if featured_media:
            payload["featured_media"] = featured_media
        if categories:
            payload["categories"] = categories
        logger.info("Creando post en WordPress…")
        resp = requests.post(url, json=payload, auth=self._auth(), timeout=60)
        resp.raise_for_status()
        post_id = resp.json().get("id")
        logger.info("Post creado. ID: %s", post_id)
        return post_id