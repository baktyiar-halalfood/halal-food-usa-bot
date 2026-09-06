import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕌 Halal Food USA\n\n"
        "Отправьте свою геолокацию 📍, и я помогу найти халяльную еду рядом."
    )

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    await update.message.reply_text(
        f"📍 Геолокация получена!\n\n"
        f"Широта: {loc.latitude}\n"
        f"Долгота: {loc.longitude}\n\n"
        "Скоро здесь появится поиск халяльной кухни рядом."
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location))

    app.run_polling()

if __name__ == "__main__":
    main()
