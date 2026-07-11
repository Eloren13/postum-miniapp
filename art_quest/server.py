# server.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from database import DB_NAME

app = Flask(__name__, static_folder='web_app')
CORS(app)

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return send_from_directory('web_app', 'index.html')

@app.route('/api/disciplines')
def get_disciplines():
    conn = get_db()
    disciplines = conn.execute('SELECT * FROM disciplines ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(d) for d in disciplines])

@app.route('/api/sections/<int:discipline_id>')
def get_sections(discipline_id):
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

@app.route('/api/discipline-topics/<int:discipline_id>')
def get_discipline_topics(discipline_id):
    conn = get_db()
    topics = conn.execute('''
        SELECT t.* FROM topics t
        JOIN sections s ON s.id = t.section_id
        WHERE s.discipline_id = ?
        ORDER BY t.name
    ''', (discipline_id,)).fetchall()
    conn.close()
    return jsonify([dict(t) for t in topics])

@app.route('/api/questions/random')
def get_random_questions():
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
    conn = get_db()
    material = conn.execute('''
        SELECT lm.*, t.name as topic_name 
        FROM learning_materials lm
        JOIN topics t ON t.id = lm.topic_id
        WHERE lm.id = ?
    ''', (material_id,)).fetchone()
    conn.close()
    return jsonify(dict(material) if material else {})

@app.route('/api/topics/quick')
def get_quick_topics():
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

@app.route('/api/daily')
def get_daily():
    conn = get_db()
    question = conn.execute('''
        SELECT q.*, t.name as topic_name 
        FROM questions q
        JOIN topics t ON t.id = q.topic_id
        ORDER BY RANDOM() 
        LIMIT 1
    ''').fetchone()
    conn.close()
    return jsonify(dict(question) if question else {'question': 'Вопрос не найден'})

@app.route('/api/progress', methods=['POST'])
def save_progress():
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    correct = data.get('correct', False)
    
    conn = get_db()
    
    # Получаем topic_id для вопроса
    topic = conn.execute(
        'SELECT topic_id FROM questions WHERE id = ?',
        (question_id,)
    ).fetchone()
    
    if topic:
        # Обновляем прогресс по теме
        conn.execute('''
            INSERT OR REPLACE INTO user_topic_progress 
            (user_id, topic_id, correct_count, total_count, last_answered)
            VALUES (?, ?, 
                COALESCE((SELECT correct_count FROM user_topic_progress 
                         WHERE user_id = ? AND topic_id = ?), 0) + ?,
                COALESCE((SELECT total_count FROM user_topic_progress 
                         WHERE user_id = ? AND topic_id = ?), 0) + 1,
                ?)
        ''', (user_id, topic[0], user_id, topic[0], 1 if correct else 0,
              user_id, topic[0], datetime.now()))
    
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/achievements')
def get_achievements():
    conn = get_db()
    achievements = conn.execute('SELECT * FROM achievements').fetchall()
    conn.close()
    return jsonify([dict(a) for a in achievements])

@app.route('/api/check-achievements', methods=['POST'])
def check_achievements():
    data = request.json
    user_id = data.get('id')
    
    conn = get_db()
    
    # Проверяем достижения
    achievements = conn.execute('SELECT * FROM achievements').fetchall()
    unlocked = []
    
    for a in achievements:
        # Проверяем, не разблокировано ли уже
        existing = conn.execute(
            'SELECT * FROM user_achievements WHERE user_id = ? AND achievement_id = ?',
            (user_id, a['id'])
        ).fetchone()
        
        if existing:
            continue
        
        # Проверяем условия
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
            # Подсчитываем уникальные дисциплины, в которых есть ответы
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
                'INSERT INTO user_achievements (user_id, achievement_id, unlocked_at) VALUES (?, ?, ?)',
                (user_id, a['id'], datetime.now())
            )
            unlocked.append(a['name'])
    
    conn.commit()
    conn.close()
    
    return jsonify({'unlocked': unlocked})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
