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

def seed_database():
    """Заполнение базы данных начальными данными"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
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
        INSERT OR IGNORE INTO disciplines (name, icon, description, color)
        VALUES (?, ?, ?, ?)
    ''', disciplines)
    
    # Получаем ID дисциплин
    cursor.execute('SELECT id, name FROM disciplines')
    disc_ids = {name: id for id, name in cursor.fetchall()}
    
    # Добавляем разделы и темы
    sections_data = [
        # Литература
        (disc_ids['Литература'], 'Русская литература XIX века', 'Золотой век русской литературы', 1),
        (disc_ids['Литература'], 'Зарубежная литература', 'Мировая классическая литература', 2),
        (disc_ids['Литература'], 'Поэзия Серебряного века', 'Русская поэзия начала XX века', 3),
        
        # История
        (disc_ids['История'], 'Древний мир', 'Цивилизации древности', 1),
        (disc_ids['История'], 'Средневековье', 'Европа и Русь в средние века', 2),
        (disc_ids['История'], 'Новое время', 'XVII-XIX века', 3),
        
        # Философия
        (disc_ids['Философия'], 'Античная философия', 'Философия Древней Греции и Рима', 1),
        (disc_ids['Философия'], 'Русская философия', 'Философская мысль в России', 2),
        
        # Психология
        (disc_ids['Психология'], 'Основы психологии', 'Базовые психологические концепции', 1),
        (disc_ids['Психология'], 'Психология личности', 'Теории личности и развития', 2),
        
        # Социология
        (disc_ids['Социология'], 'Социологические теории', 'Основные социологические концепции', 1),
        
        # Музыка
        (disc_ids['Музыка'], 'Классическая музыка', 'Музыкальные произведения классического периода', 1),
        (disc_ids['Музыка'], 'Джаз и блюз', 'Американская музыкальная традиция', 2),
        
        # Живопись
        (disc_ids['Живопись'], 'Ренессанс', 'Итальянское Возрождение', 1),
        (disc_ids['Живопись'], 'Импрессионизм', 'Французская живопись XIX века', 2),
        
        # Скульптура
        (disc_ids['Скульптура'], 'Античная скульптура', 'Греческая и римская скульптура', 1),
        
        # Театр
        (disc_ids['Театр'], 'Античный театр', 'Греческая драматургия', 1),
        (disc_ids['Театр'], 'Русский театр', 'Театральное искусство в России', 2)
    ]
    
    for disc_id, name, desc, order_num in sections_data:
        cursor.execute('''
            INSERT OR IGNORE INTO sections (discipline_id, name, description, order_num)
            VALUES (?, ?, ?, ?)
        ''', (disc_id, name, desc, order_num))
    
    # Получаем ID разделов
    cursor.execute('SELECT id, name FROM sections')
    section_ids = {name: id for id, name in cursor.fetchall()}
    
    # Добавляем темы
    topics_data = [
        # Русская литература XIX века
        (section_ids['Русская литература XIX века'], 'А.С. Пушкин', 'Жизнь и творчество', 1),
        (section_ids['Русская литература XIX века'], 'Ф.М. Достоевский', 'Романы и идеи', 2),
        (section_ids['Русская литература XIX века'], 'Л.Н. Толстой', 'Эпопеи и романы', 3),
        (section_ids['Русская литература XIX века'], 'А.П. Чехов', 'Рассказы и пьесы', 4),
        
        # Зарубежная литература
        (section_ids['Зарубежная литература'], 'У. Шекспир', 'Трагедии и комедии', 1),
        (section_ids['Зарубежная литература'], 'Ч. Диккенс', 'Викторианский роман', 2),
        
        # Античная философия
        (section_ids['Античная философия'], 'Сократ', 'Сократический метод', 1),
        (section_ids['Античная философия'], 'Платон', 'Теория идей', 2),
        (section_ids['Античная философия'], 'Аристотель', 'Логика и этика', 3),
        
        # Психология
        (section_ids['Основы психологии'], 'Введение в психологию', 'Основные понятия', 1),
        (section_ids['Основы психологии'], 'Психологические школы', 'Основные направления', 2),
        
        # Классическая музыка
        (section_ids['Классическая музыка'], 'В.А. Моцарт', 'Жизнь и творчество', 1),
        (section_ids['Классическая музыка'], 'Л. Бетховен', 'Симфонии и сонаты', 2),
        
        # Живопись - Ренессанс
        (section_ids['Ренессанс'], 'Леонардо да Винчи', 'Универсальный гений', 1),
        (section_ids['Ренессанс'], 'Микеланджело', 'Скульптура и живопись', 2),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO topics (section_id, name, description, order_num)
        VALUES (?, ?, ?, ?)
    ''', topics_data)
    
    # Получаем ID тем
    cursor.execute('SELECT id, name FROM topics')
    topic_ids = {name: id for id, name in cursor.fetchall()}
    
    # Добавляем вопросы
    questions_data = [
        # Пушкин
        (topic_ids['А.С. Пушкин'], 'Какое произведение А.С. Пушкина считается первым реалистическим романом в стихах?', 
         json.dumps(['"Руслан и Людмила"', '"Евгений Онегин"', '"Медный всадник"', '"Борис Годунов"']), 1, 1, 
         '"Евгений Онегин" — первый русский реалистический роман в стихах, начат в 1823 году.'),
         
        (topic_ids['А.С. Пушкин'], 'В каком году родился А.С. Пушкин?', 
         json.dumps(['1795', '1799', '1801', '1805']), 1, 1, 
         'Александр Сергеевич Пушкин родился 6 июня 1799 года в Москве.'),
        
        # Достоевский
        (topic_ids['Ф.М. Достоевский'], 'Какой роман Достоевского стал одним из первых философских романов в русской литературе?',
         json.dumps(['"Бедные люди"', '"Преступление и наказание"', '"Идиот"', '"Братья Карамазовы"']), 1, 2,
         '"Преступление и наказание" (1866) исследует вопросы морали, свободы и ответственности.'),
        
        # Шекспир
        (topic_ids['У. Шекспир'], 'Сколько сонетов написал У. Шекспир?',
         json.dumps(['104', '154', '204', '254']), 1, 1,
         'Уильям Шекспир написал 154 сонета, опубликованных в 1609 году.'),
        
        # Сократ
        (topic_ids['Сократ'], 'Как называется философский метод, разработанный Сократом?',
         json.dumps(['Диалектика', 'Софистика', 'Эпикурейство', 'Стоицизм']), 0, 2,
         'Сократический метод — это форма диалога, основанная на постановке вопросов.'),
        
        # Моцарт
        (topic_ids['В.А. Моцарт'], 'Какое произведение Моцарта было написано в возрасте 6 лет?',
         json.dumps(['Первая симфония', 'Первая соната', 'Первая опера', 'Первый концерт']), 0, 2,
         'В 6 лет Моцарт написал свою первую симфонию (K.16).'),
        
        # Леонардо да Винчи
        (topic_ids['Леонардо да Винчи'], 'В каком году была написана "Мона Лиза"?',
         json.dumps(['1495-1500', '1503-1519', '1520-1525', '1510-1515']), 1, 2,
         'Леонардо работал над "Моной Лизой" с 1503 по 1519 год.'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO questions 
        (topic_id, question, options, correct_answer, difficulty, explanation)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', questions_data)
    
    # Добавляем обучающие материалы
    learning_materials = [
        (topic_ids['А.С. Пушкин'], 'Биография Пушкина', 
         'Александр Сергеевич Пушкин (1799-1837) — великий русский поэт, основоположник современного русского литературного языка. Родился в Москве в дворянской семье. В 1820 году опубликовал поэму "Руслан и Людмила". В 1837 году погиб на дуэли. Его творчество охватывает все литературные жанры: поэзию, прозу, драматургию.', 
         'text', None, None, 1),
         
        (topic_ids['Сократ'], 'Сократический метод',
         'Сократический метод (майевтика) — это метод ведения диалога, при котором собеседник с помощью наводящих вопросов приходит к истине. Метод включает иронию (осознание незнания) и майевтику (рождение истины). Сократ считал, что истина уже заложена в каждом человеке, и задача философа — помочь её "родить".',
         'text', None, None, 1),
         
        (topic_ids['Леонардо да Винчи'], 'Техника сфумато',
         'Сфумато (от итал. sfumato — "дымчатый, расплывчатый") — техника живописи, разработанная Леонардо да Винчи. Она создаёт эффект мягких переходов между цветами и тонами, делая изображение более реалистичным. Леонардо писал тонкими слоями прозрачной краски (лессировками), создавая туманную атмосферу. Яркий пример — "Мона Лиза".',
         'text', None, None, 2),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO learning_materials 
        (topic_id, title, content, type, image_url, video_url, order_num)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', learning_materials)
    
    # Добавляем достижения
    achievements = [
        ('Новичок', 'Правильно ответить на 10 вопросов', '🌱', 'correct_answers', 10, 50),
        ('Эрудит', 'Правильно ответить на 50 вопросов', '📚', 'correct_answers', 50, 150),
        ('Знаток', 'Правильно ответить на 100 вопросов', '🎯', 'correct_answers', 100, 300),
        ('Профессор', 'Завершить 5 тем полностью', '👨‍🏫', 'topics_completed', 5, 500),
        ('Полиглот', 'Правильно ответить в 5 разных дисциплинах', '🌍', 'disciplines_completed', 5, 200),
        ('Меценат', 'Набрать 500 очков', '🎨', 'total_score', 500, 400),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO achievements 
        (name, description, icon, condition_type, condition_value, xp_reward)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', achievements)
    
    conn.commit()
    conn.close()
    print("✅ База данных успешно заполнена!")

# Вызов при импорте
if __name__ == "__main__":
    init_db()
    seed_database()
