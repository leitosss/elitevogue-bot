"""
Article generator module for the fashion news bot.

This module uses the OpenAI API to rewrite raw news content into a
luxurious magazine article or a streetwear piece, depending on
configuration.  It can also translate source material into Spanish if
translation is enabled and the original language is not Spanish.

If the OpenAI API key is not provided the module returns a basic
placeholder article to allow the rest of the pipeline to run.
"""

import logging
from typing import Dict
import re                     # 👈 nuevo
import markdown  
from openai import OpenAI
from langdetect import detect, LangDetectException

from .config import settings

logger = logging.getLogger(__name__)


# Preconfigure OpenAI client if API key is available
client = None
if settings.openai_api_key:
    client = OpenAI(api_key=settings.openai_api_key)
else:
    logger.warning(
        "OPENAI_API_KEY no configurada. writer.py trabajará en modo dummy."
    )


# Style templates for different writer styles
STYLE_TEMPLATES = {
    "luxury": (
        "Estilo: lujoso, editorial, sofisticado, comparable a Vogue, Harper’s Bazaar, Elle o WWD.\n"
        "Tono: profesional, aspiracional y elegante, evita jerga vulgar.\n"
        "Palabras clave SEO de forma natural: moda, pasarela, tendencias, lujo.\n"
        "Estructura: título llamativo, subtítulo elegante, cuerpo de 400‑900 palabras con\n"
        "introducción profesional, contexto de tendencias, análisis editorial, datos de marca/diseñador y\n"
        "conclusión inspiradora.\n"
    ),
    "streetwear": (
        "Estilo: urbano, contemporáneo, con influencia de streetwear y cultura pop.\n"
        "Tono: fresco, atrevido y con referencias a la cultura de la calle, pero manteniendo coherencia y buen gusto.\n"
        "Palabras clave SEO de forma natural: street style, streetwear, urbano, tendencias.\n"
        "Estructura: título impactante, subtítulo pegadizo, cuerpo de 300‑700 palabras con\n"
        "introducción audaz, contexto cultural, análisis de prendas/marcas, guiños a influencers y\n"
        "cierre motivador.\n"
    ),
}
def markdown_a_html_bonito(texto: str) -> str:
    """
    Convierte markdown a HTML con una estructura limpia y elegante.
    """
    # Opcional: subir un nivel los títulos ### a ## para que se vean más grandes
    texto = re.sub(r"^###\s+", "## ", texto, flags=re.MULTILINE)

    html = markdown.markdown(
        texto,
        extensions=["extra", "sane_lists"]
    )

    # Primer párrafo como "bajada" si querés algo más editorial
    html = re.sub(
        r"<p>(.*?)</p>",
        r'<p class="elitevogue-lead">\1</p>',
        html,
        count=1
    )

    # Contenedor para poder estilizar fácil desde el theme
    return f'<div class="elitevogue-article">{html}</div>'

def _detect_language(text: str) -> str:
    """Detect the language of a piece of text using langdetect.

    Returns a two‑letter ISO 639‑1 language code, or 'unknown' on failure.
    """
    try:
        return detect(text)  # e.g. 'es', 'en'
    except LangDetectException:
        return "unknown"


def generate_article_text(article: Dict) -> Dict:
    """Generate an editorial article in Spanish based on a raw article dictionary.

    The dictionary is expected to contain keys `title`, `description` and
    `content`.  The output dictionary contains keys:

    - magazine_title: the refined title
    - subtitle: a stylish subtitle
    - raw_markdown: the article content in markdown
    - body_html: the article content in simple HTML
    - meta_description: a short meta description for SEO
    - category: optional; classification label provided externally
    """
    # Concatenate available fields as the input for rewriting
    base_content = (
        (article.get("title") or "")
        + "\n\n"
        + (article.get("description") or "")
        + "\n\n"
        + (article.get("content") or "")
    )[:8000]

    # Detect language for possible translation
    lang = _detect_language(base_content)
    logger.info("Idioma detectado: %s", lang)

    # Determine style instructions
    style_key = settings.writer_style if settings.writer_style in STYLE_TEMPLATES else "luxury"
    style_instructions = STYLE_TEMPLATES[style_key]

    # Dummy mode: return simple placeholder if no OpenAI key
    if client is None:
        logger.warning("Sin OPENAI_API_KEY: devolviendo contenido de ejemplo.")
        dummy_title = article.get("title", "Artículo de moda")
        dummy_subtitle = "Subtítulo de ejemplo"
        dummy_body = (
            f"# {dummy_title}\n\n"
            f"## {dummy_subtitle}\n\n"
            "Este artículo es un marcador de posición generado localmente. "
            "Configura OPENAI_API_KEY para obtener texto editorial real."
        )
        return {
            "magazine_title": dummy_title,
            "subtitle": dummy_subtitle,
            "raw_markdown": dummy_body,
            "body_html": dummy_body.replace("\n\n", "<br><br>"),
            "meta_description": dummy_title,
        }

    # Compose prompt for OpenAI
    translation_instruction = (
        "Traduce toda la información al español neutro antes de escribir el artículo. "
        if settings.translation_enabled and lang != "es"
        else ""
    )
    prompt = (
        "Eres un redactor senior de una revista de moda. "
        + translation_instruction
        + "A partir de la siguiente información original (título, descripción y contenido), "
        + "reformula y redacta un artículo completamente nuevo en español neutro. "
        + style_instructions
        + "\n\nInformación original:\n"  # separate the content
        + base_content
        + "\n\n## Instrucciones adicionales:\n"
        + "* No copies literalmente el texto original; reescribe con tu propio estilo.\n"
        + "* Si la fuente original es muy corta, amplía la información con contexto de moda actual.\n"
        + "* Usa subtítulos y párrafos para estructurar el artículo.\n"
    )

    logger.info("Llamando a OpenAI para generar texto editorial...")
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )
    raw_markdown = response.output[0].content[0].text

    # ============================
    # Formateo bonito de salida
    # ============================

    # Extraer título y subtítulo desde el markdown
    magazine_title = article.get("title", "Artículo de moda")
    subtitle = ""
    lines = raw_markdown.strip().splitlines()

    if lines:
        # primer encabezado como título
        for line in lines:
            if line.startswith("#"):
                magazine_title = line.lstrip("# ").strip()
                break

    for line in lines:
        if line.startswith("##"):
            subtitle = line.lstrip("# ").strip()
            break

    # Limpiar posibles restos de markdown en título/subtítulo
    magazine_title = re.sub(r"[*_`#]", "", magazine_title).strip()
    subtitle = re.sub(r"[*_`#]", "", subtitle).strip()

    # Meta description: texto plano sin signos de markdown
    clean_text = re.sub(r"[#*_`]", " ", raw_markdown)
    clean_text = clean_text.replace("\n", " ")
    meta_description = clean_text[:155].strip() + "…"

    # Convertir el cuerpo a HTML bonito
    body_html = markdown_a_html_bonito(raw_markdown)

    return {
        "magazine_title": magazine_title,
        "subtitle": subtitle,
        "raw_markdown": raw_markdown,
        "body_html": body_html,
        "meta_description": meta_description,
    }
