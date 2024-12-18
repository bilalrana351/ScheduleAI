from datetime import datetime, timedelta

from scheduler import minutes_between  # Importing a utility function to calculate minutes between two times


def backtracking_slot_placement(wake_up, sleep, obligations, tasks):
    """
    Function to schedule tasks into available time slots using a backtracking algorithm.

    Parameters:
        wake_up (datetime.time): Wake-up time.
        sleep (datetime.time): Sleep time.
        obligations (list): List of fixed obligations with 'start' and 'end' times.
        tasks (list): List of tasks with 'task', 'duration', and other attributes.

    Returns:
        list: Scheduled tasks with their start and end times.
    """

    # 1- Firstly I have initialized the timeline as a single slot from wake-up to sleep time.
    timeline = [{"start": wake_up, "end": sleep}]

    # 2- I Processed all obligations, splitting the timeline wherever obligations occupy time.
    for obligation in sorted(obligations, key=lambda x: x["start"]):  # Obligations are sorted by start time
        new_timeline = []  # Temporary timeline to store updated available slots

        for slot in timeline:
            # Case 1: If the obligation starts within the current slot, split before it starts.
            if slot["start"] < obligation["start"] < slot["end"]:
                new_timeline.append({"start": slot["start"], "end": obligation["start"]})

            # Case 2: If the obligation ends within the current slot, split after it ends.
            if slot["start"] < obligation["end"] < slot["end"]:
                new_timeline.append({"start": obligation["end"], "end": slot["end"]})

            # Case 3: If the obligation does not overlap, retain the slot as is.
            if obligation["end"] <= slot["start"] or obligation["start"] >= slot["end"]:
                new_timeline.append(slot)

        # Updating the timeline after processing the current obligation.
        timeline = new_timeline

    # 3- Initialize a list to store successfully scheduled tasks.
    scheduled_tasks = []

    # Defined the backtracking function for recursive task placement.
    def backtrack(task_index, timeline):
        """
        Recursive function to schedule tasks using backtracking.

        Parameters:
            task_index (int): Index of the current task to be scheduled.
            timeline (list): List of available time slots.

        Returns:
            bool: True if all tasks are successfully scheduled, False otherwise.
        """
        # Base case: If all tasks are placed, return True.
        if task_index == len(tasks):
            return True

        # Get the current task and its duration.
        task = tasks[task_index]
        duration_needed = task["duration"]

        # Iterate through available time slots to find a suitable slot for the task.
        for slot in timeline:
            # Calculate available minutes in the current slot.
            available_minutes = minutes_between(slot["start"], slot["end"])

            # Check if the slot can accommodate the task's duration.
            if available_minutes >= duration_needed:
                # Assign the task a start and end time.
                task_start = slot["start"]
                task_end = (datetime.combine(datetime.today(), task_start) + timedelta(minutes=duration_needed)).time()

                # Add the task to the scheduled list.
                scheduled_tasks.append({"task": task["task"], "start": task_start, "end": task_end})

                # Update the timeline by splitting the current slot after the task.
                new_start = task_end  # Remaining time starts after the task ends.
                new_timeline = [{"start": new_start, "end": slot["end"]}] + [s for s in timeline if s != slot]

                # Recursively try to place the next task with the updated timeline.
                if backtrack(task_index + 1, new_timeline):
                    return True

                # Backtrack: Remove the task if it leads to an invalid solution.
                scheduled_tasks.pop()

        # If no valid slot is found for the current task, return False.
        return False

    # Step 4: Start the backtracking process from the first task.
    backtrack(0, timeline)

    # Return the list of successfully scheduled tasks.
    return scheduled_tasks
