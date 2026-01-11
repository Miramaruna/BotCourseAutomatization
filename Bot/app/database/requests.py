import aiosqlite
from app.database.core import DB_NAME
from config import ADMIN_IDS

async def chek_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def add_user(user_id, username, chat_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username, chat_id) VALUES (?, ?, ?)',
            (user_id, username, chat_id)
        )
        await db.commit()

async def update_user_name(user_id, full_name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET full_name = ? WHERE user_id = ?', (full_name, user_id))
        await db.commit()

async def purchase_course(user_id, course_column, amount):
    """
    course_column: 'course_1', 'course_2' и т.д.
    """
    async with aiosqlite.connect(DB_NAME) as db:
        query = f'UPDATE users SET {course_column} = 1, total_spent = total_spent + ? WHERE user_id = ?'
        await db.execute(query, (amount, user_id))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT full_name, user_id, course_1, course_2, course_3, total_spent FROM users') as cursor:
            return await cursor.fetchall()

async def search_users(query):
    async with aiosqlite.connect(DB_NAME) as db:
        search_pattern = f'%{query}%'
        async with db.execute('''
            SELECT user_id, full_name, username FROM users 
            WHERE full_name LIKE ? OR username LIKE ?
        ''', (search_pattern, search_pattern)) as cursor:
            return await cursor.fetchall()
        
# app/database/requests.py
from config import COURSES_CONFIG

async def sync_courses_from_config():
    async with aiosqlite.connect(DB_NAME) as db:
        for c_id, data in COURSES_CONFIG.items():
            # Проверяем, существует ли курс, чтобы не затереть измененные админом данные
            async with db.execute('SELECT 1 FROM courses WHERE course_id = ?', (c_id,)) as cur:
                if not await cur.fetchone():
                    price = int(''.join(filter(str.isdigit, str(data['price']))))
                    await db.execute(
                        'INSERT INTO courses (course_id, name, price, channel_id) VALUES (?, ?, ?, ?)',
                        (c_id, data['name'], price, data.get('channel_id'))
                    )
        await db.commit()

async def get_active_courses():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM courses WHERE is_active = 1') as cursor:
            return await cursor.fetchall()

async def get_all_courses_admin():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM courses') as cursor:
            return await cursor.fetchall()

async def update_course_param(course_id, column, value):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f'UPDATE courses SET {column} = ? WHERE course_id = ?', (value, course_id))
        await db.commit()
        
async def update_course_param(course_id, column, value):
    """
    Обновляет любой параметр курса (name, price, is_active)
    """
    async with aiosqlite.connect(DB_NAME) as db:
        # ВАЖНО: column нельзя передавать как параметр в execute из-за защиты от SQL-инъекций,
        # но так как мы вызываем эту функцию только из своего кода с жестко заданными строками, это допустимо.
        query = f'UPDATE courses SET {column} = ? WHERE course_id = ?'
        await db.execute(query, (value, course_id))
        await db.commit()

async def get_course_by_id(course_id):
    """Получает данные одного курса"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM courses WHERE course_id = ?', (course_id,)) as cursor:
            return await cursor.fetchone()  
        
async def get_all_users_without_admin():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT full_name, user_id, course_1, course_2, course_3, total_spent FROM users WHERE user_id NOT IN ({})'.format(','.join('?'*len(ADMIN_IDS))), ADMIN_IDS) as cursor:
            return await cursor.fetchall()