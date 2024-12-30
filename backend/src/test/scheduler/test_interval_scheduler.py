from datetime import datetime, timedelta
from src.schedulers.interval_scheduler import interval_schedule

def create_time(hour, minute=0):
    return datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()

def print_schedule(result):
    print("\nInterval Scheduler Results:")
    print("-" * 50)
    
    if result is None:
        print("No valid schedule found!")
        return
        
    print(f"Schedule found! Preferences respected: {result['preference_respected']}")
    print("\nScheduled Tasks:")
    for task in result["tasks"]:
        print(f"- {task['task']}: {task['start']} to {task['end']} "
              f"(Duration: {task['duration']} minutes)")

def test_interval_scheduler_with_preferences():
    """Test interval scheduler with time preferences."""
    wake_up = create_time(8)
    sleep = create_time(22)
    
    tasks = [
        {
            "task": "Morning Study",
            "duration": 120,
            "preference": "morning"
        },
        {
            "task": "Evening Exercise",
            "duration": 60,
            "preference": "evening"
        }
    ]
    
    result = interval_schedule(wake_up, sleep, [], tasks)
    print(result)
    assert result is not None, "Failed to find a schedule"
    assert result["preference_respected"] is True

def test_interval_scheduler_with_tight_schedule():
    """Test interval scheduler with very tight time constraints."""
    wake_up = create_time(8)
    sleep = create_time(12)  # Only 4 hours available
    
    tasks = [
        {"task": "Task 1", "duration": 120},
        {"task": "Task 2", "duration": 120}
    ]
    
    result = interval_schedule(wake_up, sleep, [], tasks)
    assert result is not None, "Failed to find a schedule"
    
    # Verify total duration matches
    total_duration = sum(task["duration"] for task in result["tasks"])
    assert total_duration == 240  # 4 hours = 240 minutes

def test_interval_scheduler_with_complex_obligations():
    """Test interval scheduler with complex overlapping obligations."""
    wake_up = create_time(8)
    sleep = create_time(22)
    
    obligations = [
        {"start": create_time(10), "end": create_time(11)},
        {"start": create_time(13), "end": create_time(15)},
        {"start": create_time(14), "end": create_time(16)},  # Overlaps with previous
        {"start": create_time(18), "end": create_time(19)}
    ]
    
    tasks = [
        {"task": "Task 1", "duration": 60},
        {"task": "Task 2", "duration": 120}
    ]
    
    result = interval_schedule(wake_up, sleep, obligations, tasks)
    assert result is not None, "Failed to find a schedule"
    
    # Verify tasks don't overlap with obligations
    for task in result["tasks"]:
        for obligation in obligations:
            task_start = task["start"].hour * 60 + task["start"].minute
            task_end = task["end"].hour * 60 + task["end"].minute
            obl_start = obligation["start"].hour * 60 + obligation["start"].minute
            obl_end = obligation["end"].hour * 60 + obligation["end"].minute
            
            assert not (task_start < obl_end and task_end > obl_start), \
                "Task overlaps with obligation"

def test_interval_scheduler_with_split_tasks():
    """Test interval scheduler's ability to split tasks across intervals."""
    wake_up = create_time(8)
    sleep = create_time(16)
    
    obligations = [
        {"start": create_time(10), "end": create_time(14)}  # 4-hour obligation in middle
    ]
    
    tasks = [
        {"task": "Split Task", "duration": 240}  # 4-hour task that must be split
    ]
    
    result = interval_schedule(wake_up, sleep, obligations, tasks)
    assert result is not None, "Failed to find a schedule"
    
    # Verify task was split
    split_tasks = [t for t in result["tasks"] if t["task"] == "Split Task"]
    assert len(split_tasks) > 1, "Task was not split"

    print(result)
    
    # Verify total duration matches original task
    total_duration = sum(t["duration"] for t in split_tasks)
    assert total_duration == 240

def test_interval_scheduler_performance():
    """Test performance of interval scheduler with a large number of tasks."""
    wake_up = create_time(8)
    sleep = create_time(22)
    
    # Create 10 tasks of 30 minutes each
    tasks = [
        {"task": f"Task {i}", "duration": 30}
        for i in range(10)
    ]
    
    start_time = datetime.now()
    result = interval_schedule(wake_up, sleep, [], tasks)
    end_time = datetime.now()
    
    assert result is not None, "Failed to find a schedule"
    assert len(result["tasks"]) == 10
    print(f"Interval scheduler took {(end_time - start_time).total_seconds():.3f} seconds")

def test_interval_scheduler_with_impossible_schedule():
    """Test interval scheduler with an impossible schedule."""
    wake_up = create_time(8)
    sleep = create_time(12)  # 4 hours available
    
    tasks = [
        {"task": "Task 1", "duration": 180},  # 3 hours
        {"task": "Task 2", "duration": 180}   # 3 hours
    ]
    
    result = interval_schedule(wake_up, sleep, [], tasks)
    assert result is None, "Should have failed to find a schedule"

def test_interval_scheduler_with_wrong_preferences():
    """Test interval scheduler with wrong preferences."""
    wake_up = create_time(8)
    sleep = create_time(16)

    obligations = [
        {"start": create_time(10), "end": create_time(14)}
    ]

    tasks = [
        {"task": "Task 1", "duration": 120, "preference": "morning"},
        {"task": "Task 2", "duration": 120, "preference": "morning"}
    ]

    result = interval_schedule(wake_up, sleep, obligations, tasks)
    assert result is not None, "Failed to find a schedule"
    assert len(result["tasks"]) == 2
    assert result["preference_respected"] is False

def test_interval_scheduler_with_minimal_intervals():
    """Test interval scheduler with tasks that exactly match interval size."""
    wake_up = create_time(8)
    sleep = create_time(12)
    
    tasks = [
        {"task": "Task 1", "duration": 30},  # This will determine interval size
        {"task": "Task 2", "duration": 60},  # Should take 2 intervals
        {"task": "Task 3", "duration": 90}   # Should take 3 intervals
    ]
    
    result = interval_schedule(wake_up, sleep, [], tasks)
    assert result is not None, "Failed to find a schedule"
    
    # Verify tasks were scheduled with correct durations
    task_durations = {t["task"]: sum(p["duration"] for p in result["tasks"] if p["task"] == t["task"])
                     for t in tasks}
    assert task_durations["Task 1"] == 30
    assert task_durations["Task 2"] == 60
    assert task_durations["Task 3"] == 90

if __name__ == "__main__":
    test_interval_scheduler_with_preferences()
    test_interval_scheduler_with_tight_schedule()
    test_interval_scheduler_with_complex_obligations()
    test_interval_scheduler_with_split_tasks()
    test_interval_scheduler_performance()
    test_interval_scheduler_with_impossible_schedule()
    test_interval_scheduler_with_wrong_preferences()
    test_interval_scheduler_with_minimal_intervals()
    print("All interval scheduler tests passed successfully!") 