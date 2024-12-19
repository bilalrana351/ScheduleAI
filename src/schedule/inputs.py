import datetime
from scheduler import minutes_between

def get_time(prompt):
    while True:
        try:
            time_input = input(prompt + " (HH:MM, 24-hour format): ")
            time = datetime.datetime.strptime(time_input, "%H:%M").time()
            return time
        except ValueError:
            print("Invalid time format. Please enter in HH:MM format (e.g., 07:30).")

def get_obligations():
    obligations = []
    print("Enter your obligations. Press Enter without inputting a task to stop.")
    while True:
        task = input("Task name: ")
        if not task:
            break
        start_time = get_time(f"Start time for '{task}'")
        end_time = get_time(f"End time for '{task}'")
        if end_time <= start_time:
            print("End time must be after start time. Please re-enter this obligation.")
            continue
        # Added a duration just to have more information, nothing wrong in the code
        # We just use the minutes_between function to calculate the duration
        obligations.append({"task": task, "start": start_time, "end": end_time, "duration": minutes_between(start_time, end_time)})
    return obligations

def get_regular_tasks():
    tasks = []
    print("Enter your regular tasks. Press Enter without inputting a task to stop.")
    while True:
        task = input("Task name: ")
        if not task:
            break
        duration = input(f"Duration for '{task}' in minutes: ")
        if not duration.isdigit() or int(duration) <= 0:
            print("Invalid duration. Please enter a positive number.")
            continue
        tasks.append({"task": task, "duration": int(duration)})
    return tasks

def get_schedule_inputs():
    wake_up_time = get_time("Enter your wake-up time")
    sleep_time = get_time("Enter your sleep time")
    if sleep_time <= wake_up_time:
        print("Sleep time must be after wake-up time. Please ensure a valid schedule.")
        return None

    print("Now let's input your daily obligations:")
    obligations = get_obligations()

    print("Now let's input your regular tasks:")
    regular_tasks = get_regular_tasks()

    return {
        "wake_up_time": wake_up_time,
        "sleep_time": sleep_time,
        "obligations": obligations,
        "regular_tasks": regular_tasks
    }
