import json
import tracker
import requests
def analyze_session(session_data):
    print("analyze_session was called")
    print(session_data)
previous_activity = None
activity_history = []
def recorded_activity(activity):
    global previous_activity
    if activity != previous_activity:
        activity_history.append(activity)
        print(activity_history)
        previous_activity = activity
def analyze_session(session_data):
    history = activity_history
    goal = session_data["session_goal"]
    duration = session_data["duration"]
    time_spent_idle = session_data["time_spent_idle"]
    most_frequented_websites = session_data["most_frequented_websites"]
    most_frequented_apps = session_data["most_frequented_apps"]
    prompt = f"""
    The user's goal for the session was: {goal}
    The user's most frequented websites were: {most_frequented_websites}
    The user's most frequented apps were: {most_frequented_apps}
    The user spent {time_spent_idle} seconds idle.
    The session lasted {duration} seconds.
    The history, of every action the user performed in their session is: {history}.
    ROLE:
    You are evaluating whether a computer productivity session
    was productive relative to the user's stated goal.

    TASK:
    Evaluate the session and assign a productivity score from 0-100.

    SCORING:
    100 = session activity was almost entirely relevant to the goal
    75 = mostly productive with minor distractions
    50 = mixed productive and unproductive activity
    25 = mostly unrelated activity
    0 = no meaningful activity related to the goal

    IMPORTANT:
    Judge websites and applications relative to the user's goal.
    Do not assume that an app or website is inherently productive
    or unproductive.

    Consider:
    - relevance of apps to the goal
    - relevance of websites to the goal
    - idle time relative to total duration
    - amount of time spent on each activity
    - activity/window/tab context when available

    RETURN:
    Return only structured JSON with:
    productivity_score
    classification
    reason
    productive_activities
    unproductive_activities
    """
    data = {
    "model": "gemma3:latest",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "stream": False
    }
    response = requests.post(
        "http://localhost:11434/api/chat",
        json = data
    )
    response_data = response.json()
    print(response_data["message"]["content"])