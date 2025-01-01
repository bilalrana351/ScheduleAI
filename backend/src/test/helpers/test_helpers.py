from src.core.helpers import (
    get_state_sequence,
    get_time_converted_sentence,
    get_time_from_duration,
    handle_hours,
    handle_minutes,
    handle_days,
    get_index_dict_from_corpus,
    get_index_dict_from_states,
    add_indexes_to_training_instance,
    add_indexes_to_training_corpus,
    normalize_matrices,
    find_and_replace_time,
    get_available_slots
)

from datetime import datetime

from src.config import STATES

from src.config import ACTIONS, DURATIONS, PREFERENCES, SENTENCES

from src.hmms.training.templates import TrainingInstance

import torch

def test_get_state_sequence():
    # Test case 1: Simple sentence with all components
    assert get_state_sequence(
        sentence="I want to wake up for five hours in the morning",
        action="wake up",
        duration="hours",
        preference="morning",
        time="five"
    ) == ["O", "O", "O", "A", "A", "O", "T", "D", "O", "O", "P"]

    assert get_state_sequence(
        sentence="I want to wake up for five hours in the night",
        action="wake up",
        duration="hours",
        preference="night",
        time="five"
    ) == ["O", "O", "O", "A", "A", "O", "T", "D", "O", "O", "P"]

def test_get_time_converted_sentence():
    # Test with numeric time
    sentence = "I want to sleep for 5 hours"
    result = get_time_converted_sentence(sentence, "5")
    assert result == "i want to sleep for <TIME> hours"
    
    # Test with word time
    sentence = "I want to sleep for five fourty minutes"
    result = get_time_converted_sentence(sentence, "five fourty")

    assert result == "i want to sleep for <TIME> <TIME> minutes"
    
    # Test with no time in sentence
    sentence = "I want to sleep"
    result = get_time_converted_sentence(sentence, "5")
    assert result == "i want to sleep"

def test_handle_hours():
    # Test numeric output
    result = handle_hours(1)
    assert isinstance(result, int)
    assert result >= 1 and result <= 23
    
    # Test word output
    result = handle_hours(0)
    assert isinstance(result, str)

def test_handle_minutes():
    # Test numeric output
    result = handle_minutes(1)
    assert isinstance(result, int)
    assert result >= 1 and result <= 59
    
    # Test word output
    result = handle_minutes(0)
    assert isinstance(result, str)

def test_handle_days():
    # Test numeric output
    result = handle_days(1)
    assert isinstance(result, int)
    assert result >= 1 and result <= 30
    
    # Test word output
    result = handle_days(0)
    assert isinstance(result, str)

def test_get_time_from_duration():
    # Test various duration inputs
    result = get_time_from_duration("minutes")
    assert isinstance(result, (str, int))
    
    result = get_time_from_duration("hours")
    assert isinstance(result, (str, int))
    
    result = get_time_from_duration("days")
    assert isinstance(result, (str, int))
    
    # Test invalid duration
    try:
        get_time_from_duration("invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        assert True

def test_get_index_dict_from_corpus():
    from src.hmms.training.get_training_data_code import get_training_data_cartesian
    corpus = get_training_data_cartesian()
    index_dict = get_index_dict_from_corpus(corpus)
    assert isinstance(index_dict, dict)
    assert len(index_dict) > 0

    # Iterate over the corpus, if we cannot find a word in the index_dict, raise an error
    for instance in corpus:
        for word in instance.sentence.split():
            if word not in index_dict:
                raise ValueError(f"Word {word} not found in index_dict")

    print("Index dict test passed successfully!")

def test_get_index_dict_from_states():
    state_index_dict = get_index_dict_from_states()
    assert isinstance(state_index_dict, dict)
    assert len(state_index_dict) == len(STATES)
    
    # Check if all states from STATES are in the index dict
    for state in STATES.values():
        assert state in state_index_dict
        assert isinstance(state_index_dict[state], int)
        assert state_index_dict[state] >= 0

def test_add_indexes_to_training_instance():
    # Create a sample training instance
    instance = TrainingInstance(
        sentence="i want to sleep for five hours",
        state_sequence=["O", "O", "O", "A", "O", "T", "D"]
    )
    
    # Create sample index dictionaries
    word_index_dict = {
        "i": 0, "want": 1, "to": 2, "sleep": 3,
        "for": 4, "five": 5, "hours": 6
    }
    state_index_dict = {"O": 0, "A": 1, "T": 2, "D": 3}
    
    # Add indexes to the instance
    instance = add_indexes_to_training_instance(instance, word_index_dict, state_index_dict)
    
    # Verify the results
    assert instance.sentence_indexes == [0, 1, 2, 3, 4, 5, 6]
    assert instance.state_sequence_indexes == [0, 0, 0, 1, 0, 2, 3]

def test_add_indexes_to_training_corpus():
    # Create a sample corpus
    corpus = [
        TrainingInstance(
            sentence="i want to sleep sleep",
            state_sequence=["O", "O", "O", "D", "O"]
        ),
        TrainingInstance(
            sentence="sleep for five hours",
            state_sequence=["A", "O", "T", "D"]
        )
    ]
    
    # Create sample index dictionaries
    word_index_dict = {
        "i": 0, "want": 1, "to": 2, "sleep": 3,
        "for": 4, "five": 5, "hours": 6
    }
    state_index_dict = {"O": 0, "A": 1, "T": 2, "D": 3}
    
    # Add indexes to the corpus
    corpus = add_indexes_to_training_corpus(corpus, word_index_dict, state_index_dict)
    
    # Verify the results
    assert corpus[0].sentence_indexes == [0, 1, 2, 3, 3]
    assert corpus[0].state_sequence_indexes == [0, 0, 0, 3, 0]
    assert corpus[1].sentence_indexes == [3, 4, 5, 6]
    assert corpus[1].state_sequence_indexes == [1, 0, 2, 3]

def test_training_instance_defaults():
    # Create a training instance without indexes
    instance = TrainingInstance(
        sentence="i want to sleep",
        state_sequence=["O", "O", "O", "A"]
    )
    
    # Verify that indexes are empty lists by default
    assert instance.sentence_indexes == []
    assert instance.state_sequence_indexes == []
    
    # Verify that we can still set them manually
    instance.sentence_indexes = [0, 1, 2, 3]
    instance.state_sequence_indexes = [0, 0, 0, 1]
    assert instance.sentence_indexes == [0, 1, 2, 3]
    assert instance.state_sequence_indexes == [0, 0, 0, 1]

def test_normalize_matrices():
    # Create sample transition matrix (3x3)
    transition_matrix = torch.tensor([
        [2., 1., 5.],  # Column sums to 10
        [3., 4., 0.],  # Column sums to 5
        [5., 0., 5.],  # Column sums to 10
    ])
    
    # Create sample emission matrix (4x3)
    emission_matrix = torch.tensor([
        [2., 3., 7.],  # Column sums to 4
        [3., 3., 0.],  # Column sums to 6
        [0., 1., 1.],  # Column sums to 2
        [5., 3., 2.],  # Column sums to 6
    ])
    
    # Normalize matrices
    norm_transition, norm_emission = normalize_matrices(transition_matrix, emission_matrix)
    
    # Test transition matrix normalization
    expected_transition = torch.tensor([
        [0.2, 0.2, 0.5],
        [0.3, 0.8, 0.0],
        [0.5, 0.0, 0.5]
    ])
    assert torch.allclose(norm_transition, expected_transition)
    
    # Test emission matrix normalization
    expected_emission = torch.tensor([
        [0.2, 0.3, 0.7],
        [0.3, 0.3, 0.0],
        [0.0, 0.1, 0.1],
        [0.5, 0.3, 0.2]
    ])
    assert torch.allclose(norm_emission, expected_emission)
    
    # Verify column sums equal 1
    assert torch.allclose(torch.sum(norm_transition, dim=0), torch.ones(3))
    assert torch.allclose(torch.sum(norm_emission, dim=0), torch.ones(3))

def test_find_and_replace_time():
    # Test numeric digits
    assert find_and_replace_time("meet at 5") == "meet at <time>"
    assert find_and_replace_time("call me at 23") == "call me at <time>"
    assert find_and_replace_time("wake up at 7 30") == "wake up at <time> <time>"
    
    # Test number words
    assert find_and_replace_time("meet at five") == "meet at <time>"
    assert find_and_replace_time("call me at twenty three") == "call me at <time> <time>"
    
    assert find_and_replace_time("wake up at seven thirty") == "wake up at <time> <time>"
    assert find_and_replace_time("schedule for twenty-three") == "schedule for <time>"
    


def test_get_available_slots_empty_timeline():
    """Test with empty timeline"""
    assert get_available_slots([]) == []

def test_get_available_slots_single_slot():
    """Test with a single slot in the middle of the day"""
    timeline = [{
        'start': datetime.strptime("10:00", "%H:%M").time(),
        'end': datetime.strptime("14:00", "%H:%M").time()
    }]
    
    expected = [
        {
            'start': datetime.strptime("00:00", "%H:%M").time(),
            'end': datetime.strptime("10:00", "%H:%M").time()
        },
        {
            'start': datetime.strptime("14:00", "%H:%M").time(),
            'end': datetime.strptime("23:59", "%H:%M").time()
        }
    ]
    
    assert get_available_slots(timeline) == expected

def test_get_available_slots_multiple_slots():
    """Test with multiple slots with gaps"""
    timeline = [
        {
            'start': datetime.strptime("09:00", "%H:%M").time(),
            'end': datetime.strptime("10:00", "%H:%M").time()
        },
        {
            'start': datetime.strptime("12:00", "%H:%M").time(),
            'end': datetime.strptime("13:00", "%H:%M").time()
        },
        {
            'start': datetime.strptime("15:00", "%H:%M").time(),
            'end': datetime.strptime("16:00", "%H:%M").time()
        }
    ]
    
    expected = [
        {
            'start': datetime.strptime("00:00", "%H:%M").time(),
            'end': datetime.strptime("09:00", "%H:%M").time()
        },
        {
            'start': datetime.strptime("10:00", "%H:%M").time(),
            'end': datetime.strptime("12:00", "%H:%M").time()
        },
        {
            'start': datetime.strptime("13:00", "%H:%M").time(),
            'end': datetime.strptime("15:00", "%H:%M").time()
        },
        {
            'start': datetime.strptime("16:00", "%H:%M").time(),
            'end': datetime.strptime("23:59", "%H:%M").time()
        }
    ]
    
    assert get_available_slots(timeline) == expected

def test_get_available_slots_full_day():
    """Test with a slot covering the entire day"""
    timeline = [{
        'start': datetime.strptime("00:00", "%H:%M").time(),
        'end': datetime.strptime("23:59", "%H:%M").time()
    }]
    
    assert get_available_slots(timeline) == []

def test_get_available_slots_adjacent_slots():
    """Test with adjacent slots with no gaps"""
    timeline = [
        {
            'start': datetime.strptime("09:00", "%H:%M").time(),
            'end': datetime.strptime("12:00", "%H:%M").time()
        },
        {
            'start': datetime.strptime("12:00", "%H:%M").time(),
            'end': datetime.strptime("15:00", "%H:%M").time()
        }
    ]
    
    expected = [
        {
            'start': datetime.strptime("00:00", "%H:%M").time(),
            'end': datetime.strptime("09:00", "%H:%M").time()
        },
        {
            'start': datetime.strptime("15:00", "%H:%M").time(),
            'end': datetime.strptime("23:59", "%H:%M").time()
        }
    ]
    
    assert get_available_slots(timeline) == expected


def run_all_tests():
    # test_get_state_sequence()
    # test_get_time_converted_sentence()
    # test_handle_hours()
    # test_handle_minutes()
    # test_handle_days()
    # test_get_time_from_duration()
    # test_get_index_dict_from_corpus()
    # test_get_index_dict_from_states()
    # test_add_indexes_to_training_instance()
    # test_add_indexes_to_training_corpus()
    # test_training_instance_defaults()
    # test_normalize_matrices()
    # test_find_and_replace_time()
    test_get_available_slots_empty_timeline()
    test_get_available_slots_single_slot()
    test_get_available_slots_multiple_slots()
    test_get_available_slots_full_day()
    test_get_available_slots_adjacent_slots()
    print("All tests passed successfully!")

if __name__ == "__main__":
    run_all_tests()