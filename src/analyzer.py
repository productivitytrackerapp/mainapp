import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from datetime import datetime
previous_activity = None
previous_activity_timestamp = datetime.now()
activity_history = []
def recorded_activity(activity):
    global previous_activity_timestamp
    global previous_activity
    if activity != previous_activity:
        if previous_activity == None:
            previous_activity = activity
            previous_activity_timestamp = datetime.now()
        else:
            current_time = datetime.now()
            elapsed = current_time - previous_activity_timestamp
            elapsed = elapsed.total_seconds()
            activity_ID = len(activity_history) + 1
            history = {"Activity": previous_activity, "Time Spent": elapsed, "activity_id": activity_ID}
            activity_history.append(history)
            previous_activity = activity
            previous_activity_timestamp = datetime.now()
def analyze_session(session_data):
    history = activity_history
    goal = session_data["session_goal"]
    duration = session_data["duration"]
    time_spent_idle = session_data["time_spent_idle"]
    most_frequented_websites = session_data["most_frequented_websites"]
    most_frequented_apps = session_data["most_frequented_apps"]
    #productivity_score = session_data["productivity_score1"]
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

    Return ONLY valid JSON.

    The JSON must have EXACTLY this structure:

    {{
    "activities": [
        {{
        "activity_id": 1,
        "classification": "productive"
        }}
    ],
    "classification": "Productive",
    "reason": "Brief explanation",
    "productive_activities": [],
    "unproductive_activities": []
    }}
    RULES FOR "activities":
    - Include exactly one object for EVERY activity segment provided in the activity history.
    - Preserve each activity_id exactly as provided.
    - Do not create new activity_ids.
    - Do not omit any activity_ids.
    - Each activity_id must appear exactly once.
    - "classification" for each activity MUST be exactly one of:
    - "productive"
    - "unproductive"
    - Do not return durations. Python will calculate durations separately.
    - Judge each activity only relative to the user's stated session goal.

    RULES FOR THE OVERALL "classification":
    - It must be a string.
    - It must be exactly one of:
    - "Highly Productive"
    - "Productive"
    - "Mixed"
    - "Unproductive"
    - "Highly Unproductive"

    RULES FOR "productive_activities" AND "unproductive_activities":
    - These must be JSON arrays.
    - They may contain short descriptions of the relevant activities.

    IMPORTANT:
    - Do not calculate a productivity percentage.
    - Do not calculate productive or unproductive seconds.
    - Do not estimate or invent time values.
    - Do not wrap the response in markdown or ```json code fences.
    - Do not include any text before or after the JSON object.
    """
    data = {
    "model": "gemma3:latest",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "stream": False,
    "format": "json"
    }
    request_body = json.dumps(data).encode("utf-8")
    ollama_request = Request(
        "http://localhost:11434/api/chat",
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
        )
    
    try:
        with urlopen(ollama_request, timeout=120) as response:
            response_data = json.load(response)
    except HTTPError as error:
        error_message = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Ollama returned HTTP {error.code}: {error_message}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            "Could not connect to Ollama at http://localhost:11434"
        ) from error
    ollama_reply = response_data["message"]["content"]
    ollama_reply = ollama_reply.strip()
    ollama_reply = ollama_reply.removeprefix("```json")
    ollama_reply = ollama_reply.removesuffix("```")
    ollama_reply = ollama_reply.strip()
    try:
        analysis = json.loads(ollama_reply)
    except:
        raise ValueError
    print(analysis.keys())
    return analysis
def productivity_formula_func(analysis):
    productive_time = 0
    for item in analysis["activities"]:
        activity_id = item["activity_id"]
        classification = item["classification"]
        if classification == "productive":
            for segment in activity_history:
                if segment["activity_id"] == activity_id:
                    productive_time += segment["Time Spent"]
    return productive_time
def unproductive_forumla(analysis):
    unproductive_time = 0
    for item in analysis["activities"]:
        activity_id = item["activity_id"]
        classification = item["classification"]
        if classification == "unproductive":
            for segment in activity_history:
                if segment["activity_id"] == activity_id:
                    unproductive_time += segment["Time Spent"]
    return unproductive_time
def productive_unproductive_formula(analysis):
    productive = productivity_formula_func(analysis)
    unproductive = unproductive_forumla(analysis)
    total_active = productive + unproductive
    if total_active == 0:
        percentage = 0
    else:
        percentage = productive / total_active * 100
    print(analysis["activities"])
    return round(percentage, 1)

