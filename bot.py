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
            "🎨 Открыть Арт-Квест",
            web_app=WebAppInfo(url=config.WEB_APP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "Добро пожаловать в **Арт-Квест** — твою интерактивную энциклопедию!\n\n"
        "📚 **Что тебя ждет:**\n"
        "• 9 дисциплин: литература, история, философия, психология,\n"
        "  социология, музыка, живопись, скульптура, театр\n"
        "• 📖 Обучающие материалы по каждой теме\n"
        "• 🎯 Викторины с разным уровнем сложности\n"
        "• 🏅 Достижения и система уровней\n"
        "• 📊 Отслеживание прогресса\n\n"
        "Нажми на кнопку ниже, чтобы начать!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        await update.message.reply_text("✅ Прогресс сохранён! Продолжай своё путешествие в мир знаний!")
    except:
        await update.message.reply_text("❌ Произошла ошибка при сохранении данных")

def main():
    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("play", start))
    app.add_handler(CommandHandler("web_app_data", handle_web_app_data))
    
    print("🚀 Бот Арт-Квест запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
