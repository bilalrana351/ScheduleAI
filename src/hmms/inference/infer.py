import torch

from src.core.helpers import get_model, Model, preprocess_inference_sentence, get_indexes_list

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

    # Preprocess the sentence
    sentence = preprocess_inference_sentence(sentence)

    # print(tensor_sentence_indexes.unsqueeze(0))
    print(model.get_most_likely_state_sequence(sentence))

if __name__ == "__main__":
    sentence = """The time for playing hockey should be ten hours, 
    then I would love to play some cricket for ten hours. 
    then I would be done for the day.
    some coffee too in the evening and in the morning."""

    sentences = sentence.split("\n")

    for sentence in sentences:
        infer(sentence)