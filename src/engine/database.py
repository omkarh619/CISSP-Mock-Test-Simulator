import sqlite3
import os
import uuid

class DatabaseManager:
    def __init__(self, db_path="data/cissp_simulator.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        # Create data directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        with self._get_connection() as conn:
            # Enable WAL mode
            conn.execute("PRAGMA journal_mode=WAL;")
            
            # Domains table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS domains (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    weight FLOAT NOT NULL
                )
            """)
            
            # Questions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id TEXT PRIMARY KEY,
                    domain_id INTEGER,
                    topic TEXT,
                    stem TEXT NOT NULL,
                    difficulty_b FLOAT NOT NULL, -- IRT 'b' parameter (-3.0 to 3.0)
                    discrimination_a FLOAT DEFAULT 1.0, -- IRT 'a' parameter
                    guessing_c FLOAT DEFAULT 0.25, -- IRT 'c' parameter
                    is_pretest BOOLEAN DEFAULT 0,
                    FOREIGN KEY(domain_id) REFERENCES domains(id)
                )
            """)
            
            # Options table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS options (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id TEXT,
                    text TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    rationale TEXT,
                    FOREIGN KEY(question_id) REFERENCES questions(id)
                )
            """)
            
            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    current_theta FLOAT DEFAULT 0.0,
                    standard_error FLOAT DEFAULT 1.0,
                    is_active INTEGER DEFAULT 1,
                    start_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Responses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    question_id TEXT,
                    selected_option_id INTEGER,
                    is_correct INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(id),
                    FOREIGN KEY(question_id) REFERENCES questions(id),
                    FOREIGN KEY(selected_option_id) REFERENCES options(id)
                )
            """)
            conn.commit()

    def seed_domains(self):
        domains = [
            (1, "Security and Risk Management", 0.16),
            (2, "Asset Security", 0.10),
            (3, "Security Architecture and Engineering", 0.13),
            (4, "Communication and Network Security", 0.13),
            (5, "Identity and Access Management (IAM)", 0.13),
            (6, "Security Assessment and Testing", 0.12),
            (7, "Security Operations", 0.13),
            (8, "Software Development Security", 0.10),
        ]
        with self._get_connection() as conn:
            conn.executemany("INSERT OR IGNORE INTO domains (id, title, weight) VALUES (?, ?, ?)", domains)
            conn.commit()

    def get_domains(self):
        with self._get_connection() as conn:
            return conn.execute("SELECT * FROM domains").fetchall()

    def get_active_session(self):
        with self._get_connection() as conn:
            return conn.execute("SELECT * FROM sessions WHERE is_active = 1 LIMIT 1").fetchone()

    def create_session(self):
        # Deactivate previous sessions
        with self._get_connection() as conn:
            conn.execute("UPDATE sessions SET is_active = 0")
            session_id = str(uuid.uuid4())
            conn.execute("INSERT INTO sessions (id) VALUES (?)", (session_id,))
            conn.commit()
            return session_id

    def save_response(self, session_id, question_id, option_id, is_correct, new_theta, new_se):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO responses (session_id, question_id, selected_option_id, is_correct)
                VALUES (?, ?, ?, ?)
            """, (session_id, question_id, option_id, is_correct))
            
            conn.execute("""
                UPDATE sessions 
                SET current_theta = ?, standard_error = ?
                WHERE id = ?
            """, (new_theta, new_se, session_id))
            conn.commit()

    def get_unanswered_questions(self, session_id):
        with self._get_connection() as conn:
            return conn.execute("""
                SELECT * FROM questions 
                WHERE id NOT IN (SELECT question_id FROM responses WHERE session_id = ?)
            """, (session_id,)).fetchall()

    def get_question_options(self, question_id):
        with self._get_connection() as conn:
            return conn.execute("SELECT * FROM options WHERE question_id = ?", (question_id,)).fetchall()

    def get_session_responses_count(self, session_id):
        with self._get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM responses WHERE session_id = ?", (session_id,)).fetchone()[0]

    def get_session_details(self, session_id):
        with self._get_connection() as conn:
            return conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
