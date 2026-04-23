from src.engine.database import DatabaseManager
import uuid
import random

def seed_database(db_path="data/cissp_simulator.db"):
    db = DatabaseManager(db_path)
    conn = db._get_connection()
    cursor = conn.cursor()

    # Domains
    domains = [
        (1, "Security and Risk Management", 0.15),
        (2, "Asset Security", 0.10),
        (3, "Security Architecture and Engineering", 0.13),
        (4, "Communication and Network Security", 0.13),
        (5, "Identity and Access Management (IAM)", 0.13),
        (6, "Security Assessment and Testing", 0.12),
        (7, "Security Operations", 0.13),
        (8, "Software Development Security", 0.11),
    ]
    cursor.executemany("INSERT OR IGNORE INTO domains (id, title, weight) VALUES (?, ?, ?)", domains)

    # Questions and Options
    # Generating 200 questions (enough for a full CAT session)
    question_count = 200
    for i in range(question_count):
        q_id = str(uuid.uuid4())
        domain_id = random.randint(1, 8)
        difficulty = round(random.uniform(-2.5, 2.5), 2)
        is_pretest = 1 if i < 25 else 0
        
        stem = f"This is a sample question for Domain {domain_id} with difficulty {difficulty}. What is the correct answer?"
        topic = f"Topic {random.randint(1, 100)}"
        
        cursor.execute("""
            INSERT INTO questions (id, domain_id, topic, stem, difficulty_b, discrimination_a, guessing_c, is_pretest)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (q_id, domain_id, topic, stem, difficulty, 1.2, 0.25, is_pretest))
        
        # Options
        correct_idx = random.randint(0, 3)
        for j in range(4):
            is_correct = 1 if j == correct_idx else 0
            option_text = f"Option {j+1} for question {i}"
            rationale = f"Rationale for Option {j+1}. This is {'correct' if is_correct else 'incorrect'} because..."
            
            cursor.execute("""
                INSERT INTO options (question_id, text, is_correct, rationale)
                VALUES (?, ?, ?, ?)
            """, (q_id, option_text, is_correct, rationale))

    conn.commit()
    conn.close()
    print("Database seeded successfully with 200 questions.")

if __name__ == "__main__":
    seed_database()
