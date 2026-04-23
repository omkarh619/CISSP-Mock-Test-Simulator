import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QRadioButton, 
                             QButtonGroup, QStackedWidget, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from src.engine.database import DatabaseManager
from src.engine.cat_engine import CATEngine

class CISSPApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.engine = CATEngine(self.db)
        self.session_id = None
        self.current_question = None

        self.setWindowTitle("CISSP CAT Simulator")
        self.resize(1024, 768)
        self.setMinimumSize(800, 600)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.init_dashboard()
        self.init_testing_screen()
        self.init_review_screen()

        # Check for active session
        active_session = self.db.get_active_session()
        if active_session:
            self.dashboard_resume_btn.setEnabled(True)
            self.session_id = active_session['id']
        else:
            self.dashboard_resume_btn.setEnabled(False)

        self.show()

    def init_dashboard(self):
        self.dashboard = QWidget()
        layout = QVBoxLayout(self.dashboard)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Main Card for Dashboard
        card = QFrame()
        card.setObjectName("card_frame")
        card.setFixedWidth(500)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(30)

        title = QLabel("CISSP CAT Simulator")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("High-Fidelity Replica of the (ISC)² CAT Environment")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #666666;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)

        self.dashboard_new_btn = QPushButton("Start New Test Session")
        self.dashboard_new_btn.setMinimumHeight(50)
        self.dashboard_new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dashboard_new_btn.clicked.connect(self.start_new_test)
        btn_layout.addWidget(self.dashboard_new_btn)

        self.dashboard_resume_btn = QPushButton("Resume Previous Test Session")
        self.dashboard_resume_btn.setMinimumHeight(50)
        self.dashboard_resume_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dashboard_resume_btn.clicked.connect(self.resume_test)
        btn_layout.addWidget(self.dashboard_resume_btn)

        card_layout.addLayout(btn_layout)
        
        info_label = QLabel("Exam Guidelines (2026): 100-150 Questions | 3 Hours")
        info_label.setFont(QFont("Segoe UI", 9))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #999999;")
        card_layout.addWidget(info_label)

        layout.addWidget(card)
        self.central_widget.addWidget(self.dashboard)

    def init_testing_screen(self):
        self.testing_screen = QWidget()
        layout = QVBoxLayout(self.testing_screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header Bar
        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_layout = QHBoxLayout(header_frame)
        
        exam_title = QLabel("Certified Information Systems Security Professional (CISSP)")
        exam_title.setObjectName("header_label")
        header_layout.addWidget(exam_title)

        header_layout.addStretch()

        self.count_label = QLabel("Question 1 of 150")
        self.count_label.setObjectName("header_label")
        header_layout.addWidget(self.count_label)
        layout.addWidget(header_frame)

        # Content Area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(50, 30, 50, 30)

        self.domain_label = QLabel("Domain: ")
        self.domain_label.setStyleSheet("font-weight: bold; color: #666666;")
        content_layout.addWidget(self.domain_label)

        # Question Area
        self.question_text = QLabel("Question Stem")
        self.question_text.setObjectName("question_text")
        self.question_text.setWordWrap(True)
        content_layout.addWidget(self.question_text)

        # Options
        self.options_group = QButtonGroup()
        self.option_buttons = []
        for i in range(4):
            rb = QRadioButton(f"Option {i+1}")
            self.options_group.addButton(rb, i)
            self.option_buttons.append(rb)
            content_layout.addWidget(rb)

        content_layout.addStretch()
        layout.addWidget(content_widget)

        # Footer Bar
        footer_frame = QFrame()
        footer_frame.setObjectName("footer_frame")
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.addStretch()
        
        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedSize(120, 40)
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.submit_answer)
        self.options_group.buttonClicked.connect(lambda: self.next_btn.setEnabled(True))
        
        footer_layout.addWidget(self.next_btn)
        layout.addWidget(footer_frame)

        self.central_widget.addWidget(self.testing_screen)

    def init_review_screen(self):
        self.review_screen = QWidget()
        layout = QVBoxLayout(self.review_screen)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("header_frame")
        header_layout = QHBoxLayout(header)
        title = QLabel("Post-Exam Diagnostic Review")
        title.setObjectName("header_label")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        layout.addWidget(header)

        # Scroll Area for Content
        self.review_scroll = QScrollArea()
        self.review_scroll.setWidgetResizable(True)
        self.review_scroll.setStyleSheet("border: none; background-color: #f3f3f3;")
        
        self.review_content = QWidget()
        self.review_content.setStyleSheet("background-color: #f3f3f3;")
        self.review_layout = QVBoxLayout(self.review_content)
        self.review_layout.setContentsMargins(50, 30, 50, 30)
        self.review_layout.setSpacing(20)
        
        self.review_scroll.setWidget(self.review_content)
        layout.addWidget(self.review_scroll)

        # Footer
        footer = QFrame()
        footer.setObjectName("footer_frame")
        footer_layout = QHBoxLayout(footer)
        footer_layout.addStretch()
        self.exit_btn = QPushButton("Return to Dashboard")
        self.exit_btn.setMinimumHeight(40) # Remove setFixedSize(200, 40)
        self.exit_btn.clicked.connect(lambda: self.central_widget.setCurrentIndex(0))
        footer_layout.addWidget(self.exit_btn)
        layout.addWidget(footer)

        self.central_widget.addWidget(self.review_screen)

    def start_new_test(self):
        self.session_id = self.db.create_session()
        self.load_next_question()
        self.central_widget.setCurrentWidget(self.testing_screen)

    def resume_test(self):
        active_session = self.db.get_active_session()
        if active_session:
            self.session_id = active_session['id']
            self.load_next_question()
            self.central_widget.setCurrentWidget(self.testing_screen)

    def load_next_question(self):
        # Check termination
        terminated, reason = self.engine.check_termination(self.session_id)
        if terminated:
            self.finish_test(reason)
            return

        question = self.engine.select_next_question(self.session_id)
        if not question:
            self.finish_test("No more questions available.")
            return

        self.current_question = question
        options = self.db.get_question_options(question['id'])
        self.current_options = options

        # Get domain title
        domains = self.db.get_domains()
        domain_map = {d['id']: d['title'] for d in domains}
        self.domain_label.setText(f"Domain: {domain_map.get(question['domain_id'], 'Unknown')}")
        
        count = self.db.get_session_responses_count(self.session_id)
        self.count_label.setText(f"Question: {count + 1} {'(Pre-test)' if question['is_pretest'] else ''}")
        self.question_text.setText(question['stem'])

        # Reset options
        self.next_btn.setEnabled(False)
        self.options_group.setExclusive(False)
        for i, rb in enumerate(self.option_buttons):
            rb.setChecked(False)
            if i < len(options):
                rb.setText(options[i]['text'])
                rb.show()
                self.options_group.setId(rb, i)
            else:
                rb.hide()
        self.options_group.setExclusive(True)

    def submit_answer(self):
        selected_id = self.options_group.checkedId()
        if selected_id == -1:
            return

        option = self.current_options[selected_id]
        is_correct = option['is_correct']

        # Update Engine and Database
        # 1. Get current scored responses (exclude pre-test) for theta update
        responses_cursor = self.db._get_connection().execute("""
            SELECT q.difficulty_b, q.discrimination_a, q.guessing_c, r.is_correct
            FROM responses r
            JOIN questions q ON r.question_id = q.id
            WHERE r.session_id = ? AND q.is_pretest = 0
        """, (self.session_id,)).fetchall()
        
        responses_list = [{'b': r['difficulty_b'], 'a': r['discrimination_a'], 'c': r['guessing_c'], 'is_correct': r['is_correct']} for r in responses_cursor]
        
        # Only add current response to theta update if it's NOT a pre-test item
        if not self.current_question['is_pretest']:
            responses_list.append({
                'b': self.current_question['difficulty_b'],
                'a': self.current_question['discrimination_a'],
                'c': self.current_question['guessing_c'],
                'is_correct': is_correct
            })

        new_theta, new_se = self.engine.update_theta(responses_list)
        
        self.db.save_response(self.session_id, self.current_question['id'], option['id'], is_correct, new_theta, new_se)

        self.load_next_question()

    def finish_test(self, reason):
        # Set session inactive
        with self.db._get_connection() as conn:
            conn.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (self.session_id,))
            conn.commit()

        self.show_review(reason)
        self.central_widget.setCurrentWidget(self.review_screen)

    def show_review(self, reason):
        # Clear layout
        while self.review_layout.count():
            item = self.review_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        reason_label = QLabel(f"Result: {reason}")
        reason_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.review_layout.addWidget(reason_label)

        # Domain Proficiency Summary
        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)
        summary_title = QLabel("Domain Proficiency & Study Recommendations")
        summary_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        summary_layout.addWidget(summary_title)

        with self.db._get_connection() as conn:
            prof = conn.execute("""
                SELECT d.title, 
                       SUM(CASE WHEN r.is_correct = 1 THEN 1 ELSE 0 END) as correct,
                       COUNT(*) as total
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                JOIN domains d ON q.domain_id = d.id
                WHERE r.session_id = ? AND q.is_pretest = 0
                GROUP BY d.title
            """, (self.session_id,)).fetchall()

            for p in prof:
                pct = (p['correct'] / p['total']) * 100
                p_label = QLabel(f"{p['title']}: {pct:.1f}% ({p['correct']}/{p['total']})")
                if pct < 70:
                    p_label.setStyleSheet("color: #d83b01; font-weight: bold;") # High priority study
                summary_layout.addWidget(p_label)
        
        self.review_layout.addWidget(summary_frame)

        # Show incorrect answers details
        detail_title = QLabel("Incorrect Items Analysis")
        detail_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        detail_title.setContentsMargins(0, 20, 0, 10)
        self.review_layout.addWidget(detail_title)

        with self.db._get_connection() as conn:
            incorrect = conn.execute("""
                SELECT q.stem, r.selected_option_id, q.id
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.session_id = ? AND r.is_correct = 0
            """, (self.session_id,)).fetchall()

            for inc in incorrect:
                q_frame = QFrame()
                q_frame.setFrameShape(QFrame.Shape.StyledPanel)
                q_layout = QVBoxLayout(q_frame)
                
                q_text = QLabel(f"Question: {inc['stem']}")
                q_text.setWordWrap(True)
                q_layout.addWidget(q_text)

                # Find correct option
                options = self.db.get_question_options(inc['id'])
                for opt in options:
                    opt_text = QLabel(f"- {opt['text']} {'(Your Answer)' if opt['id'] == inc['selected_option_id'] else ''} {'[CORRECT]' if opt['is_correct'] else ''}")
                    if opt['is_correct']:
                        opt_text.setStyleSheet("color: green;")
                    elif opt['id'] == inc['selected_option_id']:
                        opt_text.setStyleSheet("color: red;")
                    q_layout.addWidget(opt_text)
                
                # Rationale
                correct_opt = next(opt for opt in options if opt['is_correct'])
                rat_label = QLabel(f"Rationale: {correct_opt['rationale']}")
                rat_label.setWordWrap(True)
                rat_label.setStyleSheet("font-style: italic;")
                q_layout.addWidget(rat_label)

                self.review_layout.addWidget(q_frame)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CISSPApp()
    sys.exit(app.exec())
