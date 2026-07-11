# config.py
import os

# ============================================
# ⚠️ ВРЕМЕННО: ТОКЕН ПРЯМО В КОДЕ
# ⚠️ НЕ КОММИТЬТЕ ЭТОТ ФАЙЛ В ПУБЛИЧНЫЙ РЕПОЗИТОРИЙ!
# ============================================

BOT_TOKEN = "8836224811:AAH352CQXMaaoNmqNqir8GOSIa0qKGd56lY"

# ============================================
# ОСТАЛЬНЫЕ НАСТРОЙКИ
# ============================================

WEB_APP_URL = os.environ.get('WEB_APP_URL', 'https://postum-miniapp.onrender.com')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Параметры игры
QUESTIONS_PER_QUIZ = int(os.environ.get('QUESTIONS_PER_QUIZ', 10))
POINTS_PER_CORRECT = int(os.environ.get('POINTS_PER_CORRECT', 10))
XP_PER_CORRECT = int(os.environ.get('XP_PER_CORRECT', 15))
XP_PER_LEVEL = int(os.environ.get('XP_PER_LEVEL', 100))
WEB_APP_FOLDER = "web_app"

print("=" * 60)
print("✅ КОНФИГУРАЦИЯ ЗАГРУЖЕНА (ТОКЕН В КОДЕ)")
print("=" * 60)
print(f"  BOT_TOKEN: {'✅ УСТАНОВЛЕН' if BOT_TOKEN else '❌ НЕ УСТАНОВЛЕН'}")
print(f"  WEB_APP_URL: {WEB_APP_URL}")
print("=" * 60)
