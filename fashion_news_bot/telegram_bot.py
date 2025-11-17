import time
import logging
import subprocess
import requests
import os

# ======================================
# CONFIGURACIÓN
# ======================================

TELEGRAM_TOKEN = "8201322215:AAG5ibSGK5XPj-AaeSNWF1K4w_1xikoXvaw"  # <-- pegá tu token real
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Comando para ejecutar tu bot principal
BOT_COMMAND = ["python", "-m", "fashion_news_bot.main"]

LOG_FILE = os.path.join("logs", "bot.log")  # mismo log que usa el bot principal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_control_bot")


# ======================================
# FUNCIONES TELEGRAM
# ======================================

def send_message(chat_id: int, text: str, parse_mode: str | None = None):
    data = {"chat_id": chat_id, "text": text}
    if parse_mode:
        data["parse_mode"] = parse_mode
    try:
        requests.post(f"{BASE_URL}/sendMessage", data=data, timeout=15)
    except Exception as e:
        logger.exception("Error enviando mensaje: %s", e)


def send_document(chat_id: int, filepath: str):
    if not os.path.exists(filepath):
        send_message(chat_id, "⚠️ No encontré el archivo solicitado.")
        return
    try:
        with open(filepath, "rb") as f:
            files = {"document": f}
            data = {"chat_id": chat_id}
            requests.post(f"{BASE_URL}/sendDocument", data=data, files=files, timeout=30)
    except Exception as e:
        logger.exception("Error enviando documento: %s", e)


# ======================================
# MANEJO DE COMANDOS
# ======================================

def handle_start(chat_id: int):
    texto = (
        "👗 *EliteVogueBot conectado*\n\n"
        "Comandos disponibles:\n"
        "/publicar - Ejecutar bot ahora\n"
        "/estado   - Ver últimas líneas del log\n"
        "/logs     - Enviar archivo de log completo\n"
    )
    send_message(chat_id, texto, parse_mode="Markdown")


def handle_publicar(chat_id: int):
    send_message(chat_id, "⏳ Ejecutando bot de moda...")

    try:
        # Ejecutamos el bot principal desde la carpeta raíz
        result = subprocess.run(
            BOT_COMMAND,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        salida = result.stdout[-3500:] if result.stdout else "Sin salida."
        send_message(chat_id, f"✔️ Bot ejecutado.\n\n```{salida}```", parse_mode="Markdown")
    except Exception as e:
        logger.exception("Error al ejecutar el bot:")
        send_message(chat_id, f"❌ Error ejecutando el bot: {e}")


def handle_estado(chat_id: int):
    if not os.path.exists(LOG_FILE):
        send_message(chat_id, "⚠️ Todavía no hay log (aún no se ejecutó el bot).")
        return

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        ultimo = "".join(lines[-20:])
        send_message(chat_id, f"📊 Últimas líneas del log:\n\n```{ultimo}```", parse_mode="Markdown")
    except Exception as e:
        logger.exception("Error leyendo log:")
        send_message(chat_id, f"❌ Error leyendo log: {e}")


def handle_logs(chat_id: int):
    if not os.path.exists(LOG_FILE):
        send_message(chat_id, "⚠️ No existe log todavía.")
        return
    send_document(chat_id, LOG_FILE)


def handle_text_message(chat_id: int, text: str):
    text = text.strip()
    if text.startswith("/start"):
        handle_start(chat_id)
    elif text.startswith("/publicar"):
        handle_publicar(chat_id)
    elif text.startswith("/estado"):
        handle_estado(chat_id)
    elif text.startswith("/logs"):
        handle_logs(chat_id)
    else:
        send_message(chat_id, "No entiendo ese comando. Probá con /start.")


# ======================================
# LOOP PRINCIPAL (LONG POLLING)
# ======================================

def main():
    logger.info("Iniciando bot de control por Telegram...")
    last_update_id = None

    while True:
        try:
            params = {"timeout": 30}
            if last_update_id is not None:
                params["offset"] = last_update_id + 1

            resp = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
            data = resp.json()

            if not data.get("ok"):
                logger.warning("Respuesta no OK de Telegram: %s", data)
                time.sleep(2)
                continue

            for update in data.get("result", []):
                last_update_id = update["update_id"]
                message = update.get("message") or update.get("edited_message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                logger.info("Mensaje de %s: %s", chat_id, text)
                if text:
                    handle_text_message(chat_id, text)

        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario.")
            break
        except Exception as e:
            logger.exception("Error en el loop principal: %s", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
import os
import time
import logging
import subprocess
import requests

# ======================================
# CONFIGURACIÓN
# ======================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("Falta la variable de entorno TELEGRAM_TOKEN")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Comando para ejecutar tu bot principal (el que publica en WordPress)
BOT_COMMAND = ["python", "-m", "fashion_news_bot.main"]

# Ruta del log que genera main.py (dentro del paquete)
LOG_FILE = os.path.join("fashion_news_bot", "logs", "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("telegram_control_bot")


# ======================================
# FUNCIONES TELEGRAM
# ======================================

def send_message(chat_id: int, text: str, parse_mode: str | None = None):
    data = {"chat_id": chat_id, "text": text}
    if parse_mode:
        data["parse_mode"] = parse_mode
    try:
        r = requests.post(f"{BASE_URL}/sendMessage", data=data, timeout=15)
        if not r.ok:
            logger.warning("Error sendMessage: %s", r.text)
    except Exception as e:
        logger.exception("Error enviando mensaje: %s", e)


def send_document(chat_id: int, filepath: str):
    if not os.path.exists(filepath):
        send_message(chat_id, "⚠️ No encontré el archivo solicitado.")
        return
    try:
        with open(filepath, "rb") as f:
            files = {"document": f}
            data = {"chat_id": chat_id}
            r = requests.post(f"{BASE_URL}/sendDocument", data=data, files=files, timeout=60)
        if not r.ok:
            logger.warning("Error sendDocument: %s", r.text)
    except Exception as e:
        logger.exception("Error enviando documento: %s", e)


# ======================================
# MANEJO DE COMANDOS
# ======================================

def handle_start(chat_id: int):
    texto = (
        "👗 *EliteVogue Bot conectado a Render*\n\n"
        "Comandos disponibles:\n"
        "/publicar – Ejecutar bot de moda ahora\n"
        "/estado   – Ver últimas líneas del log\n"
        "/logs     – Enviar archivo de log completo\n"
    )
    send_message(chat_id, texto, parse_mode="Markdown")


def handle_publicar(chat_id: int):
    send_message(chat_id, "⏳ Ejecutando bot de moda en el servidor...")

    try:
        # Ejecutamos el bot principal desde la raíz del repo
        repo_root = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(
            BOT_COMMAND,
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        salida = result.stdout or ""
        salida = salida[-3500:]  # recortar si es muy largo

        msg = f"✔️ Bot ejecutado.\n\n```{salida or 'Sin salida.'}```"
        send_message(chat_id, msg, parse_mode="Markdown")
    except Exception as e:
        logger.exception("Error al ejecutar el bot:")
        send_message(chat_id, f"❌ Error ejecutando el bot: {e}")


def handle_estado(chat_id: int):
    if not os.path.exists(LOG_FILE):
        send_message(chat_id, "⚠️ Todavía no hay log (quizás el bot no corrió aún).")
        return

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        ultimo = "".join(lines[-20:])
        msg = f"📊 Últimas líneas del log:\n\n```{ultimo}```"
        send_message(chat_id, msg, parse_mode="Markdown")
    except Exception as e:
        logger.exception("Error leyendo log:")
        send_message(chat_id, f"❌ Error leyendo log: {e}")


def handle_logs(chat_id: int):
    if not os.path.exists(LOG_FILE):
        send_message(chat_id, "⚠️ No existe log todavía.")
        return
    send_document(chat_id, LOG_FILE)


def handle_text_message(chat_id: int, text: str):
    text = text.strip()
    if text.startswith("/start"):
        handle_start(chat_id)
    elif text.startswith("/publicar"):
        handle_publicar(chat_id)
    elif text.startswith("/estado"):
        handle_estado(chat_id)
    elif text.startswith("/logs"):
        handle_logs(chat_id)
    else:
        send_message(chat_id, "No entiendo ese comando. Probá con /start.")


# ======================================
# LOOP PRINCIPAL (LONG POLLING)
# ======================================

def main():
    logger.info("Iniciando bot de control por Telegram (Render)...")
    last_update_id = None

    while True:
        try:
            params = {"timeout": 30}
            if last_update_id is not None:
                params["offset"] = last_update_id + 1

            resp = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
            data = resp.json()

            if not data.get("ok"):
                logger.warning("Respuesta no OK de Telegram: %s", data)
                time.sleep(5)
                continue

            for update in data.get("result", []):
                last_update_id = update["update_id"]
                message = update.get("message") or update.get("edited_message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                logger.info("Mensaje de %s: %s", chat_id, text)
                if text:
                    handle_text_message(chat_id, text)

        except Exception as e:
            logger.exception("Error en el loop principal: %s", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
