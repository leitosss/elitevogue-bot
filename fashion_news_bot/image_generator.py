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
    """Generate and save an image for the given article using Imagen 3.

    Returns the path to the saved image or None if generation fails or
    no API key is provided.
    """
    os.makedirs(settings.images_output_dir, exist_ok=True)

    if client is None:
        # Sin API key, no intentamos generar
        return None

    # Prompt según estilo elegido
    prompt = (
        "Editorial fashion photography, luxury magazine style, dramatic lighting, "
        "high-end wardrobe, premium textures, elegant composition. "
        if settings.writer_style == "luxury"
        else "Streetwear editorial photography, urban setting, fresh and modern aesthetics, "
             "dynamic composition, natural light, stylish outfits. "
    )

    prompt += (
        "High quality, professional studio feel, no recognizable faces, can be conceptual: "
        "runway silhouettes, fabrics in motion, accessories, or urban details depending on context. "
        "Inspired by: " + (article.get("title") or "fashion")
    )

    try:
        logger.info("Generando imagen con Gemini / Imagen 3…")

        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
            ),
        )

        # Tomamos la primera imagen generada
        generated = response.generated_images[0]

        # Algunas versiones de la SDK devuelven image_bytes, otras un objeto PIL.
        # Usamos la forma más general.
        if hasattr(generated.image, "image_bytes"):
            img = Image.open(BytesIO(generated.image.image_bytes))
        else:
            # En algunos ejemplos la imagen viene ya como PIL.Image
            img = generated.image  # type: ignore

        file_name = f"img_{article.get('hash', 'img')}.jpg"
        file_path = os.path.join(settings.images_output_dir, file_name)
        img.save(file_path, format="JPEG")

        logger.info("Imagen guardada en %s", file_path)
        return file_path

    except Exception as e:
        logger.error("Error al generar imagen con Gemini: %s", e)
        return None
