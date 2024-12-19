from typing import List, Union

import json

from num2words import num2words

import random

from src.config import ACTIONS, DURATIONS, PREFERENCES

def handle_hours(num_or_value: int) -> Union[str, int]:
    value = random.randint(1, 23)
    
    if num_or_value == 0:
        return num2words(value)
    else:
        return value
    
def handle_minutes(num_or_value: int) -> Union[str, int]:
    value = random.randint(1, 59)
    
    if num_or_value == 0:
        return num2words(value)
    else:
        return value
    
def handle_days(num_or_value: int) -> Union[str, int]:
    value = random.randint(1, 30)
    
    if num_or_value == 0:
        return num2words(value)
    else:
        return value

def get_action_list_from_str(action_str: str) -> List[str]:
    return ["A"] * len(action_str.split(" "))

def get_duration_list_from_str(duration_str: str) -> List[str]:
    return ["D"] * len(duration_str.split(" "))

def get_preference_list_from_str(preference_str: str) -> List[str]:
    return ["P"] * len(preference_str.split(" "))

def get_time_from_duration(duration: str) -> str:
    number_or_value = random.randint(0, 1)

    if duration == "minutes":
        return handle_minutes(number_or_value)
    elif duration == "hours":
        return handle_hours(number_or_value)
    elif duration == "days":
        return handle_days(number_or_value)
    elif duration == "day":
        return handle_days(number_or_value)
    elif duration == "hour":
        return handle_hours(number_or_value)
    elif duration == "minute":
        return handle_minutes(number_or_value)
    else:
        raise ValueError(f"Invalid duration: {duration}")
    
def get_state_sequence(sentence: str, action: str, duration: str, preference: str, time: str) -> List[str]:
    words = sentence.split(" ")

    return words