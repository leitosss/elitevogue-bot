"""
Configuration module for the fashion news bot.

This module reads environment variables from a `.env` file (using
python‑dotenv) and exposes them via a dataclass.  It supports toggling
features such as NewsAPI usage, translation, writer style and WordPress
category assignments.  All paths are resolved relative to the project
directory.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Resolve the base directory of this file (the project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env if present
ENV_PATH = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)


@dataclass
class Settings:
    """Holds configuration values for the bot.

    Values may be overridden through environment variables.  See
    `.env.example` for a list of variables.
    """

    # News API
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")
    use_newsapi: bool = os.getenv("USE_NEWSAPI", "true").lower() == "true"
    newsapi_query: str = os.getenv("NEWSAPI_QUERY", "fashion OR moda")

    # RSS feeds (comma separated list in env)
    rss_feeds: list = field(default_factory=list)

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # WordPress credentials
    wp_base_url: str = os.getenv("WP_BASE_URL", "")
    wp_user: str = os.getenv("WP_USER", "")
    wp_app_password: str = os.getenv("WP_APP_PASSWORD", "")

    # Article generation
    max_articles_per_run: int = int(os.getenv("MAX_ARTICLES_PER_RUN", "3"))
    translation_enabled: bool = os.getenv("TRANSLATION_ENABLED", "true").lower() == "true"
    writer_style: str = os.getenv("WRITER_STYLE", "luxury").lower()  # luxury or streetwear

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Directories for output
    images_output_dir: str = os.path.join(BASE_DIR, "images")
    articles_output_dir: str = os.path.join(BASE_DIR, "data")
    published_db_path: str = os.path.join(BASE_DIR, "data", "published.json")
    stats_db_path: str = os.path.join(BASE_DIR, "data", "stats.json")

    # Category ID mappings (from env variables like WP_CATEGORY_RUNWAY)
    category_ids: dict = field(default_factory=dict)

    def __post_init__(self):
        # Parse RSS feeds from environment if provided
        rss = os.getenv("RSS_FEEDS", "")
        if rss:
            self.rss_feeds = [url.strip() for url in rss.split(",") if url.strip()]
        # Build category mapping using environment variables
        categories = {}
        # Expect environment variables such as WP_CATEGORY_RUNWAY=7
        for key, default_name in [
            ("RUNWAY", "pasarela"),
            ("STREET", "street"),
            ("BEAUTY", "belleza"),
            ("BUSINESS", "negocio"),
            ("GENERAL", "general"),
        ]:
            env_key = f"WP_CATEGORY_{key}"
            value = os.getenv(env_key)
            if value:
                try:
                    categories[default_name] = int(value)
                except ValueError:
                    pass
        self.category_ids = categories


# Instantiate settings
settings = Settings()