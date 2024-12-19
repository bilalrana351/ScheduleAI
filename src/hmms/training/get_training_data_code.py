from src.hmms.training.templates import TrainingInstance, TrainingData

from typing import List

import src.config as config

import random

from src.core.helpers import get_time_from_duration, get_state_sequence

def get_training_data(n_samples: int = 100) -> List[TrainingInstance]:
    print("Generating training data...")

    actions = config.ACTIONS
    durations = config.DURATIONS
    preferences = config.PREFERENCES
    sentences = config.SENTENCES

    instances = []

    for _ in range(n_samples):
        action = random.choice(actions)
        duration = random.choice(durations)
        preference = random.choice(preferences)
        sentence = random.choice(sentences)
        time = get_time_from_duration(duration)

        sentence = sentence.format(action=action, digit = time, duration=duration, preference=preference)
        
        sequences = get_state_sequence(sentence, action, duration, preference, time)
        
        instances.append(TrainingInstance(sentence=sentence, state_sequence=sequences))

    return instances

if __name__ == "__main__":
    instances = get_training_data(n_samples=10)
    print("Instances: ", instances)
