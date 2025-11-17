# Fashion News Bot

Este proyecto es un bot de noticias de moda que recolecta artículos recientes de
diversas fuentes, los reescribe con un estilo editorial de lujo o
urbano, genera imágenes y los publica automáticamente en un sitio
WordPress.  Además evita publicaciones duplicadas, traduce textos al
español, clasifica los artículos y registra estadísticas básicas.

## Características principales

1. **Recolección de noticias:**
   - Puede usar la API de NewsAPI si se configura (`USE_NEWSAPI=true`) para
     obtener artículos recientes relacionados con moda.  También soporta
     feeds RSS personalizados (WWD, FashionNetwork, Vogue, etc.).  Es
     configurable desde el fichero `.env`.
   - Deduplicación de artículos mediante un hash de fuente, URL y título.

2. **Reescritura editorial con OpenAI:**
   - El bot utiliza el modelo GPT de OpenAI para reescribir el contenido
     original y crear un artículo entre 400 y 900 palabras con un
     estilo profesional.
   - Soporta estilos “luxury” (lujo, sofisticado) y “streetwear” (urbano,
     contemporáneo).  Ajusta el tono, las keywords SEO y la longitud
     según el estilo.
   - Puede traducir automáticamente al español neutro si la información
     original está en otro idioma (`TRANSLATION_ENABLED=true`).

3. **Clasificación de artículos:**
   - Clasifica cada artículo en una de las categorías: pasarela,
     streetwear, belleza, negocio o general, según la presencia de
     palabras clave.
   - Las categorías se asignan en WordPress utilizando IDs definidos en
     `.env` (`WP_CATEGORY_RUNWAY`, `WP_CATEGORY_STREET`, etc.).  Si no
     defines un ID, esa categoría no se asignará.

4. **Generación de imágenes:**
   - Usa la API de imágenes de OpenAI (gpt‑image‑1) para crear una
     imagen alusiva al artículo.  El tamaño y la estética cambian
     según el estilo de escritura.

5. **Publicación en WordPress:**
   - Subida automática de la imagen como media y creación del post con
     título, contenido HTML y un extracto como meta descripción.
   - Soporta asignar categorías al post.

6. **Estado persistente y estadísticas:**
   - Guarda los hashes de artículos publicados en `data/published.json` para
     evitar repeticiones.
   - Registra estadísticas simples (número de artículos por fuente y por
     categoría) en `data/stats.json`.

## Instalación

1. Clona este repositorio y entra al directorio:

   ```bash
   git clone <repo>
   cd fashion_news_bot
   ```

2. Crea y activa un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Copia `.env.example` a `.env` y edita los valores:

   ```bash
   cp .env.example .env
   # Edítalo con tus claves y opciones
   ```

## Ejecución

Para ejecutar el bot manualmente:

```bash
python -m fashion_news_bot.main
```

Esto procesará hasta `MAX_ARTICLES_PER_RUN` artículos nuevos (por defecto 3).

### Automatización con cron (Hostinger/VPS)

Puedes programar la ejecución cada cierto tiempo con cron.  Por ejemplo,
cada 3 horas:

```cron
0 */3 * * * /ruta/a/venv/bin/python /ruta/a/fashion_news_bot/fashion_news_bot/main.py >> /ruta/a/logs/cron.log 2>&1
```

Reemplaza las rutas según tu sistema.  Recuerda que Hostinger permite
programar trabajos periódicos desde el panel de control.

## Configuración avanzada

Las siguientes variables del `.env` permiten personalizar el comportamiento:

| Variable                 | Descripción                                                       | Ejemplo                                     |
|------------------------- |------------------------------------------------------------------ |---------------------------------------------|
| `NEWSAPI_KEY`           | API key de NewsAPI.org.                                           | `abc123`                                    |
| `USE_NEWSAPI`           | `true` para usar NewsAPI, `false` para desactivarlo.               | `false`                                     |
| `NEWSAPI_QUERY`         | Consulta de búsqueda para NewsAPI.                                | `fashion OR moda`                          |
| `RSS_FEEDS`             | Lista de URLs RSS separadas por comas.                            | `https://wwd.com/custom-feed/fashion/,...`  |
| `OPENAI_API_KEY`        | API key de OpenAI para generar textos e imágenes.                 |                                               |
| `WP_BASE_URL`           | URL base de tu WordPress sin slash final.                         | `https://midominio.com`                     |
| `WP_USER`               | Usuario de WordPress (recomendable crear uno de aplicación).      | `bot_user`                                  |
| `WP_APP_PASSWORD`       | Contraseña de aplicación generada en WordPress.                   | `xyz123`                                    |
| `MAX_ARTICLES_PER_RUN`  | Número máximo de artículos a publicar en cada ejecución.          | `3`                                         |
| `TRANSLATION_ENABLED`   | `true` para traducir al español si el artículo está en otro idioma.| `true`                                      |
| `WRITER_STYLE`          | `luxury` o `streetwear` para elegir el tono de escritura.         | `streetwear`                                |
| `WP_CATEGORY_RUNWAY`    | ID de la categoría “pasarela” en WordPress.                      | `7`                                         |
| `WP_CATEGORY_STREET`    | ID de la categoría “streetwear” en WordPress.                    | `8`                                         |
| `WP_CATEGORY_BEAUTY`    | ID de la categoría “belleza” en WordPress.                        | `9`                                         |
| `WP_CATEGORY_BUSINESS`  | ID de la categoría “negocio” en WordPress.                        | `10`                                        |
| `WP_CATEGORY_GENERAL`   | ID de la categoría “general” en WordPress (por defecto).           | `11`                                        |

## Consejos adicionales

- **Términos de uso**: Antes de reutilizar contenido de feeds RSS, verifica las
  políticas de cada medio. Algunos permiten lectura personal pero no
  republicación integral. Usa el bot como herramienta de curaduría y
  análisis, no para copiar texto literal.【833058960778333†L102-L116】.

- **Optimización SEO**: Los artículos generados incluyen un `meta_description`
  para servir como extracto en WordPress.  Puedes ajustar la longitud o
  generar descripciones adicionales mediante un plugin.

- **Ampliaciones**: Puedes extender la clasificación, integrar otros
  modelos de traducción, almacenar las respuestas en bases de datos o
  enviar notificaciones al terminar cada ciclo.  La estructura modular
  facilita añadir nuevas fuentes o estilos.

¡Disfruta automatizando tu revista de moda! 👜