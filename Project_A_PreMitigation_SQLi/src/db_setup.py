import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'vulnerable.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, secret TEXT)''')
    c.execute("DELETE FROM users")
    c.executemany('INSERT INTO users (username,password,secret) VALUES (?, ?, ?)', [
        ('alice', 'password1', 'secret_alice'),
        ('bob', 'password2', 'secret_bob'),
        ('carol', 'password3', 'secret_carol')
    ])
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('DB initialized at', DB_PATH)
