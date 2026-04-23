import sqlite3
import json
import os
import uuid

def main():
    json_path = "data/temp_batch.json"
    db_path = "data/cissp_simulator.db"
    
    if not os.path.exists(json_path):
        print(f"Error: Temporary file {json_path} not found.")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"Ingesting {len(data)} questions...")
        
        for q in data:
            q_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO questions (id, domain_id, topic, stem, difficulty_b, is_pretest) VALUES (?, ?, ?, ?, ?, ?)",
                           (q_id, q['domain_id'], q['topic'], q['stem'], q['difficulty_b'], q.get('is_pretest', 0)))
            for opt in q['options']:
                cursor.execute("INSERT INTO options (question_id, text, is_correct, rationale) VALUES (?, ?, ?, ?)",
                               (q_id, opt['text'], 1 if opt['is_correct'] else 0, opt['rationale']))
        
        conn.commit()
        conn.close()
        
        # Clear the file after successful ingestion
        os.remove(json_path)
        print("SUCCESS: Database updated and temporary file cleared.")
        
    except Exception as e:
        print(f"CRITICAL ERROR during ingestion: {e}")

if __name__ == "__main__":
    main()
