import time
import json
import analyzer
import datetime
from tracker import get_current_tab_URL, domain_name, get_current_tab_title, get_frontmost_app, get_frontmost_title, idle_or_not
stop_requested = False
website_totals = {}
previous_domain = None
timer_paused = False
app_totals = {}
previous_app = None
app_timer_paused = False
idle_time_list = []
current_goal = None
def start_session(goal):
    global start_time
    global website_totals
    global app_totals
    global idle_time_list
    global stop_requested
    global current_goal
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
    current_goal = goal
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
def time_stamp():
    date_time = datetime.datetime.now()
    now = date_time.strftime("%Y-%m-%d %H:%M:%S")
    return now
def end_session():
    global stop_requested
    stop_requested = True
def start_domain():
    domain_time = time.perf_counter()
    return domain_time
def idle_false_to_true():
    start_idle_counter = time.perf_counter()
    return start_idle_counter
def idle_true_to_false():
    end_idle_count = time.perf_counter()
    return end_idle_count
def idle_time_calculation_via_quit():
    idle_time = final_idle_count - start_idle_counter
    return idle_time
def end_domain():
    domain_time = time.perf_counter()
    return domain_time
def end_app():
    app_time = time.perf_counter()
    return app_time
def start_app():
    start_app_time = time.perf_counter()
    return start_app_time
def duration_start():
    start_time = time.perf_counter()
    return start_time
def duration_end():
    end_time = time.perf_counter()
    return end_time
def duration_total(start_time, end_time):
    session_length = (end_time - start_time)
    return session_length
def idle_time_calculation(start_count, end_count):
    idle_time = (end_count - start_count)
    return idle_time
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
    current_activity = (
    current_app,
    domain_name_extract,
    tab_title,
    get_title,
    current_idle_state)

    productivity = {
        "duration": session_length,
        "time_spent_idle": total_idle_time,
        "most_frequented_websites": website_totals,
        "most_frequented_apps": app_totals,
        "session_goal": current_goal,
    }
    analyzer.recorded_activity(current_activity)
    if stop_requested == True:
        analysis = analyzer.analyze_session(productivity)
        productivity["analysis"] = analysis
    with open("output.json", "w") as f:
        json.dump(productivity, f, indent=4)
    return productivity