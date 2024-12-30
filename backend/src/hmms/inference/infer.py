import torch

from src.core.helpers import (
    get_model, 
    Model, 
    preprocess_inference_sentence, 
    get_indexes_list,
    replace_time_with_number
)

model = None

hmm = None

got_model = False

if not got_model:
    model = get_model()
    print(model.transition_matrix.shape)
    print(model.emission_matrix.shape)
    print(model.state_priors.shape)
    got_model = True

def infer(sentence: str) -> str:
    global model

    original_sentence = sentence

    # Preprocess the sentence
    sentence = preprocess_inference_sentence(sentence)

    print(sentence)

    # print(tensor_sentence_indexes.unsqueeze(0))
    result = model.get_most_likely_state_sequence(sentence)

    result = replace_time_with_number(result, original_sentence, get_placeholder=False)
    
    return result

if __name__ == "__main__":
    sentence = """The time for playing hockey should be twenty-nine hours in the morning"""

    result = infer(sentence)

    print(result)