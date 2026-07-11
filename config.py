# config.py
import os
import sys

# ============================================
# 1. ПОЛУЧЕНИЕ ТОКЕНА
# ============================================

# Пробуем получить токен из переменных окружения
BOT_TOKEN = os.environ.get('8836224811:AAH352CQXMaaoNmqNqir8GOSIa0qKGd56lY')

# Если не найден, пробуем другие варианты
if not BOT_TOKEN:
    BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not BOT_TOKEN:
    BOT_TOKEN = os.environ.get('TOKEN')

# Если всё равно None - показываем ошибку
if not BOT_TOKEN:
    print("=" * 60)
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    print("=" * 60)
    print("Доступные переменные окружения:")
    for key in os.environ.keys():
        if 'TOKEN' in key.upper() or 'BOT' in key.upper():
            print(f"  - {key} = {os.environ.get(key)[:10]}... (обрезано)")
    print("=" * 60)
    raise ValueError("❌ BOT_TOKEN не найден в переменных окружения!")

# ============================================
# 2. ОСТАЛЬНЫЕ НАСТРОЙКИ
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

# ============================================
# 3. ВЫВОД ИНФОРМАЦИИ
# ============================================

print("=" * 60)
print("✅ КОНФИГУРАЦИЯ ЗАГРУЖЕНА УСПЕШНО!")
print("=" * 60)
print(f"  BOT_TOKEN: {'✅ УСТАНОВЛЕН' if BOT_TOKEN else '❌ НЕ УСТАНОВЛЕН'}")
print(f"  WEB_APP_URL: {WEB_APP_URL}")
print(f"  DEBUG: {DEBUG}")
print(f"  PORT: {PORT}")
print("=" * 60)
