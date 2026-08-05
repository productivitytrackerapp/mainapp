import datetime
import time
from urllib.parse import urlparse
import subprocess
import json
import Quartz
import tldextract
from pynput import keyboard
from pynput.keyboard import Key, Controller
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QPlainTextEdit
from PyQt6.QtCore import QTimer, QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QLabel
import sys
# Helper functions
stop_requested = False
website_totals = {}
previous_domain = None
timer_paused = False
app_totals = {}
previous_app = None
app_timer_paused = False

# Determining wether or not the user is idle. Stating a timer to count the time user has spent idle. Formula for calculating the users total time spent idle. 
def end_domain():
    domain_time = time.perf_counter()
    return domain_time

end_domain_time = end_domain()

def end_app():
    app_time = time.perf_counter()
    return app_time

end_app_time = end_app()

def start_app():
    start_app_time = time.perf_counter()
    return start_app_time

start_app_time = start_app()

def start_domain():
    domain_time = time.perf_counter()
    return domain_time

start_domain_time = start_domain()

def website_time():
    total_website_time = end_domain_time - start_domain_time
    return total_website_time

total_website_time = website_time()
quit_key = "="
# Determining wether or not the user is idle. Stating a timer to count the time user has spent idle. Formula for calculating the users total time spent idle. 
# Function to start counting, used to count the duration once a session is started.
def duration_start():
    start_time = time.perf_counter()
    return start_time

# The amount of time in seconds before a user is considered idle. 2 minutes and 35 seconds in this case.
IDLE_LIMIT = 155    
# The idle_time_list is used to store the time spent idle in a list. A sum function is used on line 190 to calculate all idle sessions stored in idle_time_list into one number.
idle_time_list = []

def find_idle_state():
    return Quartz.CGEventSourceSecondsSinceLastEventType(
        Quartz.kCGEventSourceStateCombinedSessionState,
        Quartz.kCGAnyInputEventType
    )

def idle_or_not():
    idle_time = find_idle_state()
    if idle_time >= IDLE_LIMIT:
        is_idle = True
    else:
        is_idle = False
    return is_idle

idle_state = idle_or_not()

def idle_false_to_true():
    start_idle_counter = time.perf_counter()
    return start_idle_counter

def idle_time_calculation(start_count, end_count):
    idle_time = (end_count - start_count)
    return idle_time

def idle_true_to_false():
    end_idle_count = time.perf_counter()
    return end_idle_count

def idle_time_calculation_via_quit():
    idle_time = final_idle_count - start_idle_counter
    return idle_time

idle_state = idle_or_not()
previous_idle_state1 = idle_state

def on_press(key):
    try:
        if key.char == quit_key:
            global stop_requested
            stop_requested = True
    except AttributeError:
        pass

# Modularized helper functions extracted from loop
def duration_end():
    end_time = time.perf_counter()
    return end_time

def duration_total(start_time, end_time):
    session_length = (end_time - start_time)
    return session_length

def get_Applescript_URL(script):
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output = True,
        text = True
    )
    return result.stdout.strip()

def get_frontmost_app():
    script = '''
    tell application "System Events"
        get name of first application process whose frontmost is true
    end tell
    '''
    return get_Applescript_URL(script)

def get_current_tab_URL():
    current_app = get_frontmost_app()
    if current_app == "Safari":
        script = 'tell application "Safari" to get URL of current tab of front window'
    elif current_app == "Google Chrome":
        script = 'tell application "Google Chrome" to get URL of active tab of front window'
    else:
        return None
    return get_Applescript_URL(script)

def domain_name(url_title):
    url = url_title
    if url == None:
        return None
    else:
        ext = tldextract.extract(url)
        print(ext.top_domain_under_public_suffix)
        return ext.top_domain_under_public_suffix

def get_Applescript(script):
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output = True,
        text = True
    )
    return result.stdout.strip()

def get_current_tab_title():
    current_app = get_frontmost_app()
    if current_app == "Safari":
        script = 'tell application "Safari" to get name of current tab of front window'
    elif current_app == "Google Chrome":
        script = 'tell application "Google Chrome" to get title of active tab of front window'
    else:
        return None
    return get_Applescript(script)

def get_Applescript_APP(script):
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output = True,
        text = True
    )
    return result.stdout.strip()

def get_Applescript_TITLE(script):
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output = True,
        text = True
    )
    return result.stdout.strip()

def get_frontmost_title():
    script = '''
    tell application "System Events" to return name of window 1 of (first application process whose frontmost is true)
    '''
    return get_Applescript_TITLE(script)

def time_stamp():
    date_time = datetime.datetime.now()
    now = date_time.strftime("%Y-%m-%d %H:%M:%S")
    return now

def process_tracker_tick():
    global previous_idle_state1, previous_domain, start_domain_time, timer_paused
    global previous_app, start_app_time, app_timer_paused, website_totals, app_totals
    global start_idle_counter, end_idle_count, final_idle_count

    # Start the session: Begin counting the time the user is spending in a session.
    # Additional delay
    # End the session: Stop counting the time the user has spent in a session.
    end_time = duration_end()

    # Calculate the total time spent in a session by subtracting the start_time by the end_time
    session_length = round(duration_total(start_time, end_time), 2)

    # URL Tracking
    url_title = get_current_tab_URL()
    # Extract Domain from URL
    domain_name_extract = domain_name(url_title)
    # Find Tab name
    tab_title = get_current_tab_title()

    # Find App Name
    current_app = get_frontmost_app()    
    # Find window title.
    get_title = get_frontmost_title()

    # Calculate the current time stamp when run.
    date_time_function = time_stamp()

    user_current_idle_state = idle_state
    idle_started_at = None
    # Calculating time spent idle:
    current_idle_state = idle_or_not()
    if current_idle_state != previous_idle_state1:
        if current_idle_state == True:
            start_idle_counter = idle_false_to_true()
        elif current_idle_state == False:
            end_idle_count = idle_true_to_false()
            idle_time = idle_time_calculation(start_idle_counter, end_idle_count)
            idle_time_list.append(idle_time)
    total_idle_time = round(sum(idle_time_list), 2)

    # Calculating Idle Website  
    if domain_name_extract != previous_domain:
        end_domain_time = end_domain()
        website_spent = round((end_domain_time - start_domain_time), 2)
        if previous_domain is not None:
            if previous_domain not in website_totals:
                website_totals[previous_domain] = website_spent
            else:
                website_totals[previous_domain] += website_spent
        previous_domain = domain_name_extract
        start_domain_time = end_domain_time

    if domain_name_extract is not None:
        if current_idle_state == True and current_idle_state != previous_idle_state1:
            timestamp = time.perf_counter()
            active_interval = (timestamp - start_domain_time)
            if domain_name_extract not in website_totals:
                website_totals[domain_name_extract] = active_interval
            else:
                website_totals[domain_name_extract] += active_interval

            timer_paused = True
        else:
            pass

    if domain_name_extract is not None:
        if current_idle_state == False and current_idle_state != previous_idle_state1:
            start_timestamp = time.perf_counter()
            start_domain_time = start_timestamp
            timer_paused = False

    # Calculating Idle App
    if current_app != previous_app:
        end_app_time = end_app()
        app_spent = round((end_app_time - start_app_time), 2)
        if previous_app is not None:
            if previous_app not in app_totals:
                app_totals[previous_app] = app_spent
            else:
                app_totals[previous_app] += app_spent
        previous_app = current_app
        start_app_time = end_app_time

    if current_app is not None:
        if current_idle_state == True and current_idle_state != previous_idle_state1:
            timestamp = time.perf_counter()
            active_interval = (timestamp - start_app_time)
            if current_app not in app_totals:
                app_totals[current_app] = active_interval
            else:
                app_totals[current_app] += active_interval

            app_timer_paused = True
        else:
            pass

    if current_app is not None:
        if current_idle_state == False and current_idle_state != previous_idle_state1:
            start_timestamp = time.perf_counter()
            start_app_time = start_timestamp
            app_timer_paused = False

    # Stop Requests
    if stop_requested == True:
        if previous_domain:
            if timer_paused == False:
                end_domain_time = end_domain()
                website_spent = round((end_domain_time - start_domain_time), 2)
                if previous_domain not in website_totals:
                    website_totals[previous_domain] = website_spent
                else:
                    website_totals[previous_domain] += website_spent

    if stop_requested == True:
        if current_idle_state == True:
            final_idle_count = time.perf_counter()
            idle_time = idle_time_calculation_via_quit()
            idle_time_list.append(idle_time)
            session_length = round(duration_total(start_time, final_idle_count), 2)
            total_idle_time = round(sum(idle_time_list), 2)
        else:
            final_idle_count = time.perf_counter()
            session_length = round(duration_total(start_time, final_idle_count), 2)
            total_idle_time = round(sum(idle_time_list), 2)

    # App Stop Requests
    if stop_requested == True:
        if previous_app:
            if app_timer_paused == False:
                end_app_time = end_app()
                app_spent = round((end_app_time - start_app_time), 2)
                if previous_app not in app_totals:
                    app_totals[previous_app] = app_spent
                else:
                    app_totals[previous_app] += app_spent
    app_totals = dict(sorted(app_totals.items(), key=lambda item: item[1], reverse=True))
    website_totals = dict(sorted(website_totals.items(), key=lambda item: item[1], reverse=True))
    previous_idle_state1 = current_idle_state
    productivity = {
        "duration": session_length,
        "time_spent_idle": total_idle_time,
        "most_frequented_websites": website_totals,
        "most_frequented_apps": app_totals,
    }
    with open("output.json", "w") as f:
        json.dump(productivity, f, indent=4)
    return productivity
#should_session_start = False
#should_session_start = input("Print Yes to start your session, Print No to not.")
#targetLetters = "yes"
#contains_letter = targetLetters.lower() in should_session_start.lower()
#
#if contains_letter == True:
#    should_session_start = True
#    start_time = duration_start()
#    listener = keyboard.Listener(on_press=on_press)
#    listener.start()
#
#if should_session_start == True:
#   while True:
#        process_tracker_tick()
#        if stop_requested == True:
#            break
#else:
#    pass

class TrackerWorker(QObject):
    tick_finished = pyqtSignal()
    duration_update = pyqtSignal(float)
    session_report = pyqtSignal(object)
    def run_tick(self):
        report = process_tracker_tick()
        duration = report["duration"]
        self.duration_update.emit(duration)
        if stop_requested == True:
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
def start_session():
    global start_time
    global website_totals
    global app_totals
    global idle_time_list
    global stop_requested
    global previous_app
    global previous_domain
    global start_app_time
    global start_domain_time
    global previous_idle_state1
    global timer_paused
    global app_timer_paused
    global start_idle_counter
    global end_idle_count
    global final_idle_count
    start_time = duration_start()
    website_totals = {}
    app_totals = {}
    idle_time_list = []
    stop_requested = False
    previous_app = None
    previous_domain = None
    start_app_time = start_app()
    start_domain_time = start_domain()
    previous_idle_state1 = idle_or_not()
    timer_paused = previous_idle_state1
    app_timer_paused = previous_idle_state1
    start_idle_counter = None
    end_idle_count = None
    final_idle_count = None
    timer.start(500)
def on_tick_finish():
    if stop_requested:
        timer.stop() 
    else:
        timer.start(500)
def format_duration(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{hours:02}:{minutes:02}:{int(seconds):02}"
def end_session():
    global stop_requested
    stop_requested = True
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
start_button.clicked.connect(start_session)
end_button = QPushButton("End session", window)
end_button.clicked.connect(end_session)
tracker_worker.session_report.connect(print_report)
tracker_worker.tick_finished.connect(on_tick_finish)
layout.addWidget(duration_clock)
layout.addWidget(start_button)
layout.addWidget(end_button)
layout.addWidget(report_box)
window.setLayout(layout)
window.show()
app.exec()