from datetime import datetime, timedelta
from src.validators.scheduler import minutes_between
from src.core.helpers import get_time_to_preference, adjust_wakeup_and_sleep

def get_smallest_duration(tasks):
    """Get the smallest task duration from the list of tasks."""
    return min(task["duration"] for task in tasks)

def create_intervals(timeline, interval_size):
    """Create fixed-size intervals from the available timeline."""
    intervals = []
    for slot in timeline:
        current_time = slot["start"]
        while current_time < slot["end"]:
            end_time = (datetime.combine(datetime.today(), current_time) + 
                       timedelta(minutes=interval_size)).time()
            
            # If this interval would extend beyond the slot, cap it
            if end_time > slot["end"]:
                end_time = slot["end"]
            
            if current_time < end_time:  # Only add if there's actual time in the interval
                intervals.append({
                    "start": current_time,
                    "end": end_time,
                    "duration": minutes_between(current_time, end_time),
                    "assigned": False
                })
            
            current_time = end_time
    return intervals

def get_intervals_by_preference(intervals, preference):
    """Filter intervals based on time preference."""
    if not preference:
        return intervals
    
    return [interval for interval in intervals 
            if get_time_to_preference(interval["start"]) == preference.lower()]

def can_schedule_task(intervals, task_duration, start_idx):
    """Check if a task can be scheduled starting from a given interval."""
    remaining_duration = task_duration
    idx = start_idx
    
    while remaining_duration > 0 and idx < len(intervals):
        if not intervals[idx]["assigned"]:
            remaining_duration -= intervals[idx]["duration"]
        else:
            return False
        idx += 1
    
    return remaining_duration <= 0

def schedule_task_in_intervals(intervals, task, start_idx):
    """Schedule a task across intervals starting from a given index."""
    remaining_duration = task["duration"]
    scheduled_parts = []
    idx = start_idx
    
    while remaining_duration > 0 and idx < len(intervals):
        interval = intervals[idx]
        if interval["assigned"]:
            break
            
        duration_to_use = min(remaining_duration, interval["duration"])
        end_time = (datetime.combine(datetime.today(), interval["start"]) + 
                   timedelta(minutes=duration_to_use)).time()
        
        scheduled_parts.append({
            "task": task["task"],
            "start": interval["start"],
            "end": end_time,
            "duration": duration_to_use
        })
        
        interval["assigned"] = True
        remaining_duration -= duration_to_use
        idx += 1
    
    return scheduled_parts

def interval_schedule(wake_up, sleep, obligations, tasks):
    """
    Schedule tasks using interval-based algorithm with preference support.
    Tasks can be split across intervals if needed.
    
    Returns:
        dict: A dictionary containing:
            - 'tasks': List of scheduled tasks with start and end times
            - 'preference_respected': Boolean indicating if preferences were respected
    """
    # Create initial timeline
    timeline = adjust_wakeup_and_sleep(wake_up, sleep)

    
    # Process obligations
    for obligation in sorted(obligations, key=lambda x: x["start"]):
        new_timeline = []
        for slot in timeline:
            if slot["start"] < obligation["start"] < slot["end"]:
                new_timeline.append({"start": slot["start"], "end": obligation["start"]})
            if slot["start"] < obligation["end"] < slot["end"]:
                new_timeline.append({"start": obligation["end"], "end": slot["end"]})
            if obligation["end"] <= slot["start"] or obligation["start"] >= slot["end"]:
                new_timeline.append(slot)
        timeline = new_timeline
    
    # If there are no task then just add them transparently
    if len(tasks) == 0:
        return {
            "tasks": [],
            "preference_respected": True,
            "found_schedule": True
        }
    
    # Get smallest duration for interval size
    try:
        interval_size = get_smallest_duration(tasks)
    except Exception as e:
        return {
            "tasks": [],
            "preference_respected": True,
            "found_schedule": False
        }
    
    # Create fixed-size intervals
    intervals = create_intervals(timeline, interval_size)

    
    # Sort tasks by preference order (morning -> afternoon -> evening -> night -> no preference)
    preference_order = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3, "none": 4}
    
    # To handle the case where the preference is not defined
    sorted_tasks = sorted(tasks, 
                        key=lambda x: (preference_order.get(x.get("preference") or "none"), -x["duration"]))
    
    scheduled_tasks = []
    all_preferences_respected = True
    
    # Try to schedule each task
    for task in sorted_tasks:
        task_scheduled = False
        preference = task.get("preference")
        
        # First try to schedule in preferred time slots
        if preference:
            preferred_intervals = get_intervals_by_preference(intervals, preference)
            
            # Try each possible starting interval
            for i in range(len(preferred_intervals)):
                if can_schedule_task(intervals, task["duration"], i):
                    scheduled_parts = schedule_task_in_intervals(intervals, task, i)
                    scheduled_tasks.extend(scheduled_parts)
                    task_scheduled = True
                    break
            
            if not task_scheduled:
                all_preferences_respected = False
        
        # If task couldn't be scheduled in preferred slots (or has no preference),
        # try any available slots
        if not task_scheduled:
            for i in range(len(intervals)):
                if can_schedule_task(intervals, task["duration"], i):
                    scheduled_parts = schedule_task_in_intervals(intervals, task, i)
                    scheduled_tasks.extend(scheduled_parts)
                    task_scheduled = True
                    break
        
        if not task_scheduled:
            return {
                "tasks": [],
                "preference_respected": all_preferences_respected,
                "found_schedule": False
            }
    
    return {
        "tasks": scheduled_tasks,
        "preference_respected": all_preferences_respected,
        "found_schedule": True
    }

def main():
    # Sample wake up and sleep times
    wake_up = datetime.strptime("08:00", "%H:%M").time()
    sleep = datetime.strptime("22:00", "%H:%M").time()

    # Sample obligations
    obligations = [
        {"start": datetime.strptime("12:00", "%H:%M").time(), 
         "end": datetime.strptime("13:00", "%H:%M").time()},
    ]

    # Sample tasks with preferences
    tasks = [
        {"task": "Morning Exercise", "duration": 60, "preference": "morning"},
        {"task": "Study Session", "duration": 120, "preference": "afternoon"},
        {"task": "Reading", "duration": 90, "preference": "evening"},
    ]

    # Run the scheduling algorithm
    result = interval_schedule(wake_up, sleep, obligations, tasks)

    # Print results
    print("\nSchedule for the day:")
    print(f"Wake up time: {wake_up}")
    print(f"Sleep time: {sleep}")
    
    print("\nObligations:")
    for obligation in obligations:
        print(f"- {obligation['start']} to {obligation['end']}")
    
    print("\nScheduled Tasks:")
    if result:
        print(f"All preferences respected: {result['preference_respected']}")
        for task in result["tasks"]:
            print(f"- {task['task']}: {task['start']} to {task['end']} "
                  f"(Duration: {task['duration']} minutes)")
    else:
        print("Could not schedule all tasks!")

if __name__ == "__main__":
    main() 