import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import CISSPApp
from src.engine.seed_data import seed_database

def capture_all_screens():
    # Ensure we have data
    if not os.path.exists("data/cissp_simulator.db"):
        seed_database()

    app = QApplication(sys.argv)
    
    # Apply stylesheet (must match main.py)
    app.setStyleSheet("""
        QMainWindow { background-color: #ffffff; }
        #header_frame { background-color: #003057; color: white; border: none; border-radius: 0px; margin: 0px; padding: 10px; }
        #header_label { color: white; font-weight: bold; }
        #question_text { font-size: 18px; line-height: 1.6; padding: 20px; }
        #footer_frame { background-color: #e1e1e1; border-top: 1px solid #cccccc; border-radius: 0px; margin: 0px; padding: 10px; }
        QPushButton { background-color: #003057; color: white; border: 1px solid #002646; border-radius: 2px; padding: 10px 30px; font-size: 16px; font-weight: bold; }
        #card_frame { background-color: #f9f9f9; border: 1px solid #dddddd; border-radius: 4px; }
    """)
    
    window = CISSPApp()
    window.show()
    
    # Process all events to ensure window is fully rendered
    QApplication.processEvents()
    time.sleep(2) # Give OS time to show window
    
    screen = app.primaryScreen()
    
    # 1. Capture Dashboard
    QApplication.processEvents()
    screen.grabWindow(window.winId()).save("visual_test_1_dashboard.png")
    print("Captured Dashboard.")
    
    # 2. Capture Testing Screen
    window.start_new_test()
    QApplication.processEvents()
    time.sleep(1)
    screen.grabWindow(window.winId()).save("visual_test_2_testing.png")
    print("Captured Testing Screen.")
    
    # 3. Capture Review Screen
    window.finish_test("Manual Visual Audit Triggered")
    QApplication.processEvents()
    time.sleep(1)
    screen.grabWindow(window.winId()).save("visual_test_3_review.png")
    print("Captured Review Screen.")
    
    window.close()

if __name__ == "__main__":
    capture_all_screens()
