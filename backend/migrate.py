import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "smartstudy.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column already exists
cursor.execute("PRAGMA table_info(study_sessions)")
columns = [col[1] for col in cursor.fetchall()]

if "duration" not in columns:
    cursor.execute("ALTER TABLE study_sessions ADD COLUMN duration INTEGER DEFAULT 0")
    conn.commit()
    print("✅ Column 'duration' added successfully.")
else:
    print("ℹ️ Column 'duration' already exists, nothing to do.")

conn.close()