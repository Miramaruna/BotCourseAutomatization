import aiosqlite

DB_NAME = 'Users.db'

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                course_1 BOOLEAN DEFAULT 0,
                course_2 BOOLEAN DEFAULT 0,
                course_3 BOOLEAN DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                chat_id INTEGER
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                name TEXT,
                price INTEGER,
                channel_id INTEGER,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        await db.commit()