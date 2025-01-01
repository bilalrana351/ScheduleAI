str_ = """
{
    "wake_up_time": "05:00", "sleep_time": "23:00", 'obligations': [{'task': 'College', 'start': '09:00', 'end': '17:00'}, {'task': 'Lunch', 'start': '13:00', 'end': '14:00'}, {'task': 'Dinner', 'start': '21:00', 'end': '22:00'}, {'task': 'Breakfast', 'start': '08:00', 'end': '09:00'}], 'regular_tasks': [{'task': 'code', 'duration': 420, 'preference': ''}, {'task': 'have fun', 'duration': 60, 'preference': 'evening'}]}

"""


print(str_.replace("'", '"'))