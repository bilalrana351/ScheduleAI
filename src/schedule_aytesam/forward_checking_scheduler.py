
from datetime import timedelta, datetime

def minutes_between(start_time, end_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    return int((end_dt - start_dt).total_seconds() // 60)

def forward_checking_schedule(wake_up, sleep, obligations, tasks, rest_time):
    def is_consistent(task, value, assigned):
        for other_task, other_value in assigned.items():
            if not (value[1] <= other_value[0] or other_value[1] <= value[0]):
                return False
        return True

    domains = {}
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

    assigned = {}

    def backtrack():
        if len(assigned) == len(tasks):
            return assigned

        unassigned = [task for task in tasks if task["task"] not in assigned]
        current_task = unassigned[0]["task"]

        for value in domains[current_task]:
            if is_consistent(current_task, value, assigned):
                assigned[current_task] = value
                result = backtrack()
                if result is not None:
                    return result
                del assigned[current_task]

        return None

    result = backtrack()

    if result is None:
        return None

    scheduled_tasks = []
    for task, times in result.items():
        scheduled_tasks.append({"task": task, "start": times[0], "end": times[1]})

    return scheduled_tasks
