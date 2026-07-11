# database.py
import sqlite3
import json
from datetime import datetime

DB_NAME = "art_quest.db"

def init_db():
    """Создание всех таблиц"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица дисциплин
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disciplines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT,
            description TEXT,
            color TEXT
        )
    ''')
    
    # Таблица разделов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discipline_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            order_num INTEGER,
            FOREIGN KEY (discipline_id) REFERENCES disciplines(id)
        )
    ''')
    
    # Таблица тем
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            order_num INTEGER,
            FOREIGN KEY (section_id) REFERENCES sections(id)
        )
    ''')
    
    # Таблица вопросов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer INTEGER NOT NULL,
            difficulty INTEGER DEFAULT 1,
            explanation TEXT,
            image_url TEXT,
            type TEXT DEFAULT 'quiz',
            FOREIGN KEY (topic_id) REFERENCES topics(id)
        )
    ''')
    
    # Таблица обучающих материалов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT DEFAULT 'text',
            image_url TEXT,
            video_url TEXT,
            order_num INTEGER,
            FOREIGN KEY (topic_id) REFERENCES topics(id)
        )
    ''')
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            total_answers INTEGER DEFAULT 0,
            last_active TIMESTAMP,
            daily_streak INTEGER DEFAULT 0,
            last_daily TIMESTAMP
        )
    ''')
    
    # Таблица прогресса по темам
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_topic_progress (
            user_id INTEGER,
            topic_id INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            correct_count INTEGER DEFAULT 0,
            total_count INTEGER DEFAULT 0,
            last_answered TIMESTAMP,
            PRIMARY KEY (user_id, topic_id)
        )
    ''')
    
    # Таблица достижений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            condition_type TEXT,
            condition_value INTEGER,
            xp_reward INTEGER
        )
    ''')
    
    # Таблица пользовательских достижений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            user_id INTEGER,
            achievement_id INTEGER,
            unlocked_at TIMESTAMP,
            PRIMARY KEY (user_id, achievement_id),
            FOREIGN KEY (achievement_id) REFERENCES achievements(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована!")

def seed_database():
    """Заполнение базы данных начальными данными"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже данные
    cursor.execute('SELECT COUNT(*) FROM disciplines')
    count = cursor.fetchone()[0]
    if count > 0:
        print("✅ База данных уже заполнена!")
        conn.close()
        return
    
    # Добавляем дисциплины
    disciplines = [
        ('Литература', '📖', 'Художественные произведения и их анализ', '#8B4513'),
        ('История', '🏛️', 'Исторические события и личности', '#2C3E50'),
        ('Философия', '🤔', 'Философские учения и мыслители', '#8E44AD'),
        ('Психология', '🧠', 'Человеческое поведение и мышление', '#2980B9'),
        ('Социология', '👥', 'Общество и социальные отношения', '#27AE60'),
        ('Музыка', '🎵', 'Музыкальные произведения и композиторы', '#E67E22'),
        ('Живопись', '🎨', 'Изобразительное искусство и художники', '#E74C3C'),
        ('Скульптура', '🗿', 'Скульптурные произведения и скульпторы', '#95A5A6'),
        ('Театр', '🎭', 'Театральное искусство и драматургия', '#F39C12')
    ]
    
    cursor.executemany('''
        INSERT INTO disciplines (name, icon, description, color)
        VALUES (?, ?, ?, ?)
    ''', disciplines)
    
    # Получаем ID дисциплин
    cursor.execute('SELECT id, name FROM disciplines')
    disc_ids = {name: id for id, name in cursor.fetchall()}
    
    # Добавляем разделы
    sections_data = [
        (disc_ids['Литература'], 'Русская литература XIX века', 'Золотой век русской литературы', 1),
        (disc_ids['Литература'], 'Зарубежная литература', 'Мировая классическая литература', 2),
        (disc_ids['История'], 'Древний мир', 'Цивилизации древности', 1),
        (disc_ids['Философия'], 'Античная философия', 'Философия Древней Греции и Рима', 1),
        (disc_ids['Психология'], 'Основы психологии', 'Базовые психологические концепции', 1),
        (disc_ids['Музыка'], 'Классическая музыка', 'Музыкальные произведения классического периода', 1),
        (disc_ids['Живопись'], 'Ренессанс', 'Итальянское Возрождение', 1),
        (disc_ids['Театр'], 'Античный театр', 'Греческая драматургия', 1),
    ]
    
    cursor.executemany('''
        INSERT INTO sections (discipline_id, name, description, order_num)
        VALUES (?, ?, ?, ?)
    ''', sections_data)
    
    # Получаем ID разделов
    cursor.execute('SELECT id, name FROM sections')
    section_ids = {name: id for id, name in cursor.fetchall()}
    
    # Добавляем темы
    topics_data = [
        (section_ids['Русская литература XIX века'], 'А.С. Пушкин', 'Жизнь и творчество', 1),
        (section_ids['Русская литература XIX века'], 'Ф.М. Достоевский', 'Романы и идеи', 2),
        (section_ids['Зарубежная литература'], 'У. Шекспир', 'Трагедии и комедии', 1),
        (section_ids['Античная философия'], 'Сократ', 'Сократический метод', 1),
        (section_ids['Классическая музыка'], 'В.А. Моцарт', 'Жизнь и творчество', 1),
        (section_ids['Ренессанс'], 'Леонардо да Винчи', 'Универсальный гений', 1),
    ]
    
    cursor.executemany('''
        INSERT INTO topics (section_id, name, description, order_num)
        VALUES (?, ?, ?, ?)
    ''', topics_data)
    
    # Получаем ID тем
    cursor.execute('SELECT id, name FROM topics')
    topic_ids = {name: id for id, name in cursor.fetchall()}
    
    # Добавляем вопросы
    questions_data = [
        (topic_ids['А.С. Пушкин'], 'Какое произведение А.С. Пушкина считается первым реалистическим романом в стихах?', 
         json.dumps(['"Руслан и Людмила"', '"Евгений Онегин"', '"Медный всадник"', '"Борис Годунов"']), 1, 1, 
         '"Евгений Онегин" — первый русский реалистический роман в стихах.'),
         
        (topic_ids['Ф.М. Достоевский'], 'Какой роман Достоевского стал одним из первых философских романов в русской литературе?',
         json.dumps(['"Бедные люди"', '"Преступление и наказание"', '"Идиот"', '"Братья Карамазовы"']), 1, 2,
         '"Преступление и наказание" (1866) исследует вопросы морали и ответственности.'),
        
        (topic_ids['У. Шекспир'], 'Сколько сонетов написал У. Шекспир?',
         json.dumps(['104', '154', '204', '254']), 1, 1,
         'Уильям Шекспир написал 154 сонета, опубликованных в 1609 году.'),
        
        (topic_ids['Сократ'], 'Как называется философский метод, разработанный Сократом?',
         json.dumps(['Диалектика', 'Софистика', 'Эпикурейство', 'Стоицизм']), 0, 2,
         'Сократический метод основан на постановке вопросов.'),
        
        (topic_ids['В.А. Моцарт'], 'Какое произведение Моцарта было написано в возрасте 6 лет?',
         json.dumps(['Первая симфония', 'Первая соната', 'Первая опера', 'Первый концерт']), 0, 2,
         'В 6 лет Моцарт написал свою первую симфонию (K.16).'),
        
        (topic_ids['Леонардо да Винчи'], 'В каком году была написана "Мона Лиза"?',
         json.dumps(['1495-1500', '1503-1519', '1520-1525', '1510-1515']), 1, 2,
         'Леонардо работал над "Моной Лизой" с 1503 по 1519 год.'),
    ]
    
    cursor.executemany('''
        INSERT INTO questions 
        (topic_id, question, options, correct_answer, difficulty, explanation)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', questions_data)
    
    # Добавляем достижения
    achievements = [
        ('Новичок', 'Правильно ответить на 10 вопросов', '🌱', 'correct_answers', 10, 50),
        ('Эрудит', 'Правильно ответить на 50 вопросов', '📚', 'correct_answers', 50, 150),
        ('Знаток', 'Правильно ответить на 100 вопросов', '🎯', 'correct_answers', 100, 300),
        ('Меценат', 'Набрать 500 очков', '🎨', 'total_score', 500, 400),
    ]
    
    cursor.executemany('''
        INSERT INTO achievements 
        (name, description, icon, condition_type, condition_value, xp_reward)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', achievements)
    
    conn.commit()
    conn.close()
    print("✅ База данных заполнена начальными данными!")

# ============================================
# ДОБАВЬТЕ ЭТУ ФУНКЦИЮ:
# ============================================

def get_db():
    """Получение соединения с базой данных"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
