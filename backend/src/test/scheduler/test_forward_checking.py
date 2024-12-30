import pytest
from datetime import datetime, time
from src.schedulers.forward_checking import forward_checking_schedule, generate_domains, filter_domain_by_preference

def create_time(hour, minute=0):
    return datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()

class TestForwardCheckingScheduler:
    @pytest.fixture
    def basic_schedule_params(self):
        return {
            'wake_up': create_time(8),
            'sleep': create_time(22),
            'obligations': [],
            'tasks': [
                {"task": "Task 1", "duration": 60},  # 1 hour
                {"task": "Task 2", "duration": 120}  # 2 hours
            ]
        }

    def test_basic_scheduling(self, basic_schedule_params):
        """Test basic scheduling with no obligations and simple tasks."""
        result = forward_checking_schedule(**basic_schedule_params)
        assert result is not None
        assert result["preference_respected"] is True
        assert len(result["tasks"]) == 2

    def test_tight_schedule(self):
        """Test scheduling with very tight time constraints."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(12),  # Only 4 hours available
            'obligations': [],
            'tasks': [
                {"task": "Task 1", "duration": 120},  # 2 hours
                {"task": "Task 2", "duration": 120}   # 2 hours
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is not None
        assert len(result["tasks"]) == 2

    def test_impossible_schedule(self):
        """Test when tasks cannot fit in the available time."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(10),  # Only 2 hours available
            'obligations': [],
            'tasks': [
                {"task": "Task 1", "duration": 180}  # 3 hours
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is None

    def test_with_obligations(self):
        """Test scheduling with obligations breaking up the day."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(22),
            'obligations': [
                {
                    "start": create_time(12),
                    "end": create_time(14)
                }
            ],
            'tasks': [
                {"task": "Task 1", "duration": 120},  # 2 hours
                {"task": "Task 2", "duration": 120}   # 2 hours
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is not None
        assert len(result["tasks"]) == 2

    def test_with_preferences(self):
        """Test scheduling with time preferences."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(22),
            'obligations': [],
            'tasks': [
                {"task": "Morning Task", "duration": 120, "preference": "morning"},
                {"task": "Evening Task", "duration": 120, "preference": "evening"}
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is not None
        assert result["preference_respected"] is True
        
        # Verify morning task is scheduled in the morning
        morning_task = next(task for task in result["tasks"] if task["task"] == "Morning Task")
        assert morning_task["start"].hour < 12

    def test_preference_fallback(self):
        """Test that scheduler falls back when preferences cannot be respected."""
        params = {
            'wake_up': create_time(13),  # Wake up in afternoon
            'sleep': create_time(22),
            'obligations': [],
            'tasks': [
                {"task": "Morning Task", "duration": 120, "preference": "morning"}  # Can't be scheduled in morning
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is not None
        assert result["preference_respected"] is False

    def test_overlapping_obligations(self):
        """Test handling of overlapping obligations."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(22),
            'obligations': [
                {"start": create_time(10), "end": create_time(14)},
                {"start": create_time(13), "end": create_time(16)}  # Overlaps with previous
            ],
            'tasks': [
                {"task": "Task 1", "duration": 120}
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is not None
        assert len(result["tasks"]) == 1

    def test_edge_case_exact_fit(self):
        """Test when tasks fit exactly in available time."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(10),  # 2 hours available
            'obligations': [],
            'tasks': [
                {"task": "Task 1", "duration": 120}  # Exactly 2 hours
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is not None
        assert len(result["tasks"]) == 1

    def test_multiple_preferences_same_time(self):
        """Test handling multiple tasks with same time preference."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(22),
            'obligations': [],
            'tasks': [
                {"task": "Morning Task 1", "duration": 120, "preference": "morning"},
                {"task": "Morning Task 2", "duration": 120, "preference": "morning"},
                {"task": "Morning Task 3", "duration": 120, "preference": "morning"}
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is not None
        # Not all tasks might get their preferred time, but schedule should be found
        assert len(result["tasks"]) == 3

    def test_domain_generation(self):
        """Test domain generation function."""
        timeline = [{"start": create_time(8), "end": create_time(12)}]
        tasks = [{"task": "Task 1", "duration": 60}]
        domains = generate_domains(timeline, tasks)
        assert "Task 1" in domains
        assert len(domains["Task 1"]) > 0

    def test_preference_filtering(self):
        """Test preference filtering function."""
        domain = [
            (create_time(8), create_time(10)),   # Morning
            (create_time(13), create_time(15)),  # Afternoon
            (create_time(19), create_time(21))   # Evening
        ]
        filtered = filter_domain_by_preference(domain, "morning")
        assert len(filtered) == 1
        assert filtered[0][0].hour < 12

    def test_forward_checking_efficiency(self):
        """Test that forward checking prunes invalid domains early."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(12),  # 4 hours
            'obligations': [],
            'tasks': [
                {"task": "Task 1", "duration": 120},  # 2 hours
                {"task": "Task 2", "duration": 120},  # 2 hours
                {"task": "Task 3", "duration": 60}    # 1 hour - should fail early
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is None  # Should fail quickly due to forward checking

    def test_domain_wipeout(self):
        """Test handling of domain wipeout during forward checking."""
        params = {
            'wake_up': create_time(8),
            'sleep': create_time(14),  # 6 hours
            'obligations': [
                {"start": create_time(10), "end": create_time(12)}  # 2-hour obligation
            ],
            'tasks': [
                {"task": "Task 1", "duration": 180},  # 3 hours
                {"task": "Task 2", "duration": 180}   # 3 hours - should cause domain wipeout
            ]
        }
        result = forward_checking_schedule(**params)
        assert result is None  # Should fail due to domain wipeout 