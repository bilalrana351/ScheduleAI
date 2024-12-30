
from datetime import timedelta, datetime

def minutes_between(start_time, end_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    return int((end_dt - start_dt).total_seconds() // 60)


def is_consistent(task1, time1, task2, time2):
    # time1 and time2 are tuples of (start_time, end_time)
    task1_start, task1_end = time1
    task2_start, task2_end = time2
    
    # Convert times to minutes since midnight for easier comparison
    t1_start = task1_start.hour * 60 + task1_start.minute
    t1_end = task1_end.hour * 60 + task1_end.minute
    t2_start = task2_start.hour * 60 + task2_start.minute
    t2_end = task2_end.hour * 60 + task2_end.minute
    
    # Check for overlap
    if t1_start < t2_end and t1_end > t2_start:
        return False
    
    return True

def ac3_schedule(wake_up, sleep, obligations, tasks, rest_time=0):  # Keep parameter for compatibility
    tasks_dict = {task["task"]: task for task in tasks}
    
    domains = {}
    task_names = [task["task"] for task in tasks]
    constraints = {name: set(task_names) - {name} for name in task_names}

    # Create initial timeline slots
    timeline = [{"start": wake_up, "end": sleep}]
    
    # Split timeline based on obligations
    for obligation in sorted(obligations, key=lambda x: x["start"]):
        new_timeline = []
        for slot in timeline:
            if slot["start"] < obligation["start"] < slot["end"]:
                if slot["start"] != obligation["start"]:
                    new_timeline.append({"start": slot["start"], "end": obligation["start"]})
            if slot["start"] < obligation["end"] < slot["end"]:
                if obligation["end"] != slot["end"]:
                    new_timeline.append({"start": obligation["end"], "end": slot["end"]})
            if obligation["end"] <= slot["start"] or obligation["start"] >= slot["end"]:
                new_timeline.append(slot)
        timeline = new_timeline

    # Generate possible time slots for each task
    for task in tasks:
        duration = task["duration"]
        task_domains = []
        for slot in timeline:
            available_minutes = minutes_between(slot["start"], slot["end"])
            if available_minutes >= duration:
                task_end = (datetime.combine(datetime.today(), slot["start"]) +
                          timedelta(minutes=duration)).time()
                task_domains.append((slot["start"], task_end))
        domains[task["task"]] = task_domains

    # Run AC3 algorithm
    queue = [(x, y) for x in constraints for y in constraints[x]]
    while queue:
        (x, y) = queue.pop(0)
        if revise(domains, x, y, is_consistent):
            if not domains[x]:
                return None
            for z in constraints[x] - {y}:
                queue.append((z, x))

    # Create final schedule
    scheduled_tasks = []
    used_slots = set()
    
    # Sort tasks by duration (longest first)
    sorted_tasks = sorted(tasks, key=lambda x: x["duration"], reverse=True)
    
    for task in sorted_tasks:
        task_name = task["task"]
        valid_times = domains[task_name]
        
        # Find first non-overlapping slot
        scheduled = False
        for start_time, end_time in valid_times:
            slot_valid = True
            for used_start, used_end in used_slots:
                if not is_consistent(task_name, (start_time, end_time), "", (used_start, used_end)):
                    slot_valid = False
                    break
            
            if slot_valid:
                scheduled_tasks.append({
                    "task": task_name,
                    "start": start_time,
                    "end": end_time
                })
                used_slots.add((start_time, end_time))
                scheduled = True
                break
                
        if not scheduled:
            return None

    return scheduled_tasks

def revise(domains, x, y, is_consistent):
    revised = False
    for value in domains[x][:]:
        if not any(is_consistent(x, value, y, other_value) for other_value in domains[y]):
            domains[x].remove(value)
            revised = True
    return revised
