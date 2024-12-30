
from datetime import timedelta, datetime

def minutes_between(start_time, end_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    return int((end_dt - start_dt).total_seconds() // 60)

def fit_tasks_into_schedule(wake_up, sleep, obligations, tasks):
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

    scheduled_tasks = []
    for task in tasks:
        duration_needed = task["duration"]
        for slot in timeline:
            available_minutes = minutes_between(slot["start"], slot["end"])
            if available_minutes >= duration_needed:
                task_start = slot["start"]
                task_end = (datetime.combine(datetime.today(), task_start) +
                            timedelta(minutes=duration_needed)).time()
                scheduled_tasks.append({"task": task["task"], "start": task_start, "end": task_end})

                new_start = task_end
                timeline = [{"start": new_start, "end": slot["end"]}] + [
                    s for s in timeline if s != slot]
                break

    return {
        "tasks": scheduled_tasks,
        "preference_respected": False
    }
