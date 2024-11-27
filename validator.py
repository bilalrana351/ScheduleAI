
def validate_time_range(wake_up, sleep, obligations, tasks):
    errors = []
    for obligation in obligations:
        if obligation["start"] < wake_up or obligation["end"] > sleep:
            errors.append(f"Obligation '{obligation['task']}' is out of bounds.")
    for task in tasks:
        if task["duration"] > (sleep.hour * 60 + sleep.minute) - (wake_up.hour * 60 + wake_up.minute):
            errors.append(f"Task '{task['task']}' cannot fit within the available time window.")
    return errors

def check_overlaps(obligations):
    errors = []
    sorted_obligations = sorted(obligations, key=lambda x: x["start"])
    for i in range(len(sorted_obligations) - 1):
        current = sorted_obligations[i]
        next_task = sorted_obligations[i + 1]
        if current["end"] > next_task["start"]:
            errors.append(f"Obligations '{current['task']}' and '{next_task['task']}' overlap.")
    return errors

def validate_inputs(data):
    wake_up = data["wake_up_time"]
    sleep = data["sleep_time"]
    obligations = data["obligations"]
    tasks = data["regular_tasks"]

    errors = validate_time_range(wake_up, sleep, obligations, tasks)
    errors.extend(check_overlaps(obligations))

    if not errors:
        return True, None
    return False, errors
