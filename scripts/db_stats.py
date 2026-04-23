import sqlite3
import os

DB_PATH = os.path.join("data", "cissp_simulator.db")

def get_stats():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*50)
    print("      CISSP QUESTION BANK STATISTICS")
    print("="*50)

    # 1. Overall Totals
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_q = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM questions WHERE is_pretest = 1")
    total_pretest = cursor.fetchone()[0]
    
    print(f"Total Questions: {total_q}")
    print(f"Scored Items:    {total_q - total_pretest}")
    print(f"Pre-test Items:  {total_pretest}")
    print("-" * 50)

    # 2. Domain Breakdown
    print(f"{'ID':<3} | {'Domain Title':<40} | {'Count':<5}")
    print("-" * 50)
    cursor.execute("""
        SELECT d.id, d.title, COUNT(q.id) 
        FROM domains d 
        LEFT JOIN questions q ON d.id = q.domain_id 
        GROUP BY d.id
    """)
    for row in cursor.fetchall():
        print(f"{row[0]:<3} | {row[1]:<40} | {row[2]:<5}")

    # 3. Difficulty Distribution
    print("-" * 50)
    print("DIFFICULTY DISTRIBUTION (Theta Scale)")
    print("-" * 50)
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN difficulty_b < -1 THEN 1 ELSE 0 END) as easy,
            SUM(CASE WHEN difficulty_b >= -1 AND difficulty_b <= 1 THEN 1 ELSE 0 END) as moderate,
            SUM(CASE WHEN difficulty_b > 1 THEN 1 ELSE 0 END) as hard
        FROM questions
    """)
    diff = cursor.fetchone()
    print(f"Easy (-3.0 to -1.1):     {diff[0] or 0}")
    print(f"Moderate (-1.0 to 1.0):  {diff[1] or 0}")
    print(f"Hard (1.1 to 3.0):       {diff[2] or 0}")

    # 4. Top Topics
    print("-" * 50)
    print("TOP 10 TOPICS BY VOLUME")
    print("-" * 50)
    cursor.execute("""
        SELECT topic, COUNT(*) as c 
        FROM questions 
        GROUP BY topic 
        ORDER BY c DESC 
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"{row[0]:<44} | {row[1]}")

    print("="*50 + "\n")
    conn.close()

if __name__ == "__main__":
    get_stats()
