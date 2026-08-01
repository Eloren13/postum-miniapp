# bot.py
import json
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import config
from database import init_db, seed_database

# Инициализация базы данных
init_db()
seed_database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [
        [InlineKeyboardButton(
            "Открыть Арт-Квест",
            web_app=WebAppInfo(url=config.WEB_APP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Привет, {user.first_name}.\n\n"
        "*Арт-Квест* — интерактивная энциклопедия по искусству, истории и гуманитарным наукам.\n\n"
        "*Внутри:*\n"
        "— 10 дисциплин: литература, история, философия, психология, социология, "
        "музыка, живопись, скульптура, театр, архитектура\n"
        "— Более 500 вопросов и 130 обучающих статей о конкретных людях и событиях\n"
        "— Викторины с выбором дисциплины, темы и сложности\n"
        "— Достижения, уровни и ежедневный вопрос дня\n\n"
        "Открыть мини-приложение — кнопка ниже.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        await update.message.reply_text("Прогресс сохранён.")
    except:
        await update.message.reply_text("Не удалось сохранить данные. Попробуйте ещё раз.")

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("play", start))
    app.add_handler(CommandHandler("web_app_data", handle_web_app_data))

    print("Бот Арт-Квест запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()
