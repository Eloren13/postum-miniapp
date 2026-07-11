# server.py (обновленная версия)
import os
import threading
import time
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import config
from database import init_db, seed_database, get_db

# ============================================
# 1. ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ
# ============================================
init_db()
seed_database()

# ============================================
# 2. СОЗДАНИЕ FLASK ПРИЛОЖЕНИЯ
# ============================================
app = Flask(__name__, static_folder='web_app')
CORS(app)

# ============================================
# 3. МАРШРУТЫ ДЛЯ ВЕБ-ПРИЛОЖЕНИЯ
# ============================================

@app.route('/')
def index():
    """Главная страница мини-приложения"""
    return send_from_directory('web_app', 'index.html')

@app.route('/api/disciplines')
def get_disciplines():
    """Получение списка дисциплин"""
    conn = get_db()
    disciplines = conn.execute('SELECT * FROM disciplines ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(d) for d in disciplines])

@app.route('/api/sections/<int:discipline_id>')
def get_sections(discipline_id):
    """Получение разделов по дисциплине"""
    conn = get_db()
    sections = conn.execute(
        'SELECT * FROM sections WHERE discipline_id = ? ORDER BY order_num',
        (discipline_id,)
    ).fetchall()
    discipline = conn.execute(
        'SELECT name FROM disciplines WHERE id = ?',
        (discipline_id,)
    ).fetchone()
    conn.close()
    return jsonify({
        'discipline_name': discipline['name'] if discipline else '',
        'sections': [dict(s) for s in sections]
    })

@app.route('/api/topics/<int:section_id>')
def get_topics(section_id):
    """Получение тем по разделу"""
    conn = get_db()
    topics = conn.execute('''
        SELECT t.*, COUNT(q.id) as question_count 
        FROM topics t
        LEFT JOIN questions q ON q.topic_id = t.id
        WHERE t.section_id = ?
        GROUP BY t.id
        ORDER BY t.order_num
    ''', (section_id,)).fetchall()
    section = conn.execute(
        'SELECT name FROM sections WHERE id = ?',
        (section_id,)
    ).fetchone()
    conn.close()
    return jsonify({
        'section_name': section['name'] if section else '',
        'topics': [dict(t) for t in topics]
    })

@app.route('/api/questions/random')
def get_random_questions():
    """Получение случайных вопросов"""
    limit = int(request.args.get('limit', 10))
    topic_id = request.args.get('topic')
    discipline_id = request.args.get('discipline')
    difficulty = request.args.get('difficulty')
    
    conn = get_db()
    query = '''
        SELECT q.*, t.name as topic_name 
        FROM questions q
        LEFT JOIN topics t ON t.id = q.topic_id
        LEFT JOIN sections s ON s.id = t.section_id
        WHERE 1=1
    '''
    params = []
    
    if topic_id and topic_id != 'all':
        query += ' AND q.topic_id = ?'
        params.append(int(topic_id))
    elif discipline_id and discipline_id != 'all':
        query += ' AND s.discipline_id = ?'
        params.append(int(discipline_id))
    
    if difficulty and difficulty != 'all':
        query += ' AND q.difficulty = ?'
        params.append(int(difficulty))
    
    query += ' ORDER BY RANDOM() LIMIT ?'
    params.append(limit)
    
    questions = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(q) for q in questions])

@app.route('/api/questions/topic/<int:topic_id>')
def get_topic_questions(topic_id):
    """Получение вопросов по теме"""
    limit = int(request.args.get('limit', 10))
    conn = get_db()
    questions = conn.execute('''
        SELECT q.*, t.name as topic_name 
        FROM questions q
        JOIN topics t ON t.id = q.topic_id
        WHERE q.topic_id = ?
        ORDER BY RANDOM() 
        LIMIT ?
    ''', (topic_id, limit)).fetchall()
    conn.close()
    return jsonify([dict(q) for q in questions])

@app.route('/api/learning')
def get_learning_materials():
    """Получение обучающих материалов"""
    conn = get_db()
    materials = conn.execute('''
        SELECT lm.*, t.name as topic_name 
        FROM learning_materials lm
        JOIN topics t ON t.id = lm.topic_id
        ORDER BY lm.order_num
        LIMIT 20
    ''').fetchall()
    conn.close()
    return jsonify([dict(m) for m in materials])

@app.route('/api/material/<int:material_id>')
def get_material(material_id):
    """Получение конкретного материала"""
    conn = get_db()
    material = conn.execute('''
        SELECT lm.*, t.name as topic_name 
        FROM learning_materials lm
        JOIN topics t ON t.id = lm.topic_id
        WHERE lm.id = ?
    ''', (material_id,)).fetchone()
    conn.close()
    return jsonify(dict(material) if material else {})

@app.route('/api/daily')
def get_daily():
    """Ежедневный вопрос"""
    conn = get_db()
    question = conn.execute('''
        SELECT q.*, t.name as topic_name 
        FROM questions q
        JOIN topics t ON t.id = q.topic_id
        ORDER BY RANDOM() 
        LIMIT 1
    ''') .fetchone()
    conn.close()
    return jsonify(dict(question) if question else {'question': 'Вопрос не найден'})

@app.route('/api/progress', methods=['POST'])
def save_progress():
    """Сохранение прогресса пользователя"""
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    correct = data.get('correct', False)
    
    conn = get_db()
    topic = conn.execute(
        'SELECT topic_id FROM questions WHERE id = ?',
        (question_id,)
    ).fetchone()
    
    if topic:
        conn.execute('''
            INSERT OR REPLACE INTO user_topic_progress 
            (user_id, topic_id, correct_count, total_count, last_answered)
            VALUES (?, ?, 
                COALESCE((SELECT correct_count FROM user_topic_progress 
                         WHERE user_id = ? AND topic_id = ?), 0) + ?,
                COALESCE((SELECT total_count FROM user_topic_progress 
                         WHERE user_id = ? AND topic_id = ?), 0) + 1,
                datetime('now')
            )
        ''', (user_id, topic[0], user_id, topic[0], 1 if correct else 0,
              user_id, topic[0]))
    
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/achievements')
def get_achievements():
    """Получение достижений"""
    conn = get_db()
    achievements = conn.execute('SELECT * FROM achievements').fetchall()
    conn.close()
    return jsonify([dict(a) for a in achievements])

@app.route('/api/discipline-topics/<int:discipline_id>')
def get_discipline_topics(discipline_id):
    """Получение тем по дисциплине"""
    conn = get_db()
    topics = conn.execute('''
        SELECT t.* FROM topics t
        JOIN sections s ON s.id = t.section_id
        WHERE s.discipline_id = ?
        ORDER BY t.name
    ''', (discipline_id,)).fetchall()
    conn.close()
    return jsonify([dict(t) for t in topics])

@app.route('/api/topics/quick')
def get_quick_topics():
    """Быстрые темы для главной страницы"""
    conn = get_db()
    topics = conn.execute('''
        SELECT t.*, d.icon 
        FROM topics t
        JOIN sections s ON s.id = t.section_id
        JOIN disciplines d ON d.id = s.discipline_id
        ORDER BY RANDOM() 
        LIMIT 4
    ''').fetchall()
    conn.close()
    return jsonify({'topics': [dict(t) for t in topics]})

@app.route('/api/check-achievements', methods=['POST'])
def check_achievements():
    """Проверка достижений пользователя"""
    data = request.json
    user_id = data.get('id')
    
    conn = get_db()
    achievements = conn.execute('SELECT * FROM achievements').fetchall()
    unlocked = []
    
    for a in achievements:
        existing = conn.execute(
            'SELECT * FROM user_achievements WHERE user_id = ? AND achievement_id = ?',
            (user_id, a['id'])
        ).fetchone()
        
        if existing:
            continue
        
        condition_type = a['condition_type']
        condition_value = a['condition_value']
        progress = 0
        
        if condition_type == 'correct_answers':
            progress = data.get('correct_answers', 0)
        elif condition_type == 'topics_completed':
            progress = conn.execute(
                'SELECT COUNT(*) FROM user_topic_progress WHERE user_id = ? AND completed = 1',
                (user_id,)
            ).fetchone()[0]
        elif condition_type == 'disciplines_completed':
            progress = conn.execute('''
                SELECT COUNT(DISTINCT s.discipline_id) 
                FROM user_topic_progress utp
                JOIN topics t ON t.id = utp.topic_id
                JOIN sections s ON s.id = t.section_id
                WHERE utp.user_id = ? AND utp.total_count > 0
            ''', (user_id,)).fetchone()[0]
        elif condition_type == 'total_score':
            progress = data.get('score', 0)
        
        if progress >= condition_value:
            conn.execute(
                'INSERT INTO user_achievements (user_id, achievement_id, unlocked_at) VALUES (?, ?, datetime("now"))',
                (user_id, a['id'])
            )
            unlocked.append(a['name'])
    
    conn.commit()
    conn.close()
    return jsonify({'unlocked': unlocked})

# ============================================
# 4. ЗАПУСК БОТА В ФОНОВОМ ПОТОКЕ
# ============================================

def run_bot():
    """Запуск Telegram бота в отдельном потоке"""
    try:
        from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, ContextTypes
        import config
        
        print("🤖 Запуск Telegram бота...")
        
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
        
        # Создаем приложение бота
        bot_app = Application.builder().token(config.BOT_TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", start))
        bot_app.add_handler(CommandHandler("play", start))
        
        print("🚀 Бот запущен и готов к работе!")
        bot_app.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()

# ============================================
# 5. ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================

if __name__ == '__main__':
    # Запускаем бота в фоновом потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Даем боту время на инициализацию
    time.sleep(2)
    
    # Запускаем Flask сервер
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Веб-сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
