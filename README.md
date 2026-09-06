# halal-food-usa-bot
Telegram bot for Halal Food USA
import os
import sqlite3

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

NAME, ADDRESS, PHONE, LOCATION = range(4)


def init_db():
    conn = sqlite3.connect("kitchens.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kitchens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            latitude REAL,
            longitude REAL
        )
    """)
    conn.commit()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕌 Halal Food USA\n\n"
        "📍 Отправьте местоположение, чтобы найти халяльные кухни рядом.\n\n"
        "Администратор может добавить кухню командой /addkitchen"
    )


async def add_kitchen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите название кухни:")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введите полный адрес кухни:")
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("Введите телефон кухни:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    keyboard = [[KeyboardButton("📍 Отправить геолокацию кухни", request_location=True)]]

    await update.message.reply_text(
        "Теперь отправьте точную геолокацию кухни 📍",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return LOCATION


async def save_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location

    conn = sqlite3.connect("kitchens.db")
    conn.execute(
        """
        INSERT INTO kitchens
        (name, address, phone, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            context.user_data["name"],
            context.user_data["address"],
            context.user_data["phone"],
            loc.latitude,
            loc.longitude,
        ),
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(
        "✅ Кухня сохранена!\n\n"
        f"🍽 {context.user_data['name']}\n"
        f"📍 {context.user_data['address']}\n"
        f"📞 {context.user_data['phone']}",
        reply_markup=ReplyKeyboardRemove(),
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Добавление отменено.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    init_db()

    app = Application.builder().token(TOKEN).build()

    add_handler = ConversationHandler(
        entry_points=[CommandHandler("addkitchen", add_kitchen)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            LOCATION: [MessageHandler(filters.LOCATION, save_location)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(add_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
