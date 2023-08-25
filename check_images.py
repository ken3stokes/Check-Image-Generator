import sys
import os
import random
import matplotlib.pyplot as plt
from datetime import datetime
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
                             QWidget, QSpinBox, QMessageBox, QScrollArea, QDialog, QLineEdit, QFileDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSettings


# Utility Functions for Number Conversion
def number_to_words(n):
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "Ten", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    if 1 <= n < 10:
        return ones[n]
    elif 11 <= n < 20:
        return teens[n - 10]
    elif 20 <= n < 100:
        return tens[n // 10] + " " + ones[n % 10]
    elif 100 <= n < 1000:
        return ones[n // 100] + " Hundred " + number_to_words(n % 100)
    else:
        return ""


# Check Generation Functions
def generate_final_real_check_image(file_path):
    payee = "John Doe"
    amount_number = round(random.uniform(1, 1000), 2)
    amount_words = number_to_words(int(amount_number)) + " and " + str(int((amount_number * 100) % 100)) + "/100"
    date = datetime.now().strftime("%m/%d/%Y")
    memo = "For services rendered."

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.1, 0.9, "BANK OF OPENAI", weight='bold')
    ax.text(0.65, 0.9, f"Date: {date}")
    ax.text(0.1, 0.75, f"Pay to the Order of: {payee}")
    ax.text(0.7, 0.75, f"${amount_number:,.2f}")
    ax.text(0.1, 0.6, f"{amount_words} dollars")
    ax.text(0.1, 0.3, f"Memo: {memo}")
    ax.text(0.7, 0.3, "Signature: ________")
    ax.text(0.1, 0.15, "||: 0123456789 :||   123456789012   ||: 0123")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(file_path)
    plt.close(fig)


def generate_batch_real_check_images(output_directory, num_checks=1):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    generated_files = []
    for i in range(num_checks):
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"check_{current_time}_{i + 1}.png"
        file_path = os.path.join(output_directory, file_name)
        generate_final_real_check_image(file_path)
        generated_files.append(file_path)
    return generated_files


# Utility Functions for Database
def setup_database():
    conn = sqlite3.connect('checks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS checks 
                 (id INTEGER PRIMARY KEY, date TEXT, payee TEXT, amount REAL, memo TEXT, image_path TEXT)''')
    conn.commit()
    conn.close()


def insert_into_database(date, payee, amount, memo, image_path):
    conn = sqlite3.connect('checks.db')
    c = conn.cursor()
    c.execute("INSERT INTO checks (date, payee, amount, memo, image_path) VALUES (?, ?, ?, ?, ?)",
              (date, payee, amount, memo, image_path))
    conn.commit()
    conn.close()


# GUI Code for Settings
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        # Create Widgets for Settings
        self.directory_label = QLabel("Default Output Directory:")
        self.directory_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        # Set Layout for Settings
        layout = QVBoxLayout()
        layout.addWidget(self.directory_label)
        layout.addWidget(self.directory_input)
        layout.addWidget(self.browse_button)
        self.setLayout(layout)
        # Connect the browse button to the slot
        self.browse_button.clicked.connect(self.browse_directory)
        self.settings = QSettings("CheckGenerator", "Preferences")
        default_dir = self.settings.value("output_directory", "")
        self.directory_input.setText(default_dir)

    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.directory_input.setText(dir_path)

    def accept(self):
        directory = self.directory_input.text()
        self.settings.setValue("output_directory", directory)
        super().accept()


# Main GUI Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Check Image Generator")
        self.setGeometry(100, 100, 700, 400)

        # Number of checks input
        self.check_num_input = QSpinBox(self)
        self.check_num_input.setMinimum(1)
        self.check_num_input.setMaximum(25)
        self.check_num_input.setValue(1)
        self.check_num_input_label = QLabel("Number of checks:")

        # Generate button
        self.generate_button = QPushButton("Generate Checks", self)
        self.generate_button.clicked.connect(self.generate_checks)

        # Status label for feedback
        self.status_label = QLabel("", self)

        # Help button
        self.help_button = QPushButton("Help", self)
        self.help_button.clicked.connect(self.show_help)

        # Settings button
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.show_settings)

        # Preview Image
        self.check_image_label = QLabel(self)
        self.check_image_label.setFixedSize(640, 320)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.check_image_label)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.check_num_input_label)
        layout.addWidget(self.check_num_input)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.help_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.scroll_area)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def generate_checks(self):
        num_checks = self.check_num_input.value()
        settings = QSettings("CheckGenerator", "Preferences")
        output_dir = settings.value("output_directory", r"C:\Users\xx\xxx\Check Images")

        generated_files = generate_batch_real_check_images(output_dir, num_checks=num_checks)

        if generated_files:
            self.status_label.setText(f"{len(generated_files)} checks generated!")

            if len(generated_files) <= 2:
                last_check_path = generated_files[-1]
                pixmap = QPixmap(last_check_path).scaled(self.check_image_label.width(),
                                                         self.check_image_label.height(),
                                                         Qt.KeepAspectRatio,
                                                         Qt.SmoothTransformation)

                if not pixmap.isNull():
                    self.check_image_label.setPixmap(pixmap)
                else:
                    self.status_label.setText("Failed to load the generated check image!")
            else:
                self.check_image_label.clear()

            QMessageBox.information(self, 'Success', f"{len(generated_files)} checks generated successfully!")

            # Ingest into database
            for file in generated_files:
                date = datetime.now().strftime("%Y-%m-%d")
                payee = "John Doe"
                amount = round(random.uniform(1, 1000), 2)
                memo = "For services rendered"
                insert_into_database(date, payee, amount, memo, file)
        else:
            self.status_label.setText("No checks were generated. Check the output directory and permissions!")

    def show_help(self):
        QMessageBox.information(self, "Help",
                                "This tool allows you to generate fictional checks. Use the spinbox to select the number of checks to generate. Click 'Generate Checks' to create the checks.")

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()


if __name__ == '__main__':
    setup_database()  # Setup the database when the application starts
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
