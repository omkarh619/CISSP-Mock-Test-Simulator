import pytest
import os
import random
from src.engine.database import DatabaseManager
from src.engine.cat_engine import CATEngine
from src.engine.seed_data import seed_database

@pytest.fixture
def test_db():
    db_path = "data/test_simulator.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize and seed
    seed_database(db_path)
    db = DatabaseManager(db_path)
    return db

@pytest.fixture
def engine(test_db):
    return CATEngine(test_db)

def test_full_simulation(test_db, engine):
    """Simulate a user taking a full test to verify engine flow."""
    session_id = test_db.create_session()
    
    # Target ability (theta) for the simulated user
    user_true_ability = 0.5 
    
    questions_answered = 0
    terminated = False
    
    print(f"\nStarting simulation for session {session_id}")
    
    while not terminated and questions_answered < 155:
        q = engine.select_next_question(session_id)
        assert q is not None, "Engine failed to select a question"
        
        # Simulate user response based on their 'true' ability
        # Probability of correct answer using 3PL
        p = engine.probability_correct(user_true_ability, q['discrimination_a'], q['difficulty_b'], q['guessing_c'])
        is_correct = 1 if random.random() < p else 0
        
        # Get options to pick one
        options = test_db.get_question_options(q['id'])
        selected_option = next(opt for opt in options if opt['is_correct'] == is_correct)
        
        # Update Engine state for theta calculation
        responses_cursor = test_db._get_connection().execute("""
            SELECT q.difficulty_b, q.discrimination_a, q.guessing_c, r.is_correct
            FROM responses r
            JOIN questions q ON r.question_id = q.id
            WHERE r.session_id = ? AND q.is_pretest = 0
        """, (session_id,)).fetchall()
        
        responses_list = [{'b': r['difficulty_b'], 'a': r['discrimination_a'], 'c': r['guessing_c'], 'is_correct': r['is_correct']} for r in responses_cursor]
        
        if not q['is_pretest']:
            responses_list.append({
                'b': q['difficulty_b'],
                'a': q['discrimination_a'],
                'c': q['guessing_c'],
                'is_correct': is_correct
            })
            
        new_theta, new_se = engine.update_theta(responses_list)
        
        # Save to DB
        test_db.save_response(session_id, q['id'], selected_option['id'], is_correct, new_theta, new_se)
        
        questions_answered += 1
        terminated, reason = engine.check_termination(session_id)
        
        if questions_answered % 20 == 0:
            print(f"Progress: {questions_answered} questions. Current Theta: {new_theta:.2f}, SE: {new_se:.2f}")

    print(f"Simulation ended at {questions_answered} questions. Reason: {reason}")
    
    assert questions_answered >= 100, "Test terminated too early"
    assert questions_answered <= 150, "Test exceeded maximum question limit"
    
    # Verify final theta is somewhat close to true ability (within 2 SEs)
    session_details = test_db.get_session_details(session_id)
    final_theta = session_details['current_theta']
    final_se = session_details['standard_error']
    
    print(f"Final Estimate: {final_theta:.2f} (True: {user_true_ability}), SE: {final_se:.2f}")
    assert abs(final_theta - user_true_ability) < 2 * final_se or questions_answered == 150
