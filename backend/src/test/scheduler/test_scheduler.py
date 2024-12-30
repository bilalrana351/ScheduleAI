from datetime import datetime, timedelta
from src.schedulers.ac3 import ac3_schedule
from src.schedulers.backtracking import backtracking_slot_placement
from src.schedulers.forward_checking import forward_checking_schedule

def create_time(hour, minute=0):
    return datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()

def print_schedule(algorithm_name, result):
    print(f"\n{algorithm_name} Results:")
    print("-" * 50)
    
    if result is None:
        print("No valid schedule found!")
        return
        
    print(f"Schedule found! Preferences respected: {result['preference_respected']}")
    print("\nScheduled Tasks:")
    for task in result["tasks"]:
        print(f"- {task['task']}: {task['start']} to {task['end']}")

def test_all_algorithms_with_preferences():
    """Test all algorithms with time preferences."""
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
    
    algorithms = [
        ("AC3", ac3_schedule),
        ("Forward Checking", forward_checking_schedule),
        ("Backtracking", backtracking_slot_placement)
    ]
    
    for name, algorithm in algorithms:
        result = algorithm(wake_up, sleep, [], tasks)
        assert result is not None, f"{name} failed to find a schedule"
        assert result["preference_respected"] is True
        assert len(result["tasks"]) == 2
        
        # Verify morning task is in morning
        morning_task = next(t for t in result["tasks"] if t["task"] == "Morning Study")
        assert morning_task["start"].hour < 12
        
        # Verify evening task is in evening
        evening_task = next(t for t in result["tasks"] if t["task"] == "Evening Exercise")
        assert evening_task["start"].hour >= 17

def test_algorithms_with_tight_schedule():
    """Test all algorithms with very tight time constraints."""
    wake_up = create_time(8)
    sleep = create_time(12)  # Only 4 hours available
    
    tasks = [
        {"task": "Task 1", "duration": 120},
        {"task": "Task 2", "duration": 120}
    ]
    
    algorithms = [
        ("AC3", ac3_schedule),
        ("Forward Checking", forward_checking_schedule),
        ("Backtracking", backtracking_slot_placement)
    ]
    
    for name, algorithm in algorithms:
        result = algorithm(wake_up, sleep, [], tasks)
        assert result is not None, f"{name} failed to find a schedule"
        assert len(result["tasks"]) == 2

def test_algorithms_with_complex_obligations():
    """Test all algorithms with complex overlapping obligations."""
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
    
    algorithms = [
        ("AC3", ac3_schedule),
        ("Forward Checking", forward_checking_schedule),
        ("Backtracking", backtracking_slot_placement)
    ]
    
    for name, algorithm in algorithms:
        result = algorithm(wake_up, sleep, obligations, tasks)
        assert result is not None, f"{name} failed to find a schedule"
        assert len(result["tasks"]) == 2

def test_algorithms_performance():
    """Test performance of all algorithms with a large number of tasks."""
    wake_up = create_time(8)
    sleep = create_time(22)
    
    # Create 10 tasks of 30 minutes each
    tasks = [
        {"task": f"Task {i}", "duration": 30}
        for i in range(10)
    ]
    
    algorithms = [
        ("AC3", ac3_schedule),
        ("Forward Checking", forward_checking_schedule),
        ("Backtracking", backtracking_slot_placement)
    ]
    
    for name, algorithm in algorithms:
        start_time = datetime.now()
        result = algorithm(wake_up, sleep, [], tasks)
        end_time = datetime.now()
        
        assert result is not None, f"{name} failed to find a schedule"
        assert len(result["tasks"]) == 10
        print(f"{name} took {(end_time - start_time).total_seconds():.3f} seconds")

def test_algorithms_with_impossible_schedule():
    """Test all algorithms with an impossible schedule."""
    wake_up = create_time(8)
    sleep = create_time(12)  # 4 hours available
    
    tasks = [
        {"task": "Task 1", "duration": 180},  # 3 hours
        {"task": "Task 2", "duration": 180}   # 3 hours
    ]
    
    algorithms = [
        ("AC3", ac3_schedule),
        ("Forward Checking", forward_checking_schedule),
        ("Backtracking", backtracking_slot_placement)
    ]
    
    for name, algorithm in algorithms:
        result = algorithm(wake_up, sleep, [], tasks)
        assert result is None, f"{name} should have failed to find a schedule"

def test_algorithms_with_wrong_preferences():
    """Test all algorithms with wrong preferences."""
    wake_up = create_time(8)
    sleep = create_time(16)

    obligations = [
        {"start": create_time(10), "end": create_time(14)}
    ]

    tasks = [
        {"task": "Task 1", "duration": 120, "preference": "morning"},
        {"task": "Task 2", "duration": 120, "preference": "morning"}
    ]

    algorithms = [
        ("AC3", ac3_schedule),
        ("Forward Checking", forward_checking_schedule),
        ("Backtracking", backtracking_slot_placement)
    ]

    for name, algorithm in algorithms:
        result = algorithm(wake_up, sleep, obligations, tasks)
        assert result is not None, f"{name} failed to find a schedule"
        assert len(result["tasks"]) == 2
        assert result["preference_respected"] is False
        print(result)

def test_algorithms_with_wrong_schedule():
    """Test all algorithms with wrong schedule."""
    wake_up = create_time(8)
    sleep = create_time(14)

    obligations = [
        {"start": create_time(10), "end": create_time(12)}
    ]

    tasks = [
        {"task": "Task 1", "duration": 240, "preference": "morning"}
    ]

    algorithms = [
        ("AC3", ac3_schedule),
        ("Forward Checking", forward_checking_schedule),
        ("Backtracking", backtracking_slot_placement)
    ]

    for name, algorithm in algorithms:
        result = algorithm(wake_up, sleep, obligations, tasks)
        assert result is None, f"{name} found a wrong schedule"

if __name__ == "__main__":
    test_all_algorithms_with_preferences()
    test_algorithms_with_tight_schedule()
    test_algorithms_with_complex_obligations()
    test_algorithms_performance()
    test_algorithms_with_impossible_schedule()
    test_algorithms_with_wrong_preferences()
    test_algorithms_with_wrong_schedule()
    print("All additional tests passed successfully!")
