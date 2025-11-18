import os
import requests
from typing import Dict

# ================================================================
#   LEER CREDENCIALES DESDE RENDER
# ================================================================
WP_USER = os.getenv("WP_USER")          # usuario WP
WP_PASSWORD = os.getenv("WP_PASSWORD")  # application password WP
WP_API_URL = "https://elitevogue.online/wp-json/wp/v2/posts"


# ================================================================
#   CLASIFICADOR
# ================================================================
def classify_article(article: Dict) -> str:
    text = " ".join([
        article.get("title") or "",
        article.get("description") or "",
        article.get("content") or "",
    ]).lower()

    categories = {
        "portadas": [
            "portada", "cover", "editorial photo", "front page",
            "producción", "modelo destacada", "shoot", "sesión"
        ],
        "moda": [
            "moda", "fashion", "outfit", "vestido", "colección",
            "desfile", "runway", "silhouette", "estilismo"
        ],
        "tendencias": [
            "tendencia", "trend", "temporada", "color del año",
            "estará de moda", "forecast", "pronóstico"
        ],
        "belleza": [
            "maquillaje", "makeup", "skincare", "belleza",
            "cosmética", "fragancia", "piel"
        ],
        "editorial": [
            "reflexión", "poético", "crónica", "ensayo",
            "observación", "profundo"
        ],
        "lifestyle": [
            "lujo", "lifestyle", "inspiración",
            "estilo de vida", "viaje"
        ],
        "cultura_visual": [
            "visual", "estética", "fotografía",
            "imagen", "simbolismo"
        ],
        "entrevistas": [
            "entrevista", "modelo", "diseñador",
            "perfil", "nos cuenta", "historia"
        ],
    }

    for category, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                return category

    return "moda"  # por defecto


# ================================================================
#   MAPEAR CATEGORÍAS A IDS (CAMBIAR ESTOS NÚMEROS)
# ================================================================
CATEGORY_ID_MAP = {
    "moda":            6,   # <-- CAMBIAR
    "tendencias":      12,   # <-- CAMBIAR
    "belleza":         7,  # <-- REAL
    "editorial":       9,   # <-- CAMBIAR
    "lifestyle":       8,   # <-- CAMBIAR
    "cultura_visual":  10,   # <-- CAMBIAR
    "portadas":        5,   # <-- CAMBIAR
    "entrevistas":     11,   # <-- CAMBIAR
}


# ================================================================
#   PUBLICACIÓN EN WORDPRESS
# ================================================================
def publish_article_to_wp(article: Dict):
    # 1) Clasificar
    category_key = classify_article(article)
    category_id = CATEGORY_ID_MAP.get(category_key)

    if not category_id:
        category_id = CATEGORY_ID_MAP["moda"]  # fallback seguro

    payload = {
        "title": article["title"],
        "content": article["content"],
        "status": "publish",
        "categories": [category_id],
    }

    response = requests.post(
        WP_API_URL,
        json=payload,
        auth=(WP_USER, WP_PASSWORD),
    )

    try:
        response.raise_for_status()
        print("Publicado OK en categoría:", category_key)
        return response.json()
    except Exception as e:
        print("Error publicando:", response.text)
        raise e

