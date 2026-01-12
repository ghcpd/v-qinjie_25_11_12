"""
Database initialization script for Project B (Patched)
"""

import os
import sqlite3
import sys

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'patched.db')


def init_db():
    """Initialize the patched database with sample data."""
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Remove existing database
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Insert sample users
    sample_users = [
        ('admin', 'admin123', 'Administrator', 'admin@example.com', 'admin'),
        ('john', 'password123', 'John Doe', 'john@example.com', 'user'),
        ('jane', 'secure456', 'Jane Smith', 'jane@example.com', 'user'),
        ('bob', 'pass789', 'Bob Johnson', 'bob@example.com', 'moderator'),
        ('alice', 'alice2024', 'Alice Williams', 'alice@example.com', 'user'),
    ]
    
    cursor.executemany(
        'INSERT INTO users (username, password, name, email, role) VALUES (?, ?, ?, ?, ?)',
        sample_users
    )
    
    # Create audit log table
    cursor.execute('''
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            query TEXT NOT NULL,
            result TEXT,
            security_status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized at: {DATABASE_PATH}")
    print(f"Sample users: {len(sample_users)}")


if __name__ == '__main__':
    init_db()
