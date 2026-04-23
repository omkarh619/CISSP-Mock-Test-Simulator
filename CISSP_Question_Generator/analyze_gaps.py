import sqlite3
import json
import os

DB_PATH = os.path.join("data", "cissp_simulator.db")
REPORT_PATH = os.path.join("CISSP_Question_Generator", "gap_report.json")

def analyze_gaps():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Domain Distribution
    cursor.execute("SELECT domain_id, COUNT(*) FROM questions GROUP BY domain_id")
    domain_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Ensure all 8 domains are represented
    full_domain_report = {i: domain_counts.get(i, 0) for i in range(1, 9)}

    # 2. Difficulty Distribution (b-parameter)
    # Easy: -3 to -1, Moderate: -1 to 1, Hard: 1 to 3
    cursor.execute("""
        SELECT 
            domain_id,
            SUM(CASE WHEN difficulty_b < -1 THEN 1 ELSE 0 END) as easy,
            SUM(CASE WHEN difficulty_b >= -1 AND difficulty_b <= 1 THEN 1 ELSE 0 END) as moderate,
            SUM(CASE WHEN difficulty_b > 1 THEN 1 ELSE 0 END) as hard
        FROM questions
        GROUP BY domain_id
    """)
    difficulty_report = {row[0]: {"easy": row[1], "moderate": row[2], "hard": row[3]} for row in cursor.fetchall()}

    # 3. Topic Gaps (Just a count of unique topics per domain)
    cursor.execute("SELECT domain_id, COUNT(DISTINCT topic) FROM questions GROUP BY domain_id")
    topic_diversity = {row[0]: row[1] for row in cursor.fetchall()}

    report = {
        "domain_distribution": full_domain_report,
        "difficulty_balance": difficulty_report,
        "topic_diversity": topic_diversity,
        "total_questions": sum(full_domain_report.values())
    }

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=4)
    
    conn.close()
    print(f"Gap report generated at {REPORT_PATH}")

if __name__ == "__main__":
    analyze_gaps()
