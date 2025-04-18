


import sqlite3

conn = sqlite3.connect("group_invite_bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    invited_by INTEGER,
    invite_count INTEGER DEFAULT 0,
    can_post INTEGER DEFAULT 0
)
""")

conn.commit()

# Function to add user information to the database
def add_user(user_id, invited_by=None):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, invited_by) VALUES (?, ?)", (user_id, invited_by))
    if invited_by:
        cursor.execute("UPDATE users SET invite_count = invite_count + 1 WHERE user_id = ?", (invited_by,))
        cursor.execute("SELECT invite_count FROM users WHERE user_id = ?", (invited_by,))
        count = cursor.fetchone()[0]
        if count >= 10:
            cursor.execute("UPDATE users SET can_post = 1 WHERE user_id = ?", (invited_by,))
    conn.commit()

# Function to check if a user can post based on invite count
def can_user_post(user_id):
    cursor.execute("SELECT can_post FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row and row[0] == 1

# Function to get the invite count of a user
def get_invite_count(user_id):
    cursor.execute("SELECT invite_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

