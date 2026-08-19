import subprocess
import tldextract
from idle_state import find_idle_state

IDLE_LIMIT = 155
def get_Applescript_URL(script):
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output = True,
        text = True
    )
    return result.stdout.strip()

def get_Applescript(script):
    result = subprocess.run(
        ['osascript', '-e', script],
        capture_output = True,
        text = True
    )
    return result.stdout.strip()

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
def get_current_tab_title():
    current_app = get_frontmost_app()
    if current_app == "Safari":
        script = 'tell application "Safari" to get name of current tab of front window'
    elif current_app == "Google Chrome":
        script = 'tell application "Google Chrome" to get title of active tab of front window'
    else:
        return None
    return get_Applescript(script)
def get_frontmost_title():
    script = '''
    tell application "System Events" to return name of window 1 of (first application process whose frontmost is true)
    '''
    return get_Applescript_TITLE(script)
def idle_or_not():
    idle_time = find_idle_state()
    if idle_time >= IDLE_LIMIT:
        is_idle = True
    else:
        is_idle = False
    return is_idle

idle_state = idle_or_not()
get_the_current_tab_URL = get_current_tab_URL()
get_the_current_tab_title = get_current_tab_title()
get_the_frontmost_title = get_frontmost_title()