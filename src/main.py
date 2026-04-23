import sys
import os

# Add the project root to sys.path to ensure absolute imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import CISSPApp

def main():
    app = QApplication(sys.argv)
    
    # Apply a global style for Pearson VUE replica look
    app.setStyleSheet("""
        QMainWindow {
            background-color: #ffffff;
        }
        /* Header Bar */
        #header_frame {
            background-color: #003057; /* ISC2 Dark Blue */
            color: white;
            border: none;
            border-radius: 0px;
            margin: 0px;
            padding: 10px;
        }
        QLabel {
            color: #333333; /* Dark Gray for visibility */
            font-family: 'Segoe UI', sans-serif;
        }
        #header_label {
            color: #ffffff; /* Explicit White for blue background */
            font-weight: bold;
        }
        /* Question Area */
        #question_text {
            color: #000000; /* Pure Black for question text */
            font-size: 18px;
            line-height: 1.6;
            padding: 20px;
        }
        QRadioButton {
            color: #000000;
            font-size: 16px;
            spacing: 15px;
            padding: 10px;
        }
        QRadioButton::indicator {
            width: 20px;
            height: 20px;
        }
        /* Footer Bar */
        #footer_frame {
            background-color: #e1e1e1;
            border-top: 1px solid #cccccc;
            border-radius: 0px;
            margin: 0px;
            padding: 10px;
        }
        QPushButton {
            background-color: #003057;
            color: white;
            border: 1px solid #002646;
            border-radius: 2px;
            padding: 10px 30px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #004b87;
        }
        QPushButton:pressed {
            background-color: #002646;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #888888;
            border: 1px solid #aaaaaa;
        }
        /* Dashboard Cards */
        #card_frame {
            background-color: #f9f9f9;
            border: 1px solid #dddddd;
            border-radius: 4px;
        }
    """)
    
    window = CISSPApp()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
