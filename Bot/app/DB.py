import sqlite3


conn = sqlite3.connect('Users.db')
cursor = conn.cursor()

cursor.execute('''
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
conn.commit()


conn.commit()