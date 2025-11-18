"""
Clasificador editorial para EliteVogue.

Clasifica artículos según su contenido en categorías profesionales:
portadas, moda, tendencias, belleza, editorial, lifestyle,
cultura_visual, entrevistas.
"""

from typing import Dict


def classify_article(article: Dict) -> str:
    """Devuelve una categoría editorial basada en keywords."""

    text = " ".join([
        article.get("title") or "",
        article.get("description") or "",
        article.get("content") or "",
    ]).lower()

    categories = {
        "portadas": [
            "portada", "cover", "editorial photo", "front page", "producción",
            "modelo destacada", "shoot", "sesión fotográfica"
        ],
        "moda": [
            "moda", "fashion", "outfit", "vestido", "colección", "desfile",
            "runway", "silhouette", "estilismo", "look", "prenda"
        ],
        "tendencias": [
            "tendencia", "trend", "temporada", "color del año", "pronóstico",
            "futuro de la moda", "trend report", "forecast", "estará de moda"
        ],
        "belleza": [
            "maquillaje", "makeup", "skincare", "belleza", "cosmética",
            "fragancia", "perfume", "piel", "labial", "cuidado"
        ],
        "editorial": [
            "reflexión", "poético", "crónica", "análisis profundo",
            "ensayo", "narrativa", "metáfora", "estética conceptual",
            "observación", "sensibilidad"
        ],
        "lifestyle": [
            "lujo", "viaje", "lifestyle", "experiencia", "inspiración",
            "estilo de vida", "wellness", "vivir", "cultura moderna"
        ],
        "cultura_visual": [
            "visual", "estética", "fotografía", "imagen", "simbolismo",
            "arte", "composición", "color", "sombra", "contraste"
        ],
        "entrevistas": [
            "entrevista", "dialogo", "conversación", "perfil",
            "historia de vida", "modelo", "diseñador", "creador",
            "hablamos con", "nos cuenta"
        ],
    }

    for category, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                return category

    # Si no coincide nada:
    return "moda"
