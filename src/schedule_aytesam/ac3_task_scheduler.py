
from datetime import timedelta, datetime

def minutes_between(start_time, end_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    return int((end_dt - start_dt).total_seconds() // 60)

def ac3_schedule(wake_up, sleep, obligations, tasks, rest_time):
    def is_consistent(value, other_value):
        return value[1] <= other_value[0] or other_value[1] <= value[0]

    domains = {}
    task_names = [task["task"] for task in tasks]
    constraints = {name: set(task_names) - {name} for name in task_names}

    timeline = [{"start": wake_up, "end": sleep}]

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

    for task in tasks:
        duration = task["duration"] + rest_time
        task_domains = []
        for slot in timeline:
            available_minutes = minutes_between(slot["start"], slot["end"])
            if available_minutes >= duration:
                task_start = slot["start"]
                task_end = (datetime.combine(datetime.today(), task_start) +
                            timedelta(minutes=task["duration"])).time()
                rest_end = (datetime.combine(datetime.today(), task_end) +
                            timedelta(minutes=rest_time)).time()
                task_domains.append((task_start, rest_end))
        domains[task["task"]] = task_domains

    queue = [(x, y) for x in constraints for y in constraints[x]]
    while queue:
        (x, y) = queue.pop(0)
        if revise(domains, x, y, is_consistent):
            if not domains[x]:
                return None  
            for z in constraints[x] - {y}:
                queue.append((z, x))

    scheduled_tasks = []
    for task_name, times in domains.items():
        if times:
            scheduled_tasks.append({"task": task_name, "start": times[0][0], "end": times[0][1]})

    return scheduled_tasks


def revise(domains, x, y, is_consistent):
    revised = False
    for value in domains[x][:]:
        if not any(is_consistent(x, value, y, other_value) for other_value in domains[y]):
            domains[x].remove(value)
            revised = True
    return revised
