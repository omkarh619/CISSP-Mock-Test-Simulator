import pytest
import numpy as np
from src.engine.cat_engine import CATEngine
from src.engine.database import DatabaseManager

@pytest.fixture
def db():
    # Use an in-memory database for testing
    return DatabaseManager(":memory:")

@pytest.fixture
def engine(db):
    return CATEngine(db)

def test_3pl_model(engine):
    # theta=0, a=1, b=0, c=0.25
    # P(0) = 0.25 + (1-0.25)/(1 + e^-1(0-0)) = 0.25 + 0.75/2 = 0.25 + 0.375 = 0.625
    p = engine.probability_correct(0.0, 1.0, 0.0, 0.25)
    assert p == 0.625

def test_theta_update_multiple(engine):
    # Initial theta 0, SE ~1.0
    responses = []
    prev_se = 1.1 # Initial high SE
    
    for i in range(5):
        # User consistently answers correctly on questions matched to their current theta
        current_theta, current_se = engine.update_theta(responses)
        responses.append({'a': 1.2, 'b': round(current_theta, 1), 'c': 0.25, 'is_correct': True})
        
    final_theta, final_se = engine.update_theta(responses)
    assert final_theta > 0
    assert final_se < 1.0 # SE should definitely be below 1.0 after 5 correct answers

def test_theta_update_incorrect(engine):
    # Initial theta 0, SE 1
    # Response: Incorrect on an easy question (b=-1.0)
    responses = [{'a': 1.0, 'b': -1.0, 'c': 0.25, 'is_correct': False}]
    new_theta, new_se = engine.update_theta(responses)
    assert new_theta < 0
    assert new_se < 1.0
