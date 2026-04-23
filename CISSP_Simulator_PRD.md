# Product Requirements Document (PRD): CISSP Adaptive Test Simulator

## 1. Project Overview
The objective is to build a high-fidelity replica of the (ISC)² CISSP Computerized Adaptive Testing (CAT) environment for Windows 11. The simulator will adjust question difficulty based on user performance, allow for session persistence (resuming tests), and provide a detailed diagnostic review upon completion.

## 2. Target Standards (2026 Guidelines)
- **Exam Type:** Computerized Adaptive Testing (CAT).
- **Question Volume:** Minimum 100, Maximum 150.
- **Pre-test Items:** 25 unscored questions per session (randomly placed).
- **Time Limit:** 3 Hours (Note: Timer logic is excluded from the UI per user requirement but remains a background constraint for the PRD).
- **Navigation:** Strict forward-only movement; no backtracking or marking for review.

## 3. Functional Requirements

### 3.1 Adaptive Testing Logic (CAT Engine)
- **IRT Integration:** Use Item Response Theory (Theta $\\theta$ scale) to estimate user ability.
- **Difficulty Scaling:** Increase/decrease question difficulty based on the previous answer's correctness.
- **Stopping Criteria:** - Stop at 100 questions if ability is 95% certain to be above/below the passing standard.
    - Otherwise, continue up to 150 questions.
- **Domain Distribution:** Ensure balanced representation across the 8 CISSP domains:
    1. Security and Risk Management
    2. Asset Security
    3. Security Architecture and Engineering
    4. Communication and Network Security
    5. Identity and Access Management (IAM)
    6. Security Assessment and Testing
    7. Security Operations
    8. Software Development Security

### 3.2 Persistence & Session Management
- **Auto-Save:** The system must save the session state (current question, ability score, and response history) after every "Next" click.
- **Resumability:** Users must be able to close the app and resume exactly where they left off.
- **Session Reset:** A "New Test" button must allow the user to terminate the current session (archiving it) and start a fresh test at any time.

### 3.3 Diagnostic Feedback & Review
- **Post-Exam Portal:** Triggered only after test termination.
- **Incorrect Item Analysis:** Display the question stem, all options, the user's wrong answer, and the correct answer.
- **Rationale:** Provide a detailed explanation for *why* the correct answer is right and *why* each distractor is wrong.
- **Study Recommendations:** List specific sub-topics and their corresponding Domain ID/Title where the user demonstrated low proficiency.

## 4. Technical Architecture

### 4.1 Data Layer (SQLite Schema)
- **Questions Table:** ID, Domain ID, Topic, Stem, Difficulty ($\\theta$), Is_Pretest.
- **Options Table:** ID, Question_ID, Text, Is_Correct, Rationale.
- **Session_State Table:** Session_ID, Current_Theta, Count, Active_Flag.
- **Response_Log Table:** Log_ID, Session_ID, Question_ID, Selected_Option_ID, Is_Correct.

### 4.2 Application Layer
- **Frontend:** Windows 11 Desktop (Fluent Design), focused on a distraction-free "Pearson VUE" skin.
- **Backend:** Logic for IRT calculations and adaptive question selection.

## 5. User Interface Requirements
- **Testing Screen:** Minimalist; displays question, 4 radio buttons, and a "Next" button.
- **Dashboard:** Provides "New Test" and "Resume Test" options.
- **Review Screen:** Detailed list of missed questions with searchable/filterable categories.
