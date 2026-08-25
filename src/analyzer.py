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
def reset_activity_history():
    global activity_history
    global previous_activity
    global previous_activity_timestamp

    activity_history = []
    previous_activity = None
    previous_activity_timestamp = datetime.now()
def compared_domain_name_extract(domain_name_extract):
    if domain_name_extract is None:
        return None
    fixed_domain_for_comparison = domain_name_extract.removesuffix(".com")
    fixed_domain_for_comparison = fixed_domain_for_comparison.lower()
    return fixed_domain_for_comparison
def python_determination(goal, current_app, domain_name_extract):
    fixed_domain = compared_domain_name_extract(domain_name_extract)
    goal = goal.lower()
    split_goal = goal.split()
    current_app = current_app.lower()
    for items in split_goal:
        if items == fixed_domain:
            return "productive"
        elif items == current_app:
            return "productive"
    return None
def analyze_session(session_data):
    local_decisions = []
    unresolved_activities = []
    history = unresolved_activities
    goal = session_data["session_goal"]
    for segment in activity_history:
        activity_id = segment["activity_id"]
        current_app = segment["Activity"][0]
        domain_name_extract = segment["Activity"][1]
        python_result = python_determination(
            goal,
            current_app,
            domain_name_extract
        )
        if python_result == "productive":
            local_decisions.append({
                "activity_id": activity_id,
                "classification": python_result
            })
        else:
            unresolved_activities.append(segment)
    print("LOCAL:", local_decisions)
    print("SENT TO OLLAMA:", history)
    #productivity_score = session_data["productivity_score1"]
    prompt = f"""
    The user's goal for the session was: {goal}
    The history, of every action the user performed in their session is: {history}.
    TASK:
    Classify every activity as either "productive" or "unproductive"
    based ONLY on whether it directly contributes to the user's stated goal.

    STRICT RULES:
    - Do not judge an app or website by whether it is generally productive.
    - Do not invent hypothetical connections between an activity and the goal.
    - Use only the app, website, tab title, window title, and stated goal as evidence.
    - If there is not clear evidence that an activity contributes to the goal,
    classify it as "unproductive".
    - Preserve every activity_id exactly.
    - Include every activity_id exactly once.
    - Do not calculate scores, percentages, or durations.

    GOAL MATCHING PRIORITY:

    First determine whether the user's goal explicitly names an application,
    website, or activity.

    If the stated goal directly names a website or application, activity on that
    website/application satisfies the goal unless there is explicit evidence that
    it does not.

    Examples:

    Goal: "watch YouTube"
    Any activity on youtube.com = productive.

    Goal: "browse Reddit"
    Any activity on reddit.com = productive.

    Goal: "work in Python"
    Activity in the Python/code editor = productive.

    Do NOT judge whether the content itself is normally productive when using the
    named application or website is itself the user's stated goal.

    Only use tab titles and window titles to determine relevance when the goal
    requires more specific context.

    Example:
    Goal: "study quadratics"
    youtube.com alone is NOT sufficient.
    A YouTube video clearly about quadratics = productive.
    An unrelated entertainment video = unproductive.

    RETURN ONLY VALID JSON IN EXACTLY THIS FORMAT:

    {{
        "activities": [
            {{
                "activity_id": 1,
                "classification": "productive"
            }}
        ]
    }}
    """
    data = {
    "model": "gemma3:latest",
     "keep_alive": -1,
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
    analysis["activities"].extend(local_decisions)
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
def unproductive_formula(analysis):
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
    unproductive = unproductive_formula(analysis)
    total_active = productive + unproductive
    if total_active == 0:
        percentage = 0
    else:
        percentage = productive / total_active * 100
    print(analysis["activities"])
    return round(percentage, 1)