import sqlite3
from datetime import datetime

DB_NAME = "files.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filetype TEXT,
        cloudinary_url TEXT,
        size_mb REAL,
        uploaded_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_file(
    filename,
    filetype,
    cloudinary_url,
    size_mb
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO uploaded_files
    (
        filename,
        filetype,
        cloudinary_url,
        size_mb,
        uploaded_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        filename,
        filetype,
        cloudinary_url,
        size_mb,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_files():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM uploaded_files
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def delete_file(file_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM uploaded_files
    WHERE id = ?
    """, (file_id,))

    conn.commit()
    conn.close()