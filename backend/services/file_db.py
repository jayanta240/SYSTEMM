import sqlite3
from datetime import datetime

DB_NAME = "files.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --------------------------------
    # EXISTING FILES TABLE
    # --------------------------------
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

    # --------------------------------
    # ISSUE IMAGES TABLE
    # --------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issue_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_url TEXT,
        public_id TEXT,
        problem TEXT,
        solution TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# ====================================
# FILE MANAGEMENT
# ====================================

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
    SELECT *
    FROM uploaded_files
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


# ====================================
# ISSUE IMAGE KNOWLEDGE BASE
# ====================================

def add_issue(
    image_url,
    public_id,
    problem,
    solution
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO issue_images
    (
        image_url,
        public_id,
        problem,
        solution,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        image_url,
        public_id,
        problem,
        solution,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_issues():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM issue_images
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_issue(issue_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM issue_images
    WHERE id = ?
    """, (issue_id,))

    conn.commit()
    conn.close()