"""
Database initialization script for Project A
Creates SQLite database with sample user data
"""

import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')


def init_database():
    """Initialize the database with sample data"""
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample users
    users = [
        ('admin', 'admin@example.com', 'admin123', 'admin'),
        ('alice', 'alice@example.com', 'password123', 'user'),
        ('bob', 'bob@example.com', 'bobpass', 'user'),
        ('charlie', 'charlie@example.com', 'charlie123', 'moderator'),
        ('diana', 'diana@example.com', 'diana456', 'user'),
        ('eve', 'eve@example.com', 'eve789', 'user'),
    ]
    
    for username, email, password, role in users:
        # Simple password hash (for demo purposes only)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        cursor.execute(
            'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
            (username, email, password_hash, role)
        )
    
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}")
    print(f"Created {len(users)} sample users")


if __name__ == '__main__':
    init_database()

