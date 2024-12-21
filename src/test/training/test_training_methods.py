
from src.hmms.training.get_training_data_code import get_training_data_cartesian, TrainingInstance
from src.config import ACTIONS, DURATIONS, PREFERENCES, SENTENCES

def test_training_data_cartesian():
    result = get_training_data_cartesian()
    assert isinstance(result, list)
    assert len(result) > 0

    print("Length of result: ", len(result))
    print("Length of ACTIONS: ", len(ACTIONS))
    print("Length of DURATIONS: ", len(DURATIONS))
    print("Length of PREFERENCES: ", len(PREFERENCES))
    print("Length of SENTENCES: ", len(SENTENCES))

    # Check the length of the result is the same as the number of combinations
    assert len(result) == len(ACTIONS) * len(DURATIONS) * len(PREFERENCES) * len(SENTENCES)

    # Check the first element of the result is a TrainingInstance
    assert isinstance(result[0], TrainingInstance)

    print("Training data cartesian test passed successfully!")

if __name__ == "__main__":
    test_training_data_cartesian()