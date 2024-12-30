import requests
import json
from datetime import datetime
import pytest
from src.config import SERVER_URL

def create_test_payload():
    """Create sample payload for testing the scheduling endpoints"""
    return {
        "wake_up_time": "08:00",
        "sleep_time": "22:00",
        "obligations": [
            {
                "task": "Meeting 1",
                "start": "10:00",
                "end": "11:00"
            },
            {
                "task": "Meeting 2",
                "start": "14:00",
                "end": "15:00"
            }
        ],
        "regular_tasks": [
            {"task": "Study", "duration": 120},
            {"task": "Exercise", "duration": 60},
            {"task": "Read", "duration": 90}
        ]
    }

def test_schedule_endpoint():
    """Test all scheduling algorithms"""
    algorithms = ['ac3', 'forward_check', 'backward', 'greedy']
    payload = create_test_payload()
    
    print("\nTesting scheduling endpoints:")
    for algo in algorithms:
        print(f"\nTesting {algo} algorithm:")
        try:
            response = requests.post(f"{SERVER_URL}/schedule/{algo}", json=payload)
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("\nScheduled Tasks:")
                for task in result['schedule']:
                    print(f"- {task['task']}: {task['start']} to {task['end']}")
                
                print("\nObligations:")
                for obligation in result['obligations']:
                    print(f"- {obligation['task']}: {obligation['start']} to {obligation['end']}")
            else:
                print(f"Error: {response.json()['error']}")
                
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to server at {SERVER_URL}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 50)

def verify_schedule(schedule):
    """Verify that the schedule is valid"""
    # Convert times to minutes since midnight for easier comparison
    def time_to_minutes(time_str):
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    # Check for overlapping tasks
    tasks = [(task['task'], time_to_minutes(task['start']), time_to_minutes(task['end'])) 
            for task in schedule]
    
    for i, task1 in enumerate(tasks):
        for task2 in tasks[i+1:]:
            if not (task1[2] <= task2[1] or task2[2] <= task1[1]):
                return False, f"Tasks {task1[0]} and {task2[0]} overlap"
    
    return True, "Schedule is valid"

if __name__ == "__main__":
    test_schedule_endpoint()