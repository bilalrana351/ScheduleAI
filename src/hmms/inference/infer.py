import torch

from src.core.helpers import get_model, Model, preprocess_inference_sentence, get_indexes_list

from src.hmms.model import HMM

model = None

hmm = None

got_model = False

if not got_model:
    model = get_model()
    print(model.transition_matrix.shape)
    print(model.emission_matrix.shape)
    print(model.state_priors.shape)
    hmm = HMM.from_pretrained(model.transition_matrix, model.emission_matrix, model.state_priors, model.word_index_dict, model.state_index_dict, model.reverse_word_index, model.reverse_state_index)
    got_model = True

def infer(sentence: str) -> str:
    global model
    global hmm

    print(model)

    # Preprocess the sentence
    sentence = preprocess_inference_sentence(sentence)

    print(sentence)

    # Convert the sentence into indexes
    sentence_indexes = get_indexes_list(sentence, model.word_index_dict)

    tensor_sentence_indexes = torch.tensor(sentence_indexes)

    print(tensor_sentence_indexes.unsqueeze(0).shape)

    # print(tensor_sentence_indexes.unsqueeze(0))
    print(hmm.viterbi(tensor_sentence_indexes.unsqueeze(0), torch.tensor([len(sentence_indexes)])))

if __name__ == "__main__":
    infer("my goal is to apply for a job for 5 minutes this morning")