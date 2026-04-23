import json
import os

BATCH_FILE = os.path.join("CISSP_Question_Generator", "batch_questions.json")

def append_questions(new_questions):
    if os.path.exists(BATCH_FILE):
        with open(BATCH_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"questions": []}
    
    data["questions"].extend(new_questions)
    
    with open(BATCH_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Successfully appended {len(new_questions)} questions. Total: {len(data['questions'])}")

if __name__ == "__main__":
    # This script will be called with a list of questions
    pass
