from datetime import datetime, timedelta
from src.validators.scheduler import minutes_between
from src.core.helpers import get_time_to_preference, adjust_wakeup_and_sleep, get_available_slots

def generate_domains(timeline, tasks):
    """Generate initial domains for all tasks."""
    domains = {}
    for task in tasks:
        duration = task["duration"]
        task_domains = []
        for slot in timeline:
            available_minutes = minutes_between(slot["start"], slot["end"])
            if available_minutes >= duration:
                # Generate all possible start times within this slot
                current_time = slot["start"]
                while True:
                    # Check if there's enough time left in the slot
                    end_time = (datetime.combine(datetime.today(), current_time) +
                              timedelta(minutes=duration)).time()
                    if minutes_between(current_time, slot["end"]) >= duration:
                        task_domains.append((current_time, end_time))
                        # Move to next possible start time (e.g., in 30-minute increments)
                        current_time = (datetime.combine(datetime.today(), current_time) +
                                     timedelta(minutes=30)).time()
                    else:
                        break
        domains[task["task"]] = task_domains
    return domains

def is_consistent(task1, time_slot1, task2, time_slot2):
    """Check if two tasks' time slots are consistent with each other."""
    # Convert times to minutes since midnight for easier comparison
    t1_start = time_slot1[0].hour * 60 + time_slot1[0].minute
    t1_end = time_slot1[1].hour * 60 + time_slot1[1].minute
    t2_start = time_slot2[0].hour * 60 + time_slot2[0].minute
    t2_end = time_slot2[1].hour * 60 + time_slot2[1].minute
    
    # Check for overlap
    if t1_start < t2_end and t1_end > t2_start:
        return False
    
    return True

def filter_domain_by_preference(domain, preference):
    """Filter domain based on time preference."""
    if not preference:
        return domain
    
    filtered_domain = []
    for start_time, end_time in domain:
        if get_time_to_preference(start_time) == preference.lower():
            filtered_domain.append((start_time, end_time))
    return filtered_domain

def run_backtracking(domains, constraints, tasks):
    """
    Run backtracking algorithm with the given domains and constraints.
    """
    scheduled_tasks = []
    used_slots = []  # Changed from set to list for easier time slot comparison

    def select_unassigned_variable(current_domains, scheduled):
        """Select the most constrained variable with preference priority."""
        # First, try to schedule tasks with preferences
        unassigned_with_pref = [(task["task"], len(current_domains[task["task"]]))
                               for task in tasks 
                               if task["task"] not in [t["task"] for t in scheduled] 
                               and task.get("preference")]
        
        if unassigned_with_pref:
            return min(unassigned_with_pref, key=lambda x: x[1])[0]
        
        # Then schedule tasks without preferences
        unassigned = [(task["task"], len(current_domains[task["task"]]))
                     for task in tasks 
                     if task["task"] not in [t["task"] for t in scheduled]]
        
        if not unassigned:
            return None
        return min(unassigned, key=lambda x: x[1])[0]

    def is_slot_consistent(time_slot):
        """Check if a time slot is consistent with already used slots."""
        for used_slot in used_slots:
            if not is_consistent("", time_slot, "", used_slot):
                return False
        return True

    def backtrack(current_domains):
        """Recursive backtracking function."""
        if len(scheduled_tasks) == len(tasks):
            return True

        # Select the next task to schedule
        current_task = select_unassigned_variable(current_domains, scheduled_tasks)
        if current_task is None:
            return False

        # Get the task object for preference information
        task_obj = next(task for task in tasks if task["task"] == current_task)
        
        # Sort domain values based on preference if it exists
        domain_values = current_domains[current_task][:]
        if task_obj.get("preference"):
            domain_values.sort(
                key=lambda x: 0 if get_time_to_preference(x[0]) == task_obj["preference"].lower() else 1
            )

        # Try each value in the domain
        for time_slot in domain_values:
            if is_slot_consistent(time_slot):
                start_time, end_time = time_slot
                scheduled_tasks.append({
                    "task": current_task,
                    "start": start_time,
                    "end": end_time
                })
                used_slots.append(time_slot)

                # Create a copy of domains for this branch
                branch_domains = {task: list(domain) for task, domain in current_domains.items()}
                
                # Update domain of current task to only include the assigned value
                branch_domains[current_task] = [time_slot]

                if backtrack(branch_domains):
                    return True

                scheduled_tasks.pop()
                used_slots.pop()

        return False

    # Start backtracking search
    initial_domains = {task: list(domain) for task, domain in domains.items()}
    if backtrack(initial_domains):
        return scheduled_tasks
    return None

def backtracking_slot_placement(wake_up, sleep, obligations, tasks):
    """
    Schedule tasks using backtracking algorithm with preference support.
    
    Returns:
        dict: A dictionary containing:
            - 'tasks': List of scheduled tasks with start and end times
            - 'preference_respected': Boolean indicating if preferences were respected
    """
    # Create initial timeline
    timeline = adjust_wakeup_and_sleep(wake_up, sleep)

    timeline = get_available_slots(timeline)

    # If there are no task then just add them transparently
    if len(tasks) == 0:
        return {
            "tasks": [],
            "preference_respected": True,
            "found_schedule": True
        }

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

    # Generate initial domains
    domains = generate_domains(timeline, tasks)
    task_names = [task["task"] for task in tasks]
    constraints = {name: set(task_names) - {name} for name in task_names}

    # Try scheduling with preferences first
    preference_domains = {}
    for task in tasks:
        if task.get("preference"):
            filtered_domain = filter_domain_by_preference(domains[task["task"]], task["preference"])
            if filtered_domain:  # Only use filtered domain if it's not empty
                preference_domains[task["task"]] = filtered_domain
            else:
                preference_domains[task["task"]] = domains[task["task"]]
        else:
            preference_domains[task["task"]] = domains[task["task"]]

    # Try backtracking with preferences
    preference_result = run_backtracking(preference_domains.copy(), constraints, tasks)
    if preference_result:
        return {
            "tasks": preference_result,
            "preference_respected": True,
            "found_schedule": True
        }

    # If scheduling with preferences fails, try regular backtracking
    regular_result = run_backtracking(domains, constraints, tasks)
    if regular_result:
        return {
            "tasks": regular_result,
            "preference_respected": False,
            "found_schedule": True
        }

    return {
        "tasks": [],
        "preference_respected": False,
        "found_schedule": False
    }

def main():
    # Sample wake up and sleep times
    wake_up = datetime.strptime("08:00", "%H:%M").time()
    sleep = datetime.strptime("22:00", "%H:%M").time()

    # Obligations that create three tight slots
    obligations = [
        {"start": datetime.strptime("10:00", "%H:%M").time(), 
         "end": datetime.strptime("12:00", "%H:%M").time()},
        {"start": datetime.strptime("14:00", "%H:%M").time(), 
         "end": datetime.strptime("16:00", "%H:%M").time()},
        {"start": datetime.strptime("18:00", "%H:%M").time(), 
         "end": datetime.strptime("20:00", "%H:%M").time()},
    ]

    # Tasks that require careful placement
    tasks = [
        {"task": "Task A", "duration": 180},  # 2 hours
        {"task": "Task B", "duration": 120},  # 2 hours
        {"task": "Task C", "duration": 180},  # 3 hours
    ]

    # Run the scheduling algorithm
    scheduled_tasks = backtracking_slot_placement(wake_up, sleep, obligations, tasks)

    # Print results
    print("\nSchedule for the day:")
    print(f"Wake up time: {wake_up}")
    print(f"Sleep time: {sleep}")
    
    print("\nObligations:")
    for obligation in obligations:
        print(f"- {obligation['start']} to {obligation['end']}")
    
    print("\nScheduled Tasks:")
    if scheduled_tasks:
        for task in scheduled_tasks:
            print(f"- {task['task']}: {task['start']} to {task['end']}")
    else:
        print("Could not schedule all tasks!")

if __name__ == "__main__":
    main()