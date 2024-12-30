from src.hmms.training.get_training_data_code import get_training_data_cartesian

from src.hmms.training.templates import TrainingInstance

from src.core.helpers import (
    get_index_dict_from_corpus, get_index_dict_from_states, add_indexes_to_training_corpus, normalize_matrices, save_matrices, save_indexes
)

import torch
from typing import Tuple

def train_hmm(na_normalizing_alpha: int = 0.05) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Train an HMM model using the training data.
    
    Returns:
        Tuple of (transition_matrix, emission_matrix) as PyTorch tensors
    """
    training_instances = get_training_data_cartesian()

    word_index_dict = get_index_dict_from_corpus(training_instances)    
    state_index_dict = get_index_dict_from_states()

    # Add the index representation of the sentence and the state sequence
    training_instances = add_indexes_to_training_corpus(training_instances, word_index_dict, state_index_dict)

    # Make tensors for transition and emission matrices
    transition_matrix = torch.zeros((len(state_index_dict), len(state_index_dict)), dtype=torch.float32)
    emission_matrix = torch.zeros((len(word_index_dict), len(state_index_dict)), dtype=torch.float32)

    # Start to iterate over the training corpus
    for instance in training_instances:
        sentence_indexes = instance.sentence_indexes
        state_sequence_indexes = instance.state_sequence_indexes

        # Populate the transition matrix
        for i in range(len(state_sequence_indexes) - 1):
            transition_matrix[state_sequence_indexes[i + 1]][state_sequence_indexes[i]] += 1
        
        # Populate the emission matrix
        for i in range(len(sentence_indexes)):
            emission_matrix[sentence_indexes[i]][state_sequence_indexes[i]] += 1

    # Take the sum of the emission matrix along the columns, will be used for estimating the NA State 
    emission_matrix_sum = torch.sum(emission_matrix, dim=0)

    # At the end, we know that the last index is the NA state, we assign its emission matrices values as follows:
    # We assign the emission matrix values according to the most likely states
    emission_matrix[emission_matrix.shape[0] - 1] = emission_matrix_sum * na_normalizing_alpha # JUst so that it does not effect the values that much


    # # Normalize the matrices
    transition_matrix, emission_matrix = normalize_matrices(transition_matrix, emission_matrix)

    # Verify the matrices are properly normalized
    assert torch.allclose(torch.sum(transition_matrix, dim=0), torch.ones(len(state_index_dict))), "Transition matrix columns do not sum to 1"
    assert torch.allclose(torch.sum(emission_matrix, dim=0), torch.ones(len(state_index_dict))), "Emission matrix columns do not sum to 1"

    # Save the index dictionaries
    indexes_dir = save_indexes(word_index_dict, state_index_dict)
    print(f"Indexes saved in: {indexes_dir}")
    
    # Save the matrices
    save_dir = save_matrices(transition_matrix, emission_matrix)
    print(f"Matrices saved in: {save_dir}")

    return transition_matrix, emission_matrix

if __name__ == "__main__":
    transition_matrix, emission_matrix = train_hmm(na_normalizing_alpha=0.05)