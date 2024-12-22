import datetime

def validate_time_range(wake_up, sleep, obligations, tasks, rest_time):
    errors = []
    wake_up_minutes = wake_up.hour * 60 + wake_up.minute
    sleep_minutes = sleep.hour * 60 + sleep.minute

    for obligation in obligations:
        start_minutes = obligation["start"].hour * 60 + obligation["start"].minute
        end_minutes = obligation["end"].hour * 60 + obligation["end"].minute
        if start_minutes < wake_up_minutes or end_minutes > sleep_minutes:
            errors.append(f"Obligation '{obligation['task']}' is out of bounds.")

    for task in tasks:
        if task["duration"] > sleep_minutes - wake_up_minutes:
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

    errors = validate_time_range(wake_up, sleep, obligations, tasks, data.get("rest_time", 0))
    errors.extend(check_overlaps(obligations))

    if not errors:
        return True, None
    return False, errors

def find_available_slot(tasks, obligations, task_to_schedule, wake_up, sleep, rest_time):
    wake_up_minutes = wake_up.hour * 60 + wake_up.minute
    sleep_minutes = sleep.hour * 60 + sleep.minute

    def is_valid_schedule(schedule):
        for i in range(len(schedule) - 1):
            current = schedule[i]
            next_task = schedule[i + 1]
            if current["end"] + datetime.timedelta(minutes=rest_time) > next_task["start"]:
                return False
        return True

    def backtrack(schedule, task):
        for start_minutes in range(wake_up_minutes, sleep_minutes - task["duration"] + 1):
            task_start = datetime.time(start_minutes // 60, start_minutes % 60)
            task_end_minutes = start_minutes + task["duration"]
            task_end = datetime.time(task_end_minutes // 60, task_end_minutes % 60)

            task["start"] = task_start
            task["end"] = task_end

            new_schedule = sorted(schedule + [task], key=lambda x: x["start"])

            if is_valid_schedule(new_schedule):
                return new_schedule
        return None

    return backtrack(obligations + tasks, task_to_schedule)

def handle_conflict(obligations, tasks, task_to_schedule, wake_up, sleep, rest_time):
    for obligation in obligations:
        if (task_to_schedule["start"] < obligation["end"] + datetime.timedelta(minutes=rest_time) and
                task_to_schedule["end"] > obligation["start"]):
            print(f"Conflict with task: {obligation['task']} from {obligation['start']} to {obligation['end']}.")
            user_input = input("Do you want to replace this task? (yes/no): ").strip().lower()

            if user_input == "yes":
                obligations.remove(obligation)
                new_schedule = find_available_slot(tasks, obligations, obligation, wake_up, sleep, rest_time)
                if new_schedule:
                    obligations.append(task_to_schedule)
                    return new_schedule
                else:
                    print("Unable to reschedule the conflicting task.")
                    obligations.append(obligation)  
            else:
                print("Task not replaced.")
                return None

    return obligations
