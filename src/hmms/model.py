from typing import Dict, List

from src.hmms.training.get_training_data_code import TrainingInstance

from src.hmms.training.train_hmm import train_hmm

import torch

class Model:
    def __init__(self, transition_matrix: torch.Tensor = None, 
                 emission_matrix: torch.Tensor = None, 
                 word_index_dict: Dict[str, int] = None, 
                 state_index_dict: Dict[str, int] = None, 
                 reverse_word_index: Dict[int, str] = None, 
                 reverse_state_index: Dict[int, str] = None, 
                 state_priors: torch.Tensor = None):
        self.transition_matrix = transition_matrix
        self.emission_matrix = emission_matrix
        self.word_index_dict = word_index_dict
        self.state_index_dict = state_index_dict
        self.reverse_word_index = reverse_word_index
        self.reverse_state_index = reverse_state_index
        self.state_priors = state_priors

    # This will be used to train the model
    def train(self, training_data: List[TrainingInstance]):
        pass