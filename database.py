# database.py
import sqlite3
import os
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path=None):
        # default DB path
        if db_path is None:
            db_path = os.path.join("data", "career_roadmap.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        # attempt to auto-load sample careers from data/sample_career_map.csv if table empty
        self._maybe_load_sample_data()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            career_interests TEXT,
            current_skills TEXT,
            available_hours TEXT,
            experience_level TEXT,
            additional_info TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS career_paths (
            career_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            required_skills TEXT,
            description TEXT,
            duration_weeks INTEGER
        );

        CREATE TABLE IF NOT EXISTS roadmaps (
            roadmap_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            career_id INTEGER,
            steps TEXT,
            duration INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(career_id) REFERENCES career_paths(career_id)
        );
        """)
        self.conn.commit()

    def _maybe_load_sample_data(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM career_paths")
        count = cur.fetchone()["c"]
        if count == 0:
            sample_csv = os.path.join("data", "sample_career_map.csv")
            if os.path.exists(sample_csv):
                try:
                    df = pd.read_csv(sample_csv)
                    for _, row in df.iterrows():
                        title = row.get("title") or row.get("career") or row.get("job_title") or "Unknown"
                        skills = row.get("skill_list") or row.get("skills") or ""
                        desc = row.get("description") or ""
                        months = row.get("avg_duration_months") or row.get("duration_months") or None
                        try:
                            duration_weeks = int(float(months) * 4) if months else None
                        except:
                            duration_weeks = None
                        cur.execute("""
                        INSERT INTO career_paths (title, required_skills, description, duration_weeks)
                        VALUES (?, ?, ?, ?)
                        """, (title, skills, desc, duration_weeks))
                    self.conn.commit()
                except Exception:
                    # ignore failures loading sample data
                    pass

    def insert_user(self, name, email, career_interests, current_skills,
                    available_hours, experience_level, additional_info=None):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO users (name, email, career_interests, current_skills, available_hours, experience_level, additional_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email, career_interests, current_skills, available_hours, experience_level, additional_info))
        self.conn.commit()
        return cur.lastrowid

    def get_database_stats(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as users FROM users")
        users = cur.fetchone()["users"]
        cur.execute("SELECT COUNT(*) as c FROM career_paths")
        career_paths = cur.fetchone()["c"]
        cur.execute("SELECT SUM(LENGTH(required_skills) - LENGTH(REPLACE(required_skills, ';', '')) + 1) as skills_est FROM career_paths WHERE required_skills IS NOT NULL")
        val = cur.fetchone()["skills_est"]
        skills = int(val) if val and val > 0 else 0
        return {"users": users, "career_paths": career_paths, "skills": skills}

    def get_sample_career_paths(self, limit=5):
        cur = self.conn.cursor()
        cur.execute("SELECT career_id, title, required_skills, description, duration_weeks FROM career_paths LIMIT ?", (limit,))
        rows = cur.fetchall()
        result = []
        for r in rows:
            result.append({
                "career_id": r["career_id"],
                "title": r["title"],
                "required_skills": r["required_skills"],
                "description": r["description"],
                "duration_weeks": r["duration_weeks"] or 0
            })
        return result

    def close(self):
        try:
            self.conn.close()
        except:
            pass
