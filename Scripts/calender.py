import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QCalendarWidget, 
                             QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, 
                             QAction, QListWidget, QHBoxLayout, QPushButton, 
                             QLineEdit, QInputDialog, QCheckBox,QMessageBox, QDialog,
                             QLabel, QDialogButtonBox)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIcon, QBrush, QColor, QTextCharFormat

class CalendarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Task Calendar")
        self.setGeometry(300, 300, 800, 500)
    
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
    
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.show_tasks_for_date)
    
        # Task list widget
        self.task_list = QListWidget()
    
        # Task entry and buttons
        task_entry_layout = QVBoxLayout()
        self.task_entry = QLineEdit()
        self.task_entry.setPlaceholderText("Enter new task...")
        self.important_checkbox = QCheckBox("Important")
    
        # Button layout - this was missing from your layout structure
        button_layout = QHBoxLayout()
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_task)
    
        self.add_multi_date_button = QPushButton("Add Multi-Date Task")
        self.add_multi_date_button.clicked.connect(self.add_multi_date_task)
    
        # Add buttons to the horizontal layout
        button_layout.addWidget(self.add_task_button)
        button_layout.addWidget(self.add_multi_date_button)
    
        # Delete button (separate from the other two)
        self.delete_task_button = QPushButton("Delete Selected Task")
        self.delete_task_button.clicked.connect(self.delete_task)
    
        # Add everything to the task entry layout in the right order
        task_entry_layout.addWidget(self.task_entry)
        task_entry_layout.addWidget(self.important_checkbox)
        task_entry_layout.addLayout(button_layout)  # Add the button layout here
        task_entry_layout.addWidget(self.delete_task_button)
    
        # Task side layout
        task_side_layout = QVBoxLayout()
        task_side_layout.addWidget(self.task_list)
        task_side_layout.addLayout(task_entry_layout)
    
        # Add widgets to main layout
        main_layout.addWidget(self.calendar, 2)
        main_layout.addLayout(task_side_layout, 1)
    
        self.load_data()  # Load tasks and important tasks from file
    
        # Create system tray icon
        self.create_tray_icon()
    
        # Show today's tasks by default
        self.update_calendar_format()
        self.show_tasks_for_date(QDate.currentDate())

    def get_data_file_path(self):
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_dir, "calendar_data.json")

    def update_calendar_format(self):
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        important_format = QTextCharFormat()
        important_format.setBackground(QBrush(QColor(255, 200, 200))) # Light red background for important tasks

        regular_format = QTextCharFormat()
        regular_format.setBackground(QBrush(QColor(255, 255, 150))) # Light yellow background for regular tasks

        # go through all dates with tasks
        for date_str in self.tasks:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")

            format = QTextCharFormat()

            has_important = date_str in self.important_tasks and len(self.important_tasks[date_str]) > 0

            has_regular = False
            if date_str in self.tasks:
                for task in self.tasks[date_str]:
                    if date_str not in self.important_tasks or task not in self.important_tasks[date_str]:
                        has_regular = True
                        break
            
            # set background color based on task types
            if has_important and has_regular:
                format = important_format
            elif has_important:
                format = important_format
            elif has_regular:
                format = regular_format
            
            task_count = len(self.tasks[date_str])
            self.calendar.setToolTip(f"{task_count} task(s)")
            self.calendar.setDateTextFormat(qdate, format)
    
    def save_data(self):
        # Save tasks and important tasks to a JSON file
        data = {
            "tasks": self.tasks,
            "important_tasks": self.important_tasks
        }
        # create the date file path
        data_file = self.get_data_file_path()

        try:
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Data saved to {data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        # Load tasks and important tasks from a JSON file
        data_file = self.get_data_file_path()
        if os.path.exists(data_file):
            try: 
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", {})
                    self.important_tasks = data.get("important_tasks", {})
            except Exception as e:
                print(f"Error loading data: {e}")
                self.tasks = {}
                self.important_tasks = {}
        else:
            print(f"No data file found at {data_file}, starting with empty tasks.")
            self.tasks = {}
            self.important_tasks = {}

    def create_tray_icon(self):
        # Create the tray icon (use your own icon file path)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(
            QApplication.style().SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Calendar", self)
        show_action.triggered.connect(self.show)
        
        hide_action = QAction("Hide Calendar", self)
        hide_action.triggered.connect(self.hide)
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Double-click on tray icon to show/hide app
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def quit_application(self):
        self.save_data()
        QApplication.instance().quit()

    def delete_task(self):
        current_item = self.task_list.currentItem()
        if current_item:
            task_text = current_item.text().replace("★ ", "")  # Remove star if present
            current_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        
            if current_date in self.tasks and task_text in self.tasks[current_date]:
                self.tasks[current_date].remove(task_text)
                if current_date in self.important_tasks and task_text in self.important_tasks[current_date]:
                    self.important_tasks[current_date].remove(task_text)
            
            self.save_data()  # Save tasks to file
            
            self.update_calendar_format()
            self.show_tasks_for_date(self.calendar.selectedDate())
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isHidden():
                self.show()
            else:
                self.hide()
    
    def show_tasks_for_date(self, date):
        self.task_list.clear()
        date_str = date.toString("yyyy-MM-dd")
        if date_str in self.tasks:
            for task in self.tasks[date_str]:
                item = task
                if date_str in self.important_tasks and task in self.important_tasks[date_str]:
                    item = "★ " + task
                self.task_list.addItem(item)
    
    
    def add_task(self):

        if hasattr(self, 'multi_date_mode') and self.multi_date_mode:
            self.finish_multi_date_task()
            return
        
        task_text = self.task_entry.text().strip()
        if task_text:
            current_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
            
            if current_date not in self.tasks:
                self.tasks[current_date] = []
                self.important_tasks[current_date] = []
                
            self.tasks[current_date].append(task_text)

            if self.important_checkbox.isChecked():
                if current_date not in self.important_tasks:
                    self.important_tasks[current_date] = []
                self.important_tasks[current_date].append(task_text)

            self.save_data()  # Save tasks to file
            
            self.update_calendar_format()
            self.show_tasks_for_date(self.calendar.selectedDate())
            self.task_entry.clear()
            self.important_checkbox.setChecked(False)
    

    def closeEvent(self, event):
        self.save_data()

        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Calendar App",
            "Application is still running in the system tray",
            QSystemTrayIcon.Information,
            2000
        )
    
    def add_multi_date_task(self):
        task_text = self.task_entry.text().strip()
        if not task_text:
            return
        
        self.multi_date_mode = True
        self.selected_dates = set()
        self.temp_task = task_text
        self.temp_important = self.important_checkbox.isChecked()
        
        # update UI for multi-date task entry
        self.add_task_button.setText("Finish Multi-Date")
        self.add_multi_date_button.setText("Cancel Multi-Date")
        self.task_entry.setEnabled(False)
        self.important_checkbox.setEnabled(False)

        # change calendar click behavior 
        self.calendar.clicked.disconnect()
        self.calendar.clicked.connect(self.multi_date_click)

        self.setWindowTitle("My Task Calendar - Select Multiple Dates (click dates to select)")

    def multi_date_click(self, date):
        date_str = date.toString("yyyy-MM-dd")
        if date_str in self.selected_dates:
            self.selected_dates.remove(date_str)
        else:
            self.selected_dates.add(date_str)

        # Highlight selected dates
        self.update_multi_date_calendar()
    
    def update_multi_date_calendar(self):
        self.update_calendar_format()

        selected_format = QTextCharFormat()
        selected_format.setBackground(QBrush(QColor(150, 200, 255)))

        for date_str in self.selected_dates:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            self.calendar.setDateTextFormat(qdate, selected_format)
    
    def finish_multi_date_task(self):
        if not self.selected_dates:
            self.cancel_multi_date()
            return

        for date_str in self.selected_dates:
            if date_str not in self.tasks:
                self.tasks[date_str] = []
                self.important_tasks[date_str] = []

            self.tasks[date_str].append(self.temp_task)

            if self.temp_important:
                if date_str not in self.important_tasks:
                    self.important_tasks[date_str] = []
                self.important_tasks[date_str].append(self.temp_task)
        self.save_data()
        self.exit_multi_date_mode()

    def cancel_multi_date(self):
        self.exit_multi_date_mode()
    
    def exit_multi_date_mode(self):
        self.multi_date_mode = False
        self.selected_dates = set()

        # reset UI
        self.add_task_button.setText("Add Task")
        self.add_multi_date_button.setText("Add Multi-Date Task")
        self.task_entry.setEnabled(True)
        self.important_checkbox.setEnabled(True)
        self.task_entry.clear()
        self.important_checkbox.setChecked(False)

        # reset calendar click behavior
        self.calendar.clicked.disconnect()
        self.calendar.clicked.connect(self.show_tasks_for_date)

        # update display
        self.update_calendar_format()
        self.show_tasks_for_date(self.calendar.selectedDate())
        self.setWindowTitle("My Task Calendar")
    

if __name__ == "__main__":
    import signal

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed

    window = CalendarApp()
    
    app.aboutToQuit.connect(window.save_data)  # Save data on exit

    def signal_handler(signum, frame):
        window.save_data()
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    window.show()
    sys.exit(app.exec_())