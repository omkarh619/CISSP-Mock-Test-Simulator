import numpy as np
from scipy.stats import norm

class CATEngine:
    def __init__(self, db_manager):
        self.db = db_manager
        self.theta_grid = np.arange(-4.0, 4.1, 0.1)
        self.prior = norm.pdf(self.theta_grid, 0, 1)
        self.prior /= self.prior.sum()

    def probability_correct(self, theta, a, b, c):
        """3-Parameter Logistic (3PL) model."""
        return c + (1 - c) / (1 + np.exp(-a * (theta - b)))

    def update_theta(self, responses):
        """
        Update user ability estimate (theta) and standard error using EAP.
        responses: List of dicts with {'a': discrimination, 'b': difficulty, 'c': guessing, 'is_correct': boolean}
        """
        if not responses:
            return 0.0, 1.0

        likelihood = np.ones_like(self.theta_grid)
        for resp in responses:
            p = self.probability_correct(self.theta_grid, resp['a'], resp['b'], resp['c'])
            if resp['is_correct']:
                likelihood *= p
            else:
                likelihood *= (1 - p)

        posterior = likelihood * self.prior
        posterior_sum = posterior.sum()
        
        if posterior_sum == 0: # Numerical stability
            return 0.0, 1.0
            
        posterior /= posterior_sum

        # EAP estimate
        new_theta = np.sum(self.theta_grid * posterior)
        
        # Standard Error
        new_se = np.sqrt(np.sum(((self.theta_grid - new_theta) ** 2) * posterior))
        
        return float(new_theta), float(new_se)

    def select_next_question(self, session_id):
        """
        Question Selection Algorithm:
        1. Pre-test Injection
        2. Domain Balance
        3. Difficulty Match
        """
        unanswered = self.db.get_unanswered_questions(session_id)
        if not unanswered:
            return None

        # Get session details
        session = self.db.get_session_details(session_id)
        current_theta = session['current_theta']
        count = self.db.get_session_responses_count(session_id)
        
        # Pre-test Injection: 1 pre-test every 5 questions until 25
        is_pretest_turn = (count + 1) % 5 == 0 and count < 125
        
        eligible_questions = []
        if is_pretest_turn:
            eligible_questions = [q for q in unanswered if q['is_pretest']]
            if not eligible_questions:
                eligible_questions = unanswered
        else:
            # Domain Balancing
            # 1. Get current domain distribution from responses
            with self.db._get_connection() as conn:
                dist = conn.execute("""
                    SELECT q.domain_id, COUNT(*) as c
                    FROM responses r
                    JOIN questions q ON r.question_id = q.id
                    WHERE r.session_id = ?
                    GROUP BY q.domain_id
                """, (session_id,)).fetchall()
                domain_counts = {d['domain_id']: d['c'] for d in dist}
                
                # 2. Get target weights
                domains = self.db.get_domains()
                target_weights = {d['id']: d['weight'] for d in domains}
                
                # 3. Find domains below target
                total_answered = sum(domain_counts.values()) or 1
                underrepresented = []
                for d_id, weight in target_weights.items():
                    current_weight = domain_counts.get(d_id, 0) / total_answered
                    if current_weight < weight:
                        underrepresented.append(d_id)
                
                if underrepresented:
                    eligible_questions = [q for q in unanswered if not q['is_pretest'] and q['domain_id'] in underrepresented]
                
                if not eligible_questions:
                    eligible_questions = [q for q in unanswered if not q['is_pretest']]
            
            if not eligible_questions:
                eligible_questions = unanswered

        # Difficulty Match: Select closest to theta
        best_q = min(eligible_questions, key=lambda q: abs(q['difficulty_b'] - current_theta))
        return best_q

    def check_termination(self, session_id):
        """
        1. count >= 100 AND se < 0.3
        2. count == 150
        3. 95% certainty above/below passing standard (theta=0)
        """
        count = self.db.get_session_responses_count(session_id)
        session = self.db.get_session_details(session_id)
        se = session['standard_error']
        theta = session['current_theta']

        if count >= 150:
            return True, "Maximum questions reached."
        
        if count >= 100:
            if se < 0.3:
                return True, "Ability estimate confidence reached."
            
            # 95% confidence interval: [theta - 1.96*se, theta + 1.96*se]
            lower_bound = theta - 1.96 * se
            upper_bound = theta + 1.96 * se
            
            if lower_bound > 0: # Above passing
                return True, "Passed with high certainty."
            if upper_bound < -0.5: # Below passing (setting slightly lower for leniency)
                return True, "Failed with high certainty."

        return False, None
