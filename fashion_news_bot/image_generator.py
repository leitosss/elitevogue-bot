"""
Image generator for the fashion news bot.

This module uses Google Gemini / Imagen 3 to create a
beautiful, magazine-style image for each article. If no API key is
provided or the generation fails, it returns None. Images are saved
into the configured images directory.
"""

import os
import logging
from typing import Dict, Optional
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image

from .config import settings

logger = logging.getLogger(__name__)

# ======================================
# CLIENTE GEMINI / IMAGEN
# ======================================

# Intentamos leer primero desde settings (si lo agregaste ahí),
# y si no, directamente de la variable de entorno GEMINI_API_KEY.
gemini_api_key = getattr(settings, "gemini_api_key", None) or os.environ.get(
    "GEMINI_API_KEY"
)

if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)
else:
    client = None
    logger.warning(
        "GEMINI_API_KEY no configurada. image_generator.py trabajará en modo dummy."
    )


# ======================================
# FUNCIÓN PRINCIPAL
# ======================================

def generate_fashion_image(article: Dict) -> Optional[str]:
    os.makedirs(settings.images_output_dir, exist_ok=True)

    if client is None:
        return None

    # Prompt según estilo
    prompt = (
        "High-end editorial fashion photo, luxury magazine style, dramatic lighting, "
        "premium fabrics, elegant composition. "
        if settings.writer_style == "luxury"
        else "Urban streetwear fashion editorial photo, modern aesthetics, dynamic pose, "
             "natural city lighting. "
    )
    prompt += (
        "High quality, no recognizable faces. Inspired by: " +
        (article.get('title') or "fashion")
    )

    try:
        logger.info("Generando imagen con modelo imagegeneration@002…")

        response = client.models.generate_images(
            model="imagegeneration@002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
            ),
        )

        generated = response.generated_images[0]

        # Obtener bytes
        if hasattr(generated.image, "image_bytes"):
            img_bytes = generated.image.image_bytes
        else:
            logger.error("No se encontraron image_bytes en la respuesta")
            return None

        img = Image.open(BytesIO(img_bytes))

        file_name = f"img_{article.get('hash','img')}.jpg"
        file_path = os.path.join(settings.images_output_dir, file_name)
        img.save(file_path, "JPEG")

        logger.info("Imagen guardada en %s", file_path)
        return file_path

    except Exception as e:
        logger.error("Error generando imagen: %s", e)
        return None

