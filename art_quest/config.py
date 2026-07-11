# config.py (безопасная версия)
import os

# ============================================
# 1. НАСТРОЙКИ TELEGRAM БОТА
# ============================================

# Токен берем из переменных окружения
BOT_TOKEN = os.environ.get('8836224811:AAE3TQ6A_MGUC3-mrEWDWGhgfaAG0l3U5Z4')

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения!")

# ============================================
# 2. НАСТРОЙКИ ВЕБ-ПРИЛОЖЕНИЯ
# ============================================

WEB_APP_URL = os.environ.get('WEB_APP_URL', 'http://localhost:5000')

# ============================================
# 3. НАСТРОЙКИ БАЗЫ ДАННЫХ
# ============================================

# Для Render используем PostgreSQL, если он есть, иначе SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
DB_NAME = "art_quest.db"  # для SQLite

# ============================================
# 4. НАСТРОЙКИ СЕРВЕРА
# ============================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
PORT = int(os.environ.get('PORT', 5000))

# ============================================
# 5. ПАРАМЕТРЫ ИГРЫ
# ============================================

QUESTIONS_PER_QUIZ = int(os.environ.get('QUESTIONS_PER_QUIZ', 10))
POINTS_PER_CORRECT = int(os.environ.get('POINTS_PER_CORRECT', 10))
XP_PER_CORRECT = int(os.environ.get('XP_PER_CORRECT', 15))
XP_PER_LEVEL = int(os.environ.get('XP_PER_LEVEL', 100))

# ============================================
# 6. ДОПОЛНИТЕЛЬНО
# ============================================

WEB_APP_FOLDER = "web_app"

# ============================================
# 7. КОНЕЦ
# ============================================

print(f"✅ Конфигурация загружена. Режим: {'🛠️ РАЗРАБОТКА' if DEBUG else '🚀 ПРОДАКШЕН'}")
