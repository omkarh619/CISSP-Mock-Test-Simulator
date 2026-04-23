import pytest
import os
from src.engine.database import DatabaseManager
from src.engine.cat_engine import CATEngine

@pytest.fixture
def db():
    db_path = "data/test_persistence.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = DatabaseManager(db_path)
    return db

def test_session_persistence(db):
    # 1. Create a session and answer one question
    session_id = db.create_session()
    
    # Add a dummy question for testing
    db._get_connection().execute("INSERT INTO domains VALUES (1, 'Test', 1.0)")
    db._get_connection().execute("INSERT INTO questions VALUES ('q1', 1, 'Topic', 'Stem', 0.5, 1.0, 0.25, 0)")
    db._get_connection().execute("INSERT INTO options (question_id, text, is_correct, rationale) VALUES ('q1', 'Opt', 1, 'Rat')")
    
    # Save a response
    db.save_response(session_id, 'q1', 1, 1, 0.5, 0.8)
    
    # 2. Simulate app restart by getting active session
    active = db.get_active_session()
    assert active is not None
    assert active['id'] == session_id
    assert active['current_theta'] == 0.5
    assert active['standard_error'] == 0.8
    
    # 3. Create a new session, verify old one is deactivated
    new_id = db.create_session()
    active_now = db.get_active_session()
    assert active_now['id'] == new_id
    
    old_session = db.get_session_details(session_id)
    assert old_session['is_active'] == 0
