import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QApplication, QFrame
from src.ui.main_window import CISSPApp
import time

def visual_audit():
    app = QApplication(sys.argv)
    
    # Exact stylesheet from main.py for high-fidelity audit
    app.setStyleSheet("""
        QMainWindow { background-color: #ffffff; }
        #header_frame { background-color: #003057; color: white; border: none; border-radius: 0px; margin: 0px; padding: 10px; }
        #header_label { color: white; font-weight: bold; }
        #question_text { font-size: 18px; line-height: 1.6; padding: 20px; }
        #footer_frame { background-color: #e1e1e1; border-top: 1px solid #cccccc; border-radius: 0px; margin: 0px; padding: 10px; }
        QPushButton { background-color: #003057; color: white; border: 1px solid #002646; border-radius: 2px; padding: 10px 30px; font-size: 16px; font-weight: bold; }
    """)
    
    window = CISSPApp()
    window.show()
    
    # Switch to testing screen immediately
    window.central_widget.setCurrentWidget(window.testing_screen)
    
    print("--- UI Visual Audit (Corrected) ---")
    
    # Force process events to ensure styles and layouts are applied
    QApplication.processEvents()
    time.sleep(2) # Significant delay for rendering
    
    try:
        screen = app.primaryScreen()
        screenshot = screen.grabWindow(window.winId())
        screenshot.save("ui_audit_screenshot.png")
        print("Screenshot saved to ui_audit_screenshot.png")
    except Exception as e:
        print(f"Screenshot failed: {e}")

    window.close()

if __name__ == "__main__":
    visual_audit()
