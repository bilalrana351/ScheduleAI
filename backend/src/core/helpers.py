from typing import List, Union, Tuple, Dict, Optional

import json
import os

from src.hmms.model import Model
from num2words import num2words
from datetime import datetime, timedelta

import random

from src.config import (
    STATES, 
    MODEL_DIR, 
    INDEXES_DIR, 
    UNKNOWN_WORD, 
    DEFAULT_STATE_PRIORS, 
    TIME_WORD_MAPPING,
    TIME_PERIOD_MAPPING
)

from src.hmms.training.templates import TrainingInstance

import torch

from word2number import w2n

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
    words = sentence.lower().split()
    states = [STATES["other"]] * len(words)
    
    # Create a dictionary mapping each word to its state
    word_to_state = {}
    
    # Map action words
    for word in action.lower().split():
        word_to_state[word] = STATES["action"]
        
    # Map duration words
    for word in duration.lower().split():
        word_to_state[word] = STATES["duration"]
        
    # Map preference words
    for word in preference.lower().split():
        word_to_state[word] = STATES["preference"]
        
    # # Map time
    if time:
        word_to_state[str(time).lower()] = STATES["time"]
    
    # Generate states by looking up each word
    result = []
    for word in words:
        state = word_to_state.get(word)
        if word == "<time>":
            result.append(STATES["time"])
        elif state is None:
            result.append(STATES["other"])
        else:
            result.append(state)
    return result

def get_time_converted_sentence(sentence: str, time: str) -> str:
    time_lower_words = str(time).lower().split()
    words = sentence.lower().split()
    
    # Replace the time value with a placeholder
    converted_words = []
    for word in words:
        if word in time_lower_words:
            converted_words.append("<time>")
        else:
            converted_words.append(word)
    
    return " ".join(converted_words)

def find_and_replace_time(sentence: str, get_placeholder: bool = True) -> str:
    words = sentence.split()
    result = []
    i = 0
    
    while i < len(words):
        # Try to identify compound numbers by checking if both words are valid numbers
        if i < len(words) - 1:
            try:
                # Check if both words can be converted to numbers individually
                first_num = w2n.word_to_num(words[i].lower())
                second_num = w2n.word_to_num(words[i+1].lower())
                
                # If both are valid numbers, try combining them
                compound_number = "-".join(words[i:i+2])
                number = w2n.word_to_num(compound_number.lower())
                
                if get_placeholder:
                    result.append("<time>")
                else:
                    result.append(str(number))
                i += 2  # Skip next word since we used it
                continue
            except:
                pass
        
        # If compound number failed, process single word
        if words[i].isdigit():
            if get_placeholder:
                result.append("<time>")
            else:
                result.append(words[i])
        else:
            try:
                number = w2n.word_to_num(words[i].lower())
                if get_placeholder:
                    result.append("<time>")
                else:
                    result.append(str(number))
            except:
                result.append(words[i])
        i += 1

    return " ".join(result)

def is_between_time_period(time, time_period):
    return time_period[0] <= time.hour < time_period[1]

def get_time_to_preference(time):
    if is_between_time_period(time, TIME_PERIOD_MAPPING["M"]):
        return TIME_WORD_MAPPING["M"]
    elif is_between_time_period(time, TIME_PERIOD_MAPPING["A"]):
        return TIME_WORD_MAPPING["A"]
    elif is_between_time_period(time, TIME_PERIOD_MAPPING["E"]):
        return TIME_WORD_MAPPING["E"]
    else:
        return TIME_WORD_MAPPING["N"]

def remove_special_characters(sentence: str, omitted_characters: List[str] = []) -> str:
    stripped_sentence = ''
    for char in sentence:
        if char.isalpha() or char.isdigit() or char == " ":
            stripped_sentence += char
        if char in omitted_characters:
            stripped_sentence += char
    return stripped_sentence

def preprocess_inference_sentence(sentence: str) -> str:
    # Convert the whole sentence to lowercase
    sentence = sentence.lower()

    sentence = remove_special_characters(sentence, omitted_characters=["-"])

    # Remove all dots and commas from the sentence
    sentence = sentence.replace(".", "").replace(",", "")

    sentence = find_and_replace_time(sentence, get_placeholder=True)

    sentence = remove_special_characters(sentence, omitted_characters=["<", ">"])

    return sentence

def preprocess_sentence(sentence: str, action: str, duration: str, preference: str, time: str) -> str:
    sentence = sentence.format(action=action, digit = time, duration=duration, preference=preference)

    # Convert the whole sentence to lowercase
    sentence = sentence.lower()

    stripped_sentence = ''

    for char in sentence:
        if char.isalpha() or char.isdigit() or char == " ":
            stripped_sentence += char

    sentence = stripped_sentence

    # Remove all dots and commas from the sentence
    sentence = sentence.replace(".", "").replace(",", "")
    
    # Convert any instance of the time to a simple placeholder named time
    sentence = get_time_converted_sentence(sentence, time)

    return sentence

def get_index_dict_from_states() -> dict:
    # Get all the values of the STATES dictionary
    values = list(STATES.values())

    # Make a dictionary mapping each value to its index
    value_to_index = {value: index for index, value in enumerate(values)}

    return value_to_index

# This will be used in order to get the indexes of all the training data
def get_index_dict_from_corpus(corpus: List[TrainingInstance]) -> dict:

    index_dict = {}

    index = 0

    for instance in corpus:
        sentence = instance.sentence

        words = sentence.split()

        for word in words:
            if word not in index_dict:
                index_dict[word] = index
                index += 1

    # Now add the NA index
    index_dict[UNKNOWN_WORD] = index

    return index_dict

def get_indexes_list(sequence: str, index_dict: dict) -> List[int]:
    # Convert into a list of words
    words = sequence.split()

    indexes = []

    for word in words:
        if word in index_dict:
            indexes.append(index_dict[word])
        else:
            indexes.append(index_dict[UNKNOWN_WORD])

    return indexes

def add_indexes_to_training_instance(instance: TrainingInstance, word_index_dict: dict, state_index_dict: dict) -> TrainingInstance:
    """
    Add indexes to the sentence and state sequence of a TrainingInstance based on the provided index dictionaries.
    
    Args:
        instance: The TrainingInstance to add indexes to
        word_index_dict: Dictionary mapping words to their indexes
        state_index_dict: Dictionary mapping states to their indexes
        
    Returns:
        TrainingInstance with added indexes for sentence and state sequence
    """
    # Convert sentence words to indexes
    words = instance.sentence.split()
    sentence_indexes = [word_index_dict[word] for word in words]
    
    # Convert state sequence to indexes
    state_sequence_indexes = [state_index_dict[state] for state in instance.state_sequence]
    
    # Add the indexes to the instance
    instance.sentence_indexes = sentence_indexes
    instance.state_sequence_indexes = state_sequence_indexes
    
    return instance

def add_indexes_to_training_corpus(corpus: List[TrainingInstance], word_index_dict: dict, state_index_dict: dict) -> List[TrainingInstance]:
    for instance in corpus:
        add_indexes_to_training_instance(instance, word_index_dict, state_index_dict)

    return corpus

def normalize_matrices(transition_matrix: torch.Tensor, emission_matrix: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Normalize the transition and emission matrices along columns.
    
    Args:
        transition_matrix: Tensor of shape (num_states, num_states)
        emission_matrix: Tensor of shape (vocab_size, num_states)
        
    Returns:
        Tuple of normalized transition and emission matrices
    """
    # Normalize along columns (dim=0)
    transition_matrix = transition_matrix / torch.sum(transition_matrix, dim=0, keepdim=True)
    emission_matrix = emission_matrix / torch.sum(emission_matrix, dim=0, keepdim=True)
    
    return transition_matrix, emission_matrix

def save_matrices(transition_matrix: torch.Tensor, emission_matrix: torch.Tensor) -> str:
    """
    Save transition and emission matrices to JSON files.
    Creates a new run folder if there are already 3 runs.
    
    Args:
        transition_matrix: The transition matrix to save
        emission_matrix: The emission matrix to save
        
    Returns:
        str: The path where matrices were saved
    """
    
    # Convert tensors to lists for JSON serialization
    transition_data = transition_matrix.tolist()
    emission_data = emission_matrix.tolist()
    
    # Check existing runs
    existing_runs = [d for d in os.listdir(MODEL_DIR) if d.startswith('run') and os.path.isdir(os.path.join(MODEL_DIR, d))]
    
    # Create new run folder
    run_number = len(existing_runs) + 1
    run_dir = os.path.join(MODEL_DIR, f'run{run_number}')
    os.makedirs(run_dir, exist_ok=True)
    save_dir = run_dir

    # Save transition matrix
    transition_path = os.path.join(save_dir, 'transition.json')
    with open(transition_path, 'w') as f:
        json.dump(transition_data, f, indent=2)
    
    # Save emission matrix
    emission_path = os.path.join(save_dir, 'emission.json')
    with open(emission_path, 'w') as f:
        json.dump(emission_data, f, indent=2)

    # Save state priors
    state_priors_path = os.path.join(save_dir, 'state_priors.json')
    with open(state_priors_path, 'w') as f:
        json.dump(DEFAULT_STATE_PRIORS, f, indent=2)
    
    return save_dir

def save_indexes(word_index_dict: dict, state_index_dict: dict) -> str:
    """
    Save word and state index dictionaries to JSON files.
    This will override any existing index files.
    
    Args:
        word_index_dict: Dictionary mapping words to their indexes
        state_index_dict: Dictionary mapping states to their indexes
        
    Returns:
        str: The path where indexes were saved
    """
    # Save word index dictionary
    word_index_path = os.path.join(INDEXES_DIR, 'word_index.json')
    with open(word_index_path, 'w') as f:
        json.dump(word_index_dict, f, indent=2)
    
    # Save state index dictionary
    state_index_path = os.path.join(INDEXES_DIR, 'state_index.json')
    with open(state_index_path, 'w') as f:
        json.dump(state_index_dict, f, indent=2)
    
    return INDEXES_DIR

def get_latest_run() -> str:
    """Get the path of the latest run directory."""
    runs = [d for d in os.listdir(MODEL_DIR) if d.startswith('run') and os.path.isdir(os.path.join(MODEL_DIR, d))]
    if not runs:
        raise ValueError("No model runs found")
    
    latest_run = max(runs, key=lambda x: int(x[3:]))  # Extract number from 'runX'
    return os.path.join(MODEL_DIR, latest_run)

def load_matrices(run_number: Optional[int] = None) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Load transition and emission matrices from a specific run or the latest run.
    
    Args:
        run_number: Optional run number to load from. If None, loads from latest run.
        
    Returns:
        Tuple of (transition_matrix, emission_matrix) as PyTorch tensors
    """
    # Determine which run to load from
    if run_number is not None:
        run_dir = os.path.join(MODEL_DIR, f'run{run_number}')
        if not os.path.exists(run_dir):
            raise ValueError(f"Run {run_number} does not exist")
    else:
        run_dir = get_latest_run()
    
    # Load matrices
    with open(os.path.join(run_dir, 'transition.json'), 'r') as f:
        transition_data = json.load(f)
    
    with open(os.path.join(run_dir, 'emission.json'), 'r') as f:
        emission_data = json.load(f)

    with open(os.path.join(run_dir, 'state_priors.json'), 'r') as f:    
        state_priors_data = json.load(f)
    
    # Convert to PyTorch tensors
    transition_matrix = torch.tensor(transition_data, dtype=torch.float32)
    emission_matrix = torch.tensor(emission_data, dtype=torch.float32)
    state_priors = torch.tensor(state_priors_data, dtype=torch.float32)
    
    return transition_matrix, emission_matrix, state_priors

def load_indexes() -> Tuple[Dict[str, int], Dict[str, int], Dict[int, str], Dict[int, str]]:
    """
    Load index dictionaries and create their reverse mappings.
    
    Returns:
        Tuple of (word_index_dict, state_index_dict, reverse_word_index, reverse_state_index)
    """
    # Load word index dictionary
    with open(os.path.join(INDEXES_DIR, 'word_index.json'), 'r') as f:
        word_index_dict = json.load(f)
    
    # Load state index dictionary
    with open(os.path.join(INDEXES_DIR, 'state_index.json'), 'r') as f:
        state_index_dict = json.load(f)
    
    # Create reverse mappings
    reverse_word_index = {v: k for k, v in word_index_dict.items()}
    reverse_state_index = {v: k for k, v in state_index_dict.items()}
    
    return word_index_dict, state_index_dict, reverse_word_index, reverse_state_index

def get_model(run_number: Optional[int] = None) -> Model:
    """
    Load the HMM model matrices and index mappings.
    
    Args:
        run_number: Optional run number to load from. If None, loads from latest run.
        
    Returns:
        Tuple of (
            transition_matrix,
            emission_matrix,
            word_index_dict,
            state_index_dict,
            reverse_word_index,
            reverse_state_index
        )
    """
    # Load matrices from specified run or latest run
    transition_matrix, emission_matrix, state_priors = load_matrices(run_number)
    
    # Load index mappings
    word_index_dict, state_index_dict, reverse_word_index, reverse_state_index = load_indexes()


    return Model(transition_matrix, emission_matrix, word_index_dict, state_index_dict, reverse_word_index, reverse_state_index, state_priors)


def replace_time_with_number(result: Dict[str, List[str]], sentence: str, get_placeholder=False) -> Dict[str, List[str]]:
    # Convert any number words to their corresponding number
    sentence = find_and_replace_time(sentence, get_placeholder=get_placeholder)

    # Replace the special characters in the original sentence
    sentence = remove_special_characters(sentence)

    # Get the words
    words = sentence.split()

    for index, word in enumerate(words):
        if word.isdigit():
            # If the word is a digit
            result['state_sequence_with_words'][index][1] = word

    return result

def split_cross_midnight_obligations(obligations):
    split_obligations = []
    
    for obligation in obligations:
        if obligation['end'] == datetime.strptime("00:00", "%H:%M").time():
            obligation['end'] = datetime.strptime("23:59", "%H:%M").time()

        start_minutes = obligation['start'].hour * 60 + obligation['start'].minute
        end_minutes = obligation['end'].hour * 60 + obligation['end'].minute
        
        if start_minutes > end_minutes:  # Crosses midnight
            # Create first part (from start to midnight)
            midnight = datetime.strptime("23:59", "%H:%M").time()
            split_obligations.append({
                'task': obligation['task'] + " (Part 1)",
                'start': obligation['start'],
                'end': midnight
            })
            
            # Create second part (from midnight to end)
            next_day_start = datetime.strptime("00:00", "%H:%M").time()
            split_obligations.append({
                'task': obligation['task'] + " (Part 2)",
                'start': next_day_start,
                'end': obligation['end']
            })
        else:
            split_obligations.append(obligation)
    
    return split_obligations

def combine_split_obligations(schedule):
    # Group tasks by their base name (removing " (Part 1)" and " (Part 2)")
    task_groups = {}
    for task in schedule:
        base_name = task['task'].replace(" (Part 1)", "").replace(" (Part 2)", "")
        if base_name not in task_groups:
            task_groups[base_name] = []
        task_groups[base_name].append(task)
    
    # Combine split tasks
    combined_schedule = []
    for base_name, tasks in task_groups.items():
        if len(tasks) == 2 and "(Part 1)" in tasks[0]['task'] and "(Part 2)" in tasks[1]['task']:
            # This was a split task, combine it
            combined_schedule.append({
                'task': base_name,
                'start': tasks[0]['start'],
                'end': tasks[1]['end']
            })
        else:
            # This was not a split task, add it as is
            combined_schedule.extend(tasks)
    
    return combined_schedule

def adjust_wakeup_and_sleep(wake_up, sleep):
    # Handle edge case where wake_up and sleep are the same time
    if wake_up == sleep:
        return []
    
    # Check if the sleep time is 00:00
    if sleep == datetime.strptime("00:00", "%H:%M").time():
        sleep = datetime.strptime("23:59", "%H:%M").time()
        
    # Handle normal case where wake up is before sleep time
    if wake_up > sleep:
        return [{"start": sleep, "end": wake_up}]
        
    # Handle case where sleep time is before wake up (crosses midnight)
    elif wake_up < sleep:
        midnight_end = datetime.strptime("23:59", "%H:%M").time()
        midnight_start = datetime.strptime("00:00", "%H:%M").time()

        # If either of the sleep, midnight end or the midnight start or the wake up overlap then they should not be scheduled
        if sleep == midnight_end:
            return [{"start": midnight_start, "end": wake_up}]
        
        if wake_up == midnight_start:
            return [{"start": sleep, "end": midnight_end}]

        # Return two time periods:
        # 1. From sleep time to midnight
        # 2. From midnight to wake up time
        return [
            {"start": sleep, "end": midnight_end},
            {"start": midnight_start, "end": wake_up}
        ]


def get_available_slots(timeline):
    """
    Returns time slots that are not covered in the timeline.
    
    Args:
        timeline: List of dicts with 'start' and 'end' times
        
    Returns:
        List of dicts with 'start' and 'end' times representing available slots
    """
    if not timeline:
        return []
        
    # Sort timeline by start time
    sorted_timeline = sorted(timeline, key=lambda x: x['start'])
    
    # Initialize result list
    available_slots = []
    
    # Get the full day boundaries
    day_start = datetime.strptime("00:00", "%H:%M").time()
    day_end = datetime.strptime("23:59", "%H:%M").time()
    
    # Check if there's a gap at the start of the day
    if sorted_timeline[0]['start'] != day_start:
        available_slots.append({
            'start': day_start,
            'end': sorted_timeline[0]['start']
        })
    
    # Check for gaps between timeline slots
    for i in range(len(sorted_timeline) - 1):
        current_end = sorted_timeline[i]['end']
        next_start = sorted_timeline[i + 1]['start']
        
        if current_end != next_start:
            available_slots.append({
                'start': current_end,
                'end': next_start
            })
    
    # Check if there's a gap at the end of the day
    if sorted_timeline[-1]['end'] != day_end:
        available_slots.append({
            'start': sorted_timeline[-1]['end'],
            'end': day_end
        })
    
    return available_slots

if __name__ == "__main__":
    pass