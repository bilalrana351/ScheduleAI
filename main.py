from inputs import get_schedule_inputs
from validator import validate_inputs, find_available_slot
from ac3_task_scheduler import ac3_schedule
from forward_checking_scheduler import forward_checking_schedule

def main():
    schedule_data = get_schedule_inputs()
    if not schedule_data:
        print("Invalid inputs. Please restart the program.")
        return

    valid, errors = validate_inputs(schedule_data)
    if not valid:
        print("Errors found in your schedule:")
        for error in errors:
            print(f"- {error}")
        return

    print("Choose a scheduling algorithm:")
    print("1. AC-3 Algorithm")
    print("2. Forward Checking")
    choice = input("Enter your choice (1/2): ").strip()

    wake_up = schedule_data["wake_up_time"]
    sleep = schedule_data["sleep_time"]
    obligations = schedule_data["obligations"]
    regular_tasks = schedule_data["regular_tasks"]
    rest_time = schedule_data["rest_time"]

    if choice == "1":
        print("Scheduling your tasks using AC-3 algorithm...")
        scheduled_tasks = ac3_schedule(wake_up, sleep, obligations, regular_tasks, rest_time)
    elif choice == "2":
        print("Scheduling your tasks using Forward Checking...")
        scheduled_tasks = forward_checking_schedule(wake_up, sleep, obligations, regular_tasks, rest_time)
    else:
        print("Invalid choice. Please restart the program.")
        return

    if not scheduled_tasks:
        print("Unable to find a valid schedule. Attempting to resolve conflicts...")
        for task in regular_tasks:
            updated_schedule = find_available_slot(regular_tasks, obligations, task, wake_up, sleep, rest_time)
            if updated_schedule:
                print(f"Task '{task['task']}' rescheduled successfully.")
                obligations = updated_schedule
            else:
                print(f"Task '{task['task']}' could not be rescheduled.")
                break

    print("Your finalized schedule:")
    for obligation in obligations:
        print(f"Obligation: {obligation['task']} from {obligation['start']} to {obligation['end']}")
    if scheduled_tasks:
        for task in scheduled_tasks:
            print(f"Task: {task['task']} from {task['start']} to {task['end']}")

if __name__ == "__main__":
    main()
