# database.py
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "career_roadmap.db"):
        """Initialize database manager with database path."""
        self.db_path = db_path
        # Ensure folder exists if user passed a folder path
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        os.makedirs(db_dir, exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize database with all required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    career_interests TEXT NOT NULL,
                    current_skills TEXT NOT NULL,
                    available_hours TEXT NOT NULL,
                    experience_level TEXT NOT NULL,
                    additional_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Career Paths table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS career_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    required_skills TEXT NOT NULL,
                    prerequisites TEXT,
                    duration_weeks INTEGER NOT NULL,
                    difficulty_level TEXT NOT NULL,
                    salary_range TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    learning_resources TEXT,
                    estimated_hours INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Roadmaps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roadmaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    career_path_id INTEGER NOT NULL,
                    recommended_skills TEXT NOT NULL,
                    learning_timeline TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (career_path_id) REFERENCES career_paths (id)
                )
            """)
            
            # Create Skills Progress table (for tracking user progress)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_skill_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    skill_id INTEGER NOT NULL,
                    proficiency_level TEXT DEFAULT 'beginner',
                    progress_percentage INTEGER DEFAULT 0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (skill_id) REFERENCES skills (id),
                    UNIQUE(user_id, skill_id)
                )
            """)
            
            conn.commit()
            # Insert sample data if tables are empty
            self._insert_sample_data()
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _insert_sample_data(self):
        """Insert sample career paths and skills data."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM career_paths")
            career_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM skills")
            skill_count = cursor.fetchone()[0]
            
            if career_count == 0:
                # Insert sample career paths
                sample_careers = [
                    (
                        "Data Scientist",
                        "Analyze complex data to help companies make better decisions. Work with statistical models, machine learning algorithms, and data visualization tools.",
                        "Python, R, SQL, Machine Learning, Statistics, Data Visualization, Pandas, NumPy",
                        "Basic programming knowledge, Mathematics/Statistics background",
                        24,
                        "Intermediate to Advanced",
                        "$70,000 - $150,000+"
                    ),
                    (
                        "Full Stack Web Developer",
                        "Build complete web applications including both frontend user interfaces and backend server logic.",
                        "HTML, CSS, JavaScript, React, Node.js, Express, MongoDB, Git",
                        "Basic computer literacy, Problem-solving skills",
                        20,
                        "Beginner to Intermediate",
                        "$50,000 - $120,000"
                    ),
                    (
                        "Mobile App Developer",
                        "Create mobile applications for iOS and Android platforms using native or cross-platform technologies.",
                        "Swift, Kotlin, React Native, Flutter, UI/UX Design, API Integration",
                        "Basic programming concepts, Understanding of mobile platforms",
                        18,
                        "Intermediate",
                        "$60,000 - $130,000"
                    ),
                    (
                        "Machine Learning Engineer",
                        "Design and implement machine learning systems and algorithms to solve real-world problems.",
                        "Python, TensorFlow, PyTorch, scikit-learn, Deep Learning, MLOps, Docker",
                        "Programming experience, Mathematics/Statistics, Data Science basics",
                        28,
                        "Advanced",
                        "$80,000 - $180,000+"
                    ),
                    (
                        "Cybersecurity Specialist",
                        "Protect organizations from cyber threats by implementing security measures and monitoring systems.",
                        "Network Security, Ethical Hacking, Risk Assessment, Security Tools, Linux, Python",
                        "Basic networking knowledge, Understanding of computer systems",
                        22,
                        "Intermediate to Advanced",
                        "$65,000 - $140,000"
                    )
                ]
                
                cursor.executemany("""
                    INSERT INTO career_paths 
                    (title, description, required_skills, prerequisites, duration_weeks, difficulty_level, salary_range)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, sample_careers)
            
            if skill_count == 0:
                # Insert sample skills
                sample_skills = [
                    ("Python", "Programming", "High-level programming language", "Online courses, Documentation", 40),
                    ("JavaScript", "Programming", "Web programming language", "Online tutorials, Practice projects", 35),
                    ("SQL", "Database", "Database query language", "Online courses, Practice databases", 25),
                    ("Machine Learning", "Data Science", "AI algorithms and models", "Courses, Books, Kaggle competitions", 60),
                    ("React", "Frontend", "JavaScript library for building UIs", "Official docs, Tutorial projects", 30),
                    ("Node.js", "Backend", "JavaScript runtime for server-side development", "Documentation, Practice projects", 25),
                    ("HTML/CSS", "Frontend", "Web markup and styling languages", "Online tutorials, Practice", 20),
                    ("Git", "Tools", "Version control system", "Online tutorials, Practice", 15),
                    ("Docker", "DevOps", "Containerization platform", "Documentation, Hands-on practice", 20),
                    ("Statistics", "Mathematics", "Statistical analysis and methods", "Books, Online courses", 45)
                ]
                
                cursor.executemany("""
                    INSERT INTO skills 
                    (name, category, description, learning_resources, estimated_hours)
                    VALUES (?, ?, ?, ?, ?)
                """, sample_skills)
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"Error inserting sample data: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def insert_user(self, name: str, email: str, career_interests: str, 
                   current_skills: str, available_hours: str, experience_level: str,
                   additional_info: Optional[str] = None) -> int:
        """Insert a new user into the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users 
                (name, email, career_interests, current_skills, available_hours, 
                 experience_level, additional_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, career_interests, current_skills, available_hours, 
                  experience_level, additional_info))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
            
        except sqlite3.IntegrityError:
            raise Exception("Email address already exists in the system")
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get counts from each table
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM career_paths")
            career_paths_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM skills")
            skills_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM roadmaps")
            roadmaps_count = cursor.fetchone()[0]
            
            return {
                'users': users_count,
                'career_paths': career_paths_count,
                'skills': skills_count,
                'roadmaps': roadmaps_count
            }
        finally:
            conn.close()
    
    def get_sample_career_paths(self, limit: int = 3) -> List[Dict]:
        """Get sample career paths for display."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, title, description, required_skills, duration_weeks 
                FROM career_paths 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_all_skills(self) -> List[Dict]:
        """Get all skills from database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM skills ORDER BY category, name")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def get_career_paths(self) -> List[Dict]:
        """Get all career paths from database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM career_paths ORDER BY title")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
