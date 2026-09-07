import os
import sqlite3

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

NAME, ADDRESS, PHONE = range(3)


def init_db():
    conn = sqlite3.connect("kitchens.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kitchens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕌 Halal Food USA\n\n"
        "📍 Отправьте свою геолокацию, чтобы найти халяльную кухню рядом."
    )


async def addkitchen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "➕ Добавляем новую кухню.\n\n"
        "Напишите название кухни:"
    )
    return NAME


async def kitchen_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📍 Теперь напишите полный адрес кухни:")
    return ADDRESS


async def kitchen_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("📞 Теперь напишите номер телефона:")
    return PHONE


async def kitchen_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    conn = sqlite3.connect("kitchens.db")
    conn.execute(
        "INSERT INTO kitchens (name, address, phone) VALUES (?, ?, ?)",
        (
            context.user_data["name"],
            context.user_data["address"],
            context.user_data["phone"],
        ),
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(
        "✅ Кухня добавлена!\n\n"
        f"🍽 {context.user_data['name']}\n"
        f"📍 {context.user_data['address']}\n"
        f"📞 {context.user_data['phone']}"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Добавление отменено.")
    return ConversationHandler.END


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location

    await update.message.reply_text(
        "📍 Геолокация получена!\n\n"
        f"Широта: {loc.latitude}\n"
        f"Долгота: {loc.longitude}\n\n"
        "🔎 Поиск ближайших халяльных кухонь скоро подключим."
    )


def main():
    init_db()

    app = Application.builder().token(TOKEN).build()

    add_kitchen_handler = ConversationHandler(
        entry_points=[CommandHandler("addkitchen", addkitchen)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, kitchen_name)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, kitchen_address)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, kitchen_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(add_kitchen_handler)
    app.add_handler(MessageHandler(filters.LOCATION, location))

    app.run_polling()


if __name__ == "__main__":
    main()
