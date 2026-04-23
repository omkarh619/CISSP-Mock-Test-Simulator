# CISSP CAT Simulator

A high-fidelity replica of the (ISC)² CISSP Computerized Adaptive Testing (CAT) environment for Windows 11.

## Project Overview
This simulator implements Item Response Theory (IRT) to adjust question difficulty based on user performance. It follows the 2026 CISSP exam guidelines.

## Development Status

| Feature | Status | Description |
| :--- | :--- | :--- |
| **Project Initialization** | Completed | Structure, dependencies, and entry point set up. |
| **Database Schema** | Completed | SQLite with WAL mode, schema for CAT and persistence. |
| **CAT Engine** | Completed | IRT (3PL model) and EAP estimation implemented. |
| **UI Development** | Completed | PyQt6-based Dashboard, Testing, and Review screens. |
| **Session Management** | Completed | Auto-save and Resume functionality integrated. |
| **Diagnostic Review** | Completed | Detailed post-exam review with rationales. |

## Tech Stack
- **Language:** Python 3.9+
- **Database:** SQLite
- **UI:** PyQt6
- **Logic:** NumPy, SciPy (IRT calculations)

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Seed the database with sample questions: `python src/engine/seed_data.py`
3. Run the application: `python src/main.py`

## Features Implemented
- **CAT Engine:** 3-Parameter Logistic (3PL) model with EAP estimation.
- **Adaptive Selection:** Domain balancing and difficulty matching.
- **Persistence:** SQLite-backed session management with auto-save.
- **Modern UI:** Windows 11 Fluent Design inspired PyQt6 interface.
- **Diagnostic Review:** Detailed post-exam breakdown with rationales.

## CISSP Domains Covered
1. Security and Risk Management
2. Asset Security
3. Security Architecture and Engineering
4. Communication and Network Security
5. Identity and Access Management (IAM)
6. Security Assessment and Testing
7. Security Operations
8. Software Development Security
