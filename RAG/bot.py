import os
import re
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    MessageHandler, filters
)

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8100")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN no está configurado en .env")

# Usuarios que ya recibieron el mensaje de bienvenida (en memoria).
# Si reinicias el bot seguido, esto se reinicia también.
usuarios_conocidos = set()

SALUDOS = {
    "hola", "buenas", "buenos días", "buenas tardes", "buenas noches",
    "hey", "que tal", "qué tal", "saludos"
}

MENSAJE_BIENVENIDA = (
    "⛪ Hola, soy el asistente virtual de EcclesiaSys.\n\n"
    "Puedes escribirme cualquier pregunta y te ayudaré a resolverla. 🙏"
)


def es_saludo(texto: str) -> bool:
    limpio = re.sub(r"[^\w\sáéíóúñ]", "", texto.lower()).strip()
    return limpio in SALUDOS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Se dispara cuando Telegram manda /start (ej. primer contacto o deep link)."""
    chat_id = update.effective_chat.id
    usuarios_conocidos.add(chat_id)
    await update.message.reply_text(MENSAJE_BIENVENIDA)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text

    if not text:
        await update.message.reply_text("Envía una pregunta en texto.")
        return

    # Primer contacto sin haber pasado por /start (ej. escribió directo "Hola")
    if chat_id not in usuarios_conocidos:
        usuarios_conocidos.add(chat_id)
        await update.message.reply_text(MENSAJE_BIENVENIDA)
        return

    # Saludo posterior (ya lo conocemos, pero no es una pregunta real)
    if es_saludo(text):
        await update.message.reply_text(
            "¡Hola de nuevo! Cuéntame qué necesitas y te ayudo."
        )
        return

    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": text},
            timeout=30,
        )
        response.raise_for_status()
    except Exception:
        await update.message.reply_text(
            "No pude conectar con el servicio en este momento. Intenta de nuevo en unos minutos."
        )
        return

    data = response.json()
    answer = data.get("answer", "No obtuve una respuesta clara para eso.")

    await update.message.reply_text(f"📖 {answer}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()