import sys
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QCalendarWidget, 
                             QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, 
                             QAction, QListWidget, QHBoxLayout, QPushButton, 
                             QLineEdit, QInputDialog, QCheckBox)
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
        
        # Task entry and add button
        task_entry_layout = QVBoxLayout()
        self.task_entry = QLineEdit()
        self.task_entry.setPlaceholderText("Enter new task...")
        self.important_checkbox = QCheckBox("Important")
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_task)
        
        task_entry_layout.addWidget(self.task_entry)
        task_entry_layout.addWidget(self.important_checkbox)
        task_entry_layout.addWidget(self.add_task_button)
        
        # Task side layout
        task_side_layout = QVBoxLayout()
        task_side_layout.addWidget(self.task_list)
        task_side_layout.addLayout(task_entry_layout)
        
        # Add widgets to main layout
        main_layout.addWidget(self.calendar, 2)
        main_layout.addLayout(task_side_layout, 1)
        
        # Dictionary to store tasks by date
        self.tasks = {}
        self.important_tasks = {}
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Show today's tasks by default
        self.update_calendar_format()
        self.show_tasks_for_date(QDate.currentDate())

    def update_calendar_format(self):
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        important_format = QTextCharFormat()
        important_format.setBackground(QBrush(QColor(255, 200, 200))) # Light red background for important tasks

        # go through all dates with tasks
        for date_str in self.tasks:
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")

            format = QTextCharFormat()

            if date_str in self.important_tasks and self.important_tasks[date_str]:
                format = important_format
            
            current_format = self.calendar.dateTextFormat(qdate)
            task_count = len(self.tasks[date_str])

            if not current_format.isValid():
                self.calendar.setDateTextFormat(qdate, format)

            self.calendar.setToolTip(f"{task_count} task(s)")

            self.calendar.setDateTextFormat(qdate, format)
    
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
        quit_action.triggered.connect(QApplication.quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Double-click on tray icon to show/hide app
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
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
            
            self.update_calendar_format()
            self.show_tasks_for_date(self.calendar.selectedDate())
            self.task_entry.clear()
            self.important_checkbox.setChecked(False)
    
    def closeEvent(self, event):
        # Hide instead of close when X is clicked
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Calendar App",
            "Application is still running in the system tray",
            QSystemTrayIcon.Information,
            2000
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed
    window = CalendarApp()
    window.show()
    sys.exit(app.exec_())