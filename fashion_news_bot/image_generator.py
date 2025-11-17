"""
Image generator for the fashion news bot.

This module uses the OpenAI image API (gpt-image-1) to create a
beautiful, magazine‑style image for each article.  If no API key is
provided or the generation fails, it returns None.  Images are saved
into the configured images directory.
"""

import os
import logging
from typing import Dict, Optional
import base64

from openai import OpenAI

from .config import settings

logger = logging.getLogger(__name__)


client = None
if settings.openai_api_key:
    client = OpenAI(api_key=settings.openai_api_key)
else:
    logger.warning(
        "OPENAI_API_KEY no configurada. image_generator.py trabajará en modo dummy."
    )


def generate_fashion_image(article: Dict) -> Optional[str]:
    """Generate and save an image for the given article.

    Returns the path to the saved image or None if generation fails or
    no API key is provided.
    """
    os.makedirs(settings.images_output_dir, exist_ok=True)
    if client is None:
        # Without API key, don't attempt to generate
        return None
    # Build prompt using article title and style
    prompt = (
        "Fotografía editorial de moda, estilo revista de lujo. "
        if settings.writer_style == "luxury"
        else "Fotografía de streetwear urbana, con estética fresca y moderna. "
    )
    prompt += (
        "Alta calidad, iluminación profesional, composición cuidada. "
        "Sin rostros reconocibles; puede ser conceptual: pasarela, siluetas, telas en movimiento, "
        "accesorios de lujo o elementos urbanos según corresponda. "
        "Inspirado en: " + (article.get("title") or "moda")
    )

    try:
        logger.info("Generando imagen con OpenAI…")
        img_response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024" if settings.writer_style == "luxury" else "640x960",  # 16:9 vs 4:5
            n=1,
        )
        image_b64 = img_response.data[0].b64_json
        img_bytes = base64.b64decode(image_b64)
        file_name = f"img_{article.get('hash','img')}.png"
        file_path = os.path.join(settings.images_output_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(img_bytes)
        logger.info("Imagen guardada en %s", file_path)
        return file_path
    except Exception as e:
        logger.error("Error al generar imagen: %s", e)
        return None