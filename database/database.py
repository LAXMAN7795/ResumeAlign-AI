import sqlite3
import os
from pathlib import Path

DB_PATH = Path("database/resumealign.db")

def get_connection():
    """Create and return a database connection with foreign key support enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initialize database tables according to schema definition."""
    conn = get_connection()
    cursor = conn.cursor()

    # Candidate Profile Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidate (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        linkedin TEXT,
        github TEXT,
        portfolio TEXT,
        summary TEXT
    );
    """)

    # Skills Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        FOREIGN KEY (candidate_id) REFERENCES candidate (id) ON DELETE CASCADE
    );
    """)

    # Experience Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS experience (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        duration TEXT NOT NULL,
        description TEXT NOT NULL,
        FOREIGN KEY (candidate_id) REFERENCES candidate (id) ON DELETE CASCADE
    );
    """)

    # Projects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        technologies TEXT NOT NULL,
        FOREIGN KEY (candidate_id) REFERENCES candidate (id) ON DELETE CASCADE
    );
    """)

    # Job Descriptions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        raw_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Generated Resumes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        jd_id INTEGER NOT NULL,
        generated_markdown TEXT NOT NULL,
        ats_score INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES candidate (id) ON DELETE CASCADE,
        FOREIGN KEY (jd_id) REFERENCES job_descriptions (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")