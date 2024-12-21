from src.hmms.training.templates import TrainingInstance

from typing import List

from src.config import ACTIONS, DURATIONS, PREFERENCES, SENTENCES

import random

from src.core.helpers import get_time_from_duration, get_state_sequence, get_time_converted_sentence, preprocess_sentence

from itertools import product

def generate_training_sample_random():
    action = random.choice(ACTIONS)
    duration = random.choice(DURATIONS)
    preference = random.choice(PREFERENCES)
    sentence = random.choice(SENTENCES)
    time = get_time_from_duration(duration)

    sentence = preprocess_sentence(sentence, action, duration, preference, time)

    sequences = get_state_sequence(sentence, action, duration, preference, time)
    
    return TrainingInstance(sentence=sentence, state_sequence=sequences)

# Get the training data at random
def get_training_data_random(n_samples: int = 100) -> List[TrainingInstance]:
    print("Generating training data...")

    instances = []

    for _ in range(n_samples):
        instances.append(generate_training_sample_random())

    return instances

# Get the training data by taking a cartesian product of all the possible combinations of the actions, preferences, durations, sentences, however time can be random
def get_training_data_cartesian() -> List[TrainingInstance]:
    """
    Get training data by taking a cartesian product of all possible combinations of 
    actions, preferences, durations, and sentences. Time is generated randomly for each combination.
    
    Returns:
        List[TrainingInstance]: List of training instances with sentences and their state sequences
    """
    print("Generating training data using cartesian product...")
    
    instances = []
    
    # Generate all possible combinations using itertools.product
    combinations = product(ACTIONS, DURATIONS, PREFERENCES, SENTENCES)
    
    # Process each combination
    for action, duration, preference, sentence in combinations:
        # Get random time based on duration
        time = get_time_from_duration(duration)
        
        # Preprocess the sentence with the current combination
        sentence = preprocess_sentence(sentence=sentence, 
                                    action=action,
                                    duration=duration, 
                                    preference=preference,
                                    time=time)
        
        # Get state sequence for this combination
        sequences = get_state_sequence(sentence=sentence,
                                    action=action,
                                    duration=duration,
                                    preference=preference,
                                    time=time)
        
        # Create and append the training instance
        instances.append(TrainingInstance(sentence=sentence, 
                                       state_sequence=sequences))
    
    return instances


if __name__ == "__main__":
    instances = get_training_data_random(n_samples=10)
    print("Instances: ", instances)
