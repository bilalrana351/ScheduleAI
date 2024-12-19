
from inputs import get_schedule_inputs
from validator import validate_inputs
from scheduler import fit_tasks_into_schedule

def main():
    schedule_data = get_schedule_inputs()
    if not schedule_data:
        print("Invalid inputs. Please restart the program.")
        return

    validation_result = validate_inputs(schedule_data)
    if not validation_result["valid"]:
        print("Errors found in your schedule:")
        for error in validation_result["errors"]:
            print(f"- {error}")
        return

    print("Scheduling your tasks...")
    wake_up = schedule_data["wake_up_time"]
    sleep = schedule_data["sleep_time"]
    obligations = schedule_data["obligations"]
    regular_tasks = schedule_data["regular_tasks"]

    scheduled_tasks = fit_tasks_into_schedule(wake_up, sleep, obligations, regular_tasks)

    print("Your finalized schedule:")
    for obligation in obligations:
        print(f"Obligation: {obligation['task']} from {obligation['start']} to {obligation['end']}")
    for task in scheduled_tasks:
        print(f"Task: {task['task']} from {task['start']} to {task['end']}")

if __name__ == "__main__":
    main()
