from datetime import timedelta, datetime
from src.core.helpers import get_time_to_preference, adjust_wakeup_and_sleep, get_available_slots

def minutes_between(start_time, end_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    return int((end_dt - start_dt).total_seconds() // 60)

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

def filter_domain_by_preference(domain, preference):
    """Filter domain based on time preference."""
    if not preference:
        return domain
    
    filtered_domain = []
    for start_time, end_time in domain:
        if get_time_to_preference(start_time) == preference.lower():
            filtered_domain.append((start_time, end_time))
    return filtered_domain

def run_forward_checking(domains, constraints, tasks):
    """
    Run forward checking algorithm with proper backtracking and domain pruning.
    """
    def update_domains(current_domains, assigned_task, time_slot, assigned):
        """Update domains of unassigned variables based on the current assignment."""
        new_domains = {task: list(domain) for task, domain in current_domains.items()}
        
        # Set domain of assigned task to only the assigned value
        new_domains[assigned_task] = [time_slot]
        
        # Create new assigned dict with the current assignment
        new_assigned = assigned.copy()
        new_assigned[assigned_task] = time_slot
        
        # Update domains of unassigned tasks
        for task in new_domains:
            if task != assigned_task and task not in assigned:
                # Remove values that are inconsistent with the current assignment
                new_domains[task] = [
                    value for value in new_domains[task]
                    if is_consistent(task, value, new_assigned)
                ]
                
                # Check for domain wipeout
                if not new_domains[task]:
                    return None
        
        return new_domains

    def is_consistent(task_name, time_slot, assigned):
        """Check if a time slot is consistent with already assigned tasks."""
        start_time, end_time = time_slot
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        
        for other_task, (other_start, other_end) in assigned.items():
            other_start_minutes = other_start.hour * 60 + other_start.minute
            other_end_minutes = other_end.hour * 60 + other_end.minute
            
            # Check for overlap
            if not (end_minutes <= other_start_minutes or start_minutes >= other_end_minutes):
                return False
        return True

    def select_unassigned_variable(current_domains, assigned):
        """Select the most constrained variable (minimum remaining values)."""
        # First, try to schedule tasks with preferences
        unassigned_with_pref = [(task["task"], len(current_domains[task["task"]]))
                               for task in tasks 
                               if task["task"] not in assigned and task.get("preference")]
        
        if unassigned_with_pref:
            return min(unassigned_with_pref, key=lambda x: x[1])[0]
        
        # Then schedule tasks without preferences
        unassigned = [(task["task"], len(current_domains[task["task"]]))
                     for task in tasks 
                     if task["task"] not in assigned]
        
        if not unassigned:
            return None
        return min(unassigned, key=lambda x: x[1])[0]

    def backtrack_with_forward_checking(assigned, current_domains):
        """Backtracking search with forward checking after each assignment."""
        if len(assigned) == len(tasks):
            return assigned

        # Select the next variable to assign
        current_task = select_unassigned_variable(current_domains, assigned)
        if current_task is None:
            return None

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
            if is_consistent(current_task, time_slot, assigned):
                # Make assignment
                assigned[current_task] = time_slot
                
                # Update domains with forward checking
                new_domains = update_domains(current_domains, current_task, time_slot, assigned)
                
                if new_domains is not None:
                    # Recursive call with updated domains
                    result = backtrack_with_forward_checking(assigned, new_domains)
                    if result is not None:
                        return result

                # If we get here, this assignment failed
                del assigned[current_task]

        return None

    # Start backtracking search with forward checking
    result = backtrack_with_forward_checking({}, domains)
    
    if result is None:
        return None

    # Convert result to scheduled tasks list
    scheduled_tasks = []
    for task, (start_time, end_time) in result.items():
        scheduled_tasks.append({
            "task": task,
            "start": start_time,
            "end": end_time
        })

    return scheduled_tasks

def forward_checking_schedule(wake_up, sleep, obligations, tasks, rest_time=0):
    """
    Schedule tasks using forward checking algorithm with preference support.
    
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
        return {"tasks": [], "preference_respected": True, "found_schedule": True}

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

    # Try forward checking with preferences
    preference_result = run_forward_checking(preference_domains.copy(), constraints, tasks)
    if preference_result:
        return {
            "tasks": preference_result,
            "preference_respected": True,
            "found_schedule": True
        }

    # If scheduling with preferences fails, try regular forward checking
    regular_result = run_forward_checking(domains, constraints, tasks)
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