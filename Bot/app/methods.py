from app.DB import conn
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class Registration(StatesGroup):
    waiting_for_name = State()

cursor = conn.cursor()

async def chek_user(id):
    cursor.execute('''
        SELECT * FROM users WHERE user_id = ?
    ''', (id,))
    return cursor.fetchone()

async def add_user(id, username, chat_id):
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, chat_id) VALUES (?, ?, ?)', (id, username, chat_id))
    conn.commit()

async def update_user_name(id, full_name):
    cursor.execute('UPDATE users SET full_name = ? WHERE user_id = ?', (full_name, id))
    conn.commit()

async def purchase_course(id, course, amount):
    # Обновляем статус курса и прибавляем цену к общему доходу от пользователя
    cursor.execute(f'''
        UPDATE users 
        SET {course} = 1, total_spent = total_spent + ? 
        WHERE user_id = ?
    ''', (amount, id))
    conn.commit()

async def get_all_users():
    # Мы добавили total_spent в запрос
    cursor.execute('SELECT full_name, user_id, course_1, course_2, course_3, total_spent FROM users')
    return cursor.fetchall()

async def search_users(query):
    # Поиск по имени или username
    cursor.execute('''
        SELECT user_id, full_name, username FROM users 
        WHERE full_name LIKE ? OR username LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    return cursor.fetchall()

async def chek_user_funk(message, user_id, state: FSMContext):
    user_data = await chek_user(user_id)
    if not user_data:
        await add_user(user_id, message.from_user.username, message.chat.id)
        user_data = await chek_user(user_id)
        await message.answer("👋 Здравствуйте! Пожалуйста, введите вашу **Фамилию и Имя**:")
        await state.set_state(Registration.waiting_for_name)