import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8100")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN no está configurado en .env")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        await update.message.reply_text("Envía una pregunta en texto.")
        return

    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": text},
            timeout=30,
        )
        response.raise_for_status()
    except Exception as exc:
        await update.message.reply_text(
            f"Error al consultar la API: {exc}"
        )
        return

    data = response.json()
    answer = data.get("answer", "No obtuve respuesta.")

    reply = f"🤖 Respuesta:\n{answer}"

    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
