import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'app.db')

os.makedirs(DB_DIR, exist_ok=True)

if os.path.exists(DB_PATH):
    print('Overwriting existing DB at', DB_PATH)
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL
)
''')

# Insert sample users
import os
import random
import string

size = int(os.environ.get('DB_SIZE', '4'))
def random_name(i):
    return 'user' + str(i)

users = []
for i in range(size):
    if i == 0:
        users.append(('alice', 'alice@example.com'))
    elif i == 1:
        users.append(('bob', 'bob@example.com'))
    elif i == 2:
        users.append(('charlie', 'charlie@example.com'))
    elif i == 3:
        users.append(('admin', 'admin@example.com'))
    else:
        users.append((random_name(i), f'user{i}@example.com'))

cur.executemany('INSERT INTO users (username, email) VALUES (?, ?)', users)
conn.commit()
conn.close()
print('DB initialized at', DB_PATH)
