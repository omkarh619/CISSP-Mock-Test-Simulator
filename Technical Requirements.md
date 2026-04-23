# Technical Implementation Specification: CISSP CAT Simulator

## 1. Environment & Stack
- **OS:** Windows 11
- **Language:** Python 3.9+
- **Database:** SQLite (WAL Mode enabled)
- **Mathematical Libraries:** `numpy`, `scipy` (for IRT calculations)
- **UI Framework:** `Rich` (for CLI/Terminal) or `PyQt6` (for GUI)

## 2. Database Schema (DDL)
```sql
-- Enable Write-Ahead Logging for persistence
PRAGMA journal_mode=WAL;

CREATE TABLE domains (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    weight FLOAT NOT NULL -- e.g., 0.15 for 15%
);

CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    domain_id INTEGER,
    topic TEXT,
    stem TEXT NOT NULL,
    difficulty_b FLOAT NOT NULL, -- IRT 'b' parameter (-3.0 to 3.0)
    discrimination_a FLOAT DEFAULT 1.0, -- IRT 'a' parameter
    guessing_c FLOAT DEFAULT 0.25, -- IRT 'c' parameter (1/4 for 4 options)
    is_pretest BOOLEAN DEFAULT 0,
    FOREIGN KEY(domain_id) REFERENCES domains(id)
);

CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    current_theta FLOAT DEFAULT 0.0, -- User ability estimate
    standard_error FLOAT DEFAULT 1.0,
    is_active INTEGER DEFAULT 1,
    start_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    question_id TEXT,
    is_correct INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id),
    FOREIGN KEY(question_id) REFERENCES questions(id)
);

3. Core Algorithms

3.1 Item Response Theory (IRT) LogicThe probability $P$ of a correct answer is calculated via the 3-Parameter Logistic (3PL) model:
$$P(\theta) = c + \frac{1 - c}{1 + e^{-a(\theta - b)}}
$$Theta ($\theta$) Update (The Adaptive Part):
After each response, update the user’s ability estimate using Maximum Likelihood Estimation (MLE) or Expected A Posteriori (EAP).If Correct: Shift $\theta$ upward based on question difficulty.If Incorrect: Shift $\theta$ downward.


3.2 Question Selection AlgorithmFilter: Select questions not already in responses for current_session.Domain Balance: Calculate current domain distribution in responses. If a domain is < 80% of its target weight, prioritize that domain_id.Difficulty Match: Select a question where $b$ (difficulty) is closest to the user's current $\theta$.Pre-test Injection: Inject 1 "pre-test" question (is_pretest=1) every 4–5 questions until 25 are served.


3.3 Termination Logic (The "Stopping" Rule)The test terminates if:question_count >= 100 AND standard_error < 0.3 (95% confidence).question_count == 150.The system determines with 95% certainty that the user's $\theta$ cannot cross the "Passing Standard" (set at $\theta = 0.0$ or higher).

4. Feature: Persistence & Resume
On Startup: Query sessions where is_active = 1.

Resume: If found, load current_theta and the count from responses.

New Test: If user clicks "New Test", update existing active sessions to is_active = 0 and create a new session UUID.

5. Diagnostic Reporting Logic
At termination, calculate:

Domain Proficiency: (Correct Scored Questions / Total Scored Questions) per domain_id.

Topic Gap List: Select topic tags from responses where is_correct = 0.

Output: Generate a summary table mapping domain_id + title to the topic list.

6. Security & Integrity
One-Way Flow: Code must not implement a "Back" button or "Previous" function.

Commit on Answer: Database COMMIT must occur immediately after the user selects an option and clicks "Next".