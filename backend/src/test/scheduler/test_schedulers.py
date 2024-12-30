from datetime import datetime, time
from typing import List, Dict
from pprint import pprint

# Import the schedulers
from src.schedulers.ac3 import ac3_schedule
from src.schedulers.backtracking import backtracking_slot_placement
from src.schedulers.forward_checking import forward_checking_schedule
from src.schedulers.greedy_scheduler import fit_tasks_into_schedule

def create_test_data():
    """Create sample test data for scheduling algorithms"""
    # Sample wake up and sleep times
    wake_up = datetime.strptime("08:00", "%H:%M").time()
    sleep = datetime.strptime("22:00", "%H:%M").time()

    # Sample obligations (fixed appointments)
    obligations = [
        {
            "start": datetime.strptime("10:00", "%H:%M").time(),
            "end": datetime.strptime("11:00", "%H:%M").time()
        },
        {
            "start": datetime.strptime("14:00", "%H:%M").time(),
            "end": datetime.strptime("15:00", "%H:%M").time()
        }
    ]

    # Sample tasks to be scheduled
    tasks = [
        {"task": "Study", "duration": 120},  # 2 hours
        {"task": "Exercise", "duration": 60},  # 1 hour
        {"task": "Read", "duration": 90},  # 1.5 hours
    ]

    return wake_up, sleep, obligations, tasks

def print_schedule(algorithm_name: str, schedule: List[Dict]):
    """Pretty print the schedule"""
    print(f"\n{'-'*20} {algorithm_name} {'-'*20}")
    if schedule is None:
        print("No valid schedule found!")
        return
    
    for task in schedule:
        print(f"Task: {task['task']:<10} | Start: {task['start'].strftime('%H:%M')} | "
              f"End: {task['end'].strftime('%H:%M')}")

def test_all_schedulers():
    # Get test data
    wake_up, sleep, obligations, tasks = create_test_data()
    rest_time = 0  # Set rest time to zero as requested

    print("\nTest Data:")
    print(f"Wake up: {wake_up.strftime('%H:%M')}")
    print(f"Sleep: {sleep.strftime('%H:%M')}")
    print("\nObligations:")
    for obligation in obligations:
        print(f"Start: {obligation['start'].strftime('%H:%M')} | "
              f"End: {obligation['end'].strftime('%H:%M')}")
    print("\nTasks to Schedule:")
    for task in tasks:
        print(f"Task: {task['task']:<10} | Duration: {task['duration']} minutes")

    # Test AC3
    ac3_result = ac3_schedule(wake_up, sleep, obligations, tasks)
    print_schedule("AC3 Algorithm", ac3_result)

    # Test Backtracking
    backtracking_result = backtracking_slot_placement(wake_up, sleep, obligations, tasks)
    print_schedule("Backtracking Algorithm", backtracking_result)

    # Test Forward Checking
    forward_checking_result = forward_checking_schedule(wake_up, sleep, obligations, tasks, rest_time)
    print_schedule("Forward Checking Algorithm", forward_checking_result)

    # Test Greedy
    greedy_result = fit_tasks_into_schedule(wake_up, sleep, obligations, tasks)
    print_schedule("Greedy Algorithm", greedy_result)

if __name__ == "__main__":
    test_all_schedulers()