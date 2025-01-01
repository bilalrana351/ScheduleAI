from datetime import timedelta, datetime

def minutes_between(start_time, end_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    return int((end_dt - start_dt).total_seconds() // 60)

def fit_tasks_into_schedule(wake_up, sleep, obligations, tasks):
    total_day_minutes = 24 * 60
    timeline = []
    
    # Initialize timeline based on wake/sleep times
    wake_minutes = wake_up.hour * 60 + wake_up.minute
    sleep_minutes = sleep.hour * 60 + sleep.minute
    
    if wake_minutes < sleep_minutes:
        timeline = [{"start": wake_up, "end": sleep}]
    else:
        # If wake time is after sleep time, create two intervals
        midnight = datetime.strptime("00:00", "%H:%M").time()
        next_midnight = datetime.strptime("23:59", "%H:%M").time()
        timeline = [
            {"start": wake_up, "end": next_midnight},
            {"start": midnight, "end": sleep}
        ]

    # If there are no task then just add them transparently
    if len(tasks) == 0:
        return {"tasks": [], "preference_respected": True}
    
    # Process obligations
    for obligation in sorted(obligations, key=lambda x: (x["start"].hour * 60 + x["start"].minute)):
        start_minutes = obligation["start"].hour * 60 + obligation["start"].minute
        end_minutes = obligation["end"].hour * 60 + obligation["end"].minute
        
        # Handle obligations that cross midnight
        if start_minutes > end_minutes:
            # Split into two intervals
            midnight = datetime.strptime("00:00", "%H:%M").time()
            next_midnight = datetime.strptime("23:59", "%H:%M").time()
            
            # Process first interval (start to midnight)
            new_timeline = []
            for slot in timeline:
                slot_start_min = slot["start"].hour * 60 + slot["start"].minute
                slot_end_min = slot["end"].hour * 60 + slot["end"].minute
                
                if slot_start_min < start_minutes < slot_end_min:
                    new_timeline.append({"start": slot["start"], "end": obligation["start"]})
                if slot_start_min < total_day_minutes < slot_end_min:
                    new_timeline.append({"start": obligation["end"], "end": slot["end"]})
                if start_minutes >= slot_end_min or total_day_minutes <= slot_start_min:
                    new_timeline.append(slot)
            
            # Process second interval (midnight to end)
            final_timeline = []
            for slot in new_timeline:
                slot_start_min = slot["start"].hour * 60 + slot["start"].minute
                slot_end_min = slot["end"].hour * 60 + slot["end"].minute
                
                if slot_start_min < end_minutes < slot_end_min:
                    final_timeline.append({"start": slot["start"], "end": obligation["end"]})
                if slot_start_min < 0 < slot_end_min:
                    final_timeline.append({"start": obligation["end"], "end": slot["end"]})
                if end_minutes >= slot_end_min or 0 <= slot_start_min:
                    final_timeline.append(slot)
            
            timeline = final_timeline
        else:
            # Handle normal obligations
            new_timeline = []
            for slot in timeline:
                if slot["start"] < obligation["start"] < slot["end"]:
                    new_timeline.append({"start": slot["start"], "end": obligation["start"]})
                if slot["start"] < obligation["end"] < slot["end"]:
                    new_timeline.append({"start": obligation["end"], "end": slot["end"]})
                if obligation["end"] <= slot["start"] or obligation["start"] >= slot["end"]:
                    new_timeline.append(slot)
            timeline = new_timeline

    # Schedule tasks
    scheduled_tasks = []
    for task in tasks:
        duration_needed = task["duration"]
        task_scheduled = False
        
        for slot in timeline:
            slot_start_min = slot["start"].hour * 60 + slot["start"].minute
            slot_end_min = slot["end"].hour * 60 + slot["end"].minute
            
            # Adjust for slots that cross midnight
            if slot_end_min < slot_start_min:
                slot_end_min += total_day_minutes
                
            available_minutes = slot_end_min - slot_start_min
            
            if available_minutes >= duration_needed:
                task_start = slot["start"]
                task_end_minutes = (slot_start_min + duration_needed) % total_day_minutes
                task_end = datetime.strptime(f"{task_end_minutes // 60:02d}:{task_end_minutes % 60:02d}", "%H:%M").time()
                
                scheduled_tasks.append({
                    "task": task["task"],
                    "start": task_start,
                    "end": task_end
                })
                
                # Update timeline
                new_start = task_end
                timeline = [{"start": new_start, "end": slot["end"]}] + [
                    s for s in timeline if s != slot
                ]
                task_scheduled = True
                break
                
        if not task_scheduled:
            print(f"Warning: Could not schedule task '{task['task']}'")

    return scheduled_tasks
