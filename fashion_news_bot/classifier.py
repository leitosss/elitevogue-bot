"""
Simple keyword‑based classifier for fashion articles.

This module provides a function to classify an article into broad
categories based on its textual content.  It is a basic heuristic
approach; for more sophisticated classification consider using a
machine‑learning model or external API.
"""

from typing import Dict


def classify_article(article: Dict) -> str:
    """Classify an article into a high‑level category.

    The classification is based on presence of keywords in the article's
    title, description or content.  Returns one of:
    ``pasarela`` (runway), ``street`` (streetwear), ``belleza``
    (beauty), ``negocio`` (business) or ``general``.
    """
    text = " ".join([
        article.get("title") or "",
        article.get("description") or "",
        article.get("content") or "",
    ]).lower()
    categories = {
        "pasarela": ["runway", "pasarela", "fashion show", "catwalk"],
        "street": ["street style", "streetwear", "street fashion", "urbano"],
        "belleza": ["beauty", "cosmetics", "maquillaje", "fragancia", "perfume", "skincare"],
        "negocio": ["business", "negocio", "retail", "industry", "industria", "empresa", "mercado"],
    }
    for category, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                return category
    return "general"