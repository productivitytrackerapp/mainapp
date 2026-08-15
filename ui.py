import session
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QPlainTextEdit
from PyQt6.QtCore import QTimer, QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QLabel, QLineEdit
import sys
class TrackerWorker(QObject):
    tick_finished = pyqtSignal()
    duration_update = pyqtSignal(float)
    session_report = pyqtSignal(object)
    def run_tick(self):
        report = session.process_tracker_tick()
        duration = report["duration"]
        self.duration_update.emit(duration)
        if session.stop_requested == True:
            self.session_report.emit(report)
        self.tick_finished.emit()
app = QApplication(sys.argv)

window = QWidget()
timer = QTimer()
timer.setSingleShot(True)

tracker_thread = QThread()
tracker_worker = TrackerWorker()
tracker_worker.moveToThread(tracker_thread)
timer.timeout.connect(tracker_worker.run_tick)
tracker_thread.start()
def on_tick_finish():
    if session.stop_requested:
        timer.stop() 
    else:
        timer.start(500)
def format_duration(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{hours:02}:{minutes:02}:{int(seconds):02}"
def print_duration(duration):
    duration = str(duration)
    duration_clock.setText("Duration: " + duration)
def print_report(session_report):
    print(session_report)
    report_box.show()
    duration_clock.hide()
    start_button.hide()
    end_button.hide()
    formatted_duration = format_duration(session_report["duration"])
    formatted_idle = format_duration(session_report["time_spent_idle"])
    apps = session_report["most_frequented_apps"]
    websites = session_report["most_frequented_websites"]
    report = f"Duration: {formatted_duration}\nIdle Time: {formatted_idle}\n\nMost frequented Apps:\n"
    for app, seconds in apps.items():
        formatted_app = format_duration(seconds)
        report += f"{app}: {formatted_app}\n"
    report += "\nMost frequented Websites:\n"
    for website, seconds in websites.items(): 
        formatted_website = format_duration(seconds)
        report += f"{website}: {formatted_website}\n"
    report_box.setPlainText(report) 
tracker_worker.duration_update.connect(print_duration)
live_duration = "Duration: 0"
duration_clock = QLabel(live_duration)
report_box = QPlainTextEdit()
report_box.hide()
layout = QVBoxLayout()
start_button = QPushButton("Start session", window)
goal_input = QLineEdit()
def handle_start():
    goal = goal_input.setReadOnly(True)
    goal = goal_input.text()
    goal_input.hide()
    session.start_session(goal)
    start_button.setEnabled(False)
    end_button.setEnabled(True)
    timer.start(500)
start_button.clicked.connect(handle_start)
end_button = QPushButton("End session", window)
end_button.clicked.connect(session.end_session)
end_button.setEnabled(False)
tracker_worker.session_report.connect(print_report)
tracker_worker.tick_finished.connect(on_tick_finish)
layout.addWidget(duration_clock)
layout.addWidget(start_button)  
layout.addWidget(end_button)
layout.addWidget(report_box)
layout.addWidget(goal_input)
window.setLayout(layout)
window.show()
app.exec()