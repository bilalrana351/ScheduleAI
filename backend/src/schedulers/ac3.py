from datetime import timedelta, datetime

from src.core.helpers import get_time_to_preference, adjust_wakeup_and_sleep

def minutes_between(start_time, end_time):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    return int((end_dt - start_dt).total_seconds() // 60)


def is_consistent(task1, time1, task2, time2):
    """Check if two tasks' time slots are consistent with each other."""
    # Convert times to minutes since midnight for easier comparison
    t1_start = time1[0].hour * 60 + time1[0].minute
    t1_end = time1[1].hour * 60 + time1[1].minute
    t2_start = time2[0].hour * 60 + time2[0].minute
    t2_end = time2[1].hour * 60 + time2[1].minute
    
    # Check for overlap
    if t1_start < t2_end and t1_end > t2_start:
        return False
    
    return True



def filter_domain_by_preference(domain, preference):
    if not preference:
        return domain
    
    filtered_domain = []
    for start_time, end_time in domain:
        # Convert to time period
        period = get_time_to_preference(start_time)
        if period == preference.lower():
            filtered_domain.append((start_time, end_time))
    return filtered_domain

def ac3_schedule(wake_up, sleep, obligations, tasks, rest_time=0):
    """
    Schedule tasks using AC3 algorithm.
    Now includes support for time preferences (morning, afternoon, evening, night).
    
    Returns:
        dict: A dictionary containing:
            - 'tasks': List of scheduled tasks with start and end times
            - 'preference_respected': Boolean indicating if preferences were respected
    """
    tasks_dict = {task["task"]: task for task in tasks}
    
    domains = {}
    task_names = [task["task"] for task in tasks]
    constraints = {name: set(task_names) - {name} for name in task_names}

    timeline = adjust_wakeup_and_sleep(wake_up, sleep)

    print(timeline, "is the timeline")

    # If there are no task then just add them transparently
    if len(tasks) == 0:
        return {"tasks": [], "preference_respected": True, "found_schedule": True}
    
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

    # Try AC3 with preferences
    preference_result = run_ac3(preference_domains.copy(), constraints, tasks)
    if preference_result:
        return {
            "tasks": preference_result,
            "preference_respected": True,
            "found_schedule": True
        }

    # If scheduling with preferences fails, try regular AC3
    regular_result = run_ac3(domains, constraints, tasks)
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

def run_ac3(domains, constraints, tasks):
    """
    Run AC3 algorithm with backtracking and arc consistency after each assignment.
    """
    def enforce_arc_consistency(current_domains, current_task=None):
        """Run AC3 on the current domains after an assignment."""
        queue = []
        if current_task:
            # If a task was just assigned, check arcs connected to it first
            for other_task in constraints[current_task]:
                queue.append((other_task, current_task))
        else:
            # Initial run: check all arcs
            queue = [(x, y) for x in constraints for y in constraints[x]]

        while queue:
            (x, y) = queue.pop(0)
            if revise(current_domains, x, y, is_consistent):
                if not current_domains[x]:
                    return False  # Domain wipeout
                for z in constraints[x] - {y}:
                    queue.append((z, x))
        return True

    def select_unassigned_variable(current_domains, assigned_tasks):
        """Select the most constrained variable with preference priority."""
        # First, try to schedule tasks with preferences
        unassigned_with_pref = [(task["task"], len(current_domains[task["task"]]))
                               for task in tasks 
                               if task["task"] not in assigned_tasks and task.get("preference")]
        
        if unassigned_with_pref:
            return min(unassigned_with_pref, key=lambda x: x[1])[0]
        
        # Then schedule tasks without preferences
        unassigned = [(task["task"], len(current_domains[task["task"]]))
                     for task in tasks 
                     if task["task"] not in assigned_tasks]
        
        if not unassigned:
            return None
        return min(unassigned, key=lambda x: x[1])[0]

    def backtrack_with_ac3(assigned_tasks, current_domains):
        """Backtracking search with AC3 after each assignment."""
        if len(assigned_tasks) == len(tasks):
            return assigned_tasks

        # Choose the next task (most constrained variable)
        current_task = select_unassigned_variable(current_domains, assigned_tasks)
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
        for start_time, end_time in domain_values:
            # Check if the value is consistent with current assignments
            is_valid = True
            for assigned_task, (assigned_start, assigned_end) in assigned_tasks.items():
                if not is_consistent(current_task, (start_time, end_time), 
                                  assigned_task, (assigned_start, assigned_end)):
                    is_valid = False
                    break

            if is_valid:
                # Make assignment
                assigned_tasks[current_task] = (start_time, end_time)
                
                # Create a copy of domains for this branch
                branch_domains = {task: list(domain) for task, domain in current_domains.items()}
                
                # Update domain of current task to only include the assigned value
                branch_domains[current_task] = [(start_time, end_time)]
                
                # Run arc consistency
                if enforce_arc_consistency(branch_domains, current_task):
                    result = backtrack_with_ac3(assigned_tasks, branch_domains)
                    if result is not None:
                        return result

                # If we get here, this assignment failed
                del assigned_tasks[current_task]

        return None

    # Initial arc consistency check
    initial_domains = {task: list(domain) for task, domain in domains.items()}
    if not enforce_arc_consistency(initial_domains):
        return None

    # Start backtracking search
    result = backtrack_with_ac3({}, initial_domains)
    if result is None:
        return None

    # Convert result to scheduled tasks list
    scheduled_tasks = []
    for task_name, (start_time, end_time) in result.items():
        scheduled_tasks.append({
            "task": task_name,
            "start": start_time,
            "end": end_time
        })

    return scheduled_tasks

def revise(domains, x, y, is_consistent):
    """Revise the domain of x with respect to y."""
    revised = False
    for value_x in domains[x][:]:  # Make a copy to avoid modifying during iteration
        # Check if there's at least one value in y's domain that's consistent with x's value
        if not any(is_consistent(x, value_x, y, value_y) for value_y in domains[y]):
            domains[x].remove(value_x)
            revised = True
    return revised