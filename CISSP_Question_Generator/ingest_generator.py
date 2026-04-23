import json
import sqlite3
import os

DB_PATH = os.path.join("data", "cissp_simulator.db")
BATCH_FILE = os.path.join("CISSP_Question_Generator", "batch_questions.json")

def ingest_batch():
    if not os.path.exists(BATCH_FILE):
        print(f"Error: {BATCH_FILE} not found.")
        return

    try:
        with open(BATCH_FILE, "r") as f:
            data = json.load(f)
        
        questions = data.get("questions", [])
        if not questions:
            print("No questions found in batch file.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        count = 0
        for q in questions:
            # Insert question
            cursor.execute("""
                INSERT OR IGNORE INTO questions (id, domain_id, topic, stem, difficulty_b, discrimination_a, guessing_c, is_pretest)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q['id'], q['domain_id'], q['topic'], q['stem'], 
                q['difficulty_b'], q.get('discrimination_a', 1.0), 
                q.get('guessing_c', 0.25), q.get('is_pretest', 0)
            ))

            if cursor.rowcount > 0:
                # Insert options
                for opt in q['options']:
                    cursor.execute("""
                        INSERT INTO options (question_id, text, is_correct, rationale)
                        VALUES (?, ?, ?, ?)
                    """, (q['id'], opt['text'], opt['is_correct'], opt['rationale']))
                count += 1
        
        conn.commit()
        conn.close()
        
        # Cleanup
        os.remove(BATCH_FILE)
        print(f"Successfully generated and ingested {count} questions into the database.")

    except Exception as e:
        print(f"Error during ingestion: {e}")

if __name__ == "__main__":
    ingest_batch()
