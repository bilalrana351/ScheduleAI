from typing import Dict, List
import torch
from src.config import UNKNOWN_WORD


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

    def get_most_likely_state_sequence(self, sentence: str) -> List[str]:
        """
        Implements the Viterbi algorithm to find the most likely sequence of states
        given an observation sequence (sentence).
        
        Args:
            sentence: A preprocessed sentence string
            
        Returns:
            A list of state labels corresponding to each word in the sentence
        """
        # Convert sentence to word indices
        words = sentence.split()
        word_indices = []
        for word in words:
            if word in self.word_index_dict:
                word_indices.append(self.word_index_dict[word])
            else:
                # Handle unknown words with a special token index
                word_indices.append(self.word_index_dict.get(UNKNOWN_WORD))
        
        # Initialize variables
        num_states = len(self.state_index_dict)
        T = len(word_indices)
        
        # Initialize the viterbi matrix (T x num_states) and backpointer matrix
        viterbi = torch.zeros((T, num_states))
        backpointer = torch.zeros((T, num_states), dtype=torch.long)
        
        # Initialize first timestep using state priors and emission probabilities
        first_word_idx = word_indices[0]
        viterbi[0] = torch.log(self.state_priors) + torch.log(self.emission_matrix[first_word_idx])
        
        # Forward pass
        for t in range(1, T):
            word_idx = word_indices[t]
            for s in range(num_states):
                # Calculate emission probability for current state and word
                emission_prob = torch.log(self.emission_matrix[word_idx][s])
                
                # Calculate transition probabilities to current state
                transition_probs = torch.log(self.transition_matrix[s,:]) + viterbi[t-1]
                
                # Find the maximum probability and its corresponding previous state
                max_prob, prev_state = torch.max(transition_probs, dim=0)
                
                # Store the probability and backpointer
                viterbi[t][s] = emission_prob + max_prob
                backpointer[t][s] = prev_state
        
        # Backward pass to find the most likely sequence
        state_sequence_indices = []
        
        # Find the most likely final state
        current_state = torch.argmax(viterbi[-1])
        state_sequence_indices.append(current_state.item())
        
        # Backtrack through the sequence
        for t in range(T-1, 0, -1):
            current_state = backpointer[t][current_state]
            state_sequence_indices.insert(0, current_state.item())
        
        # Convert state indices back to state labels
        state_sequence = [self.reverse_state_index[idx] for idx in state_sequence_indices]
        

        # Zip the state sequence and word indices
        # Convert from tuple to list of lists
        state_sequence_with_words = [list(item) for item in zip(state_sequence, words)]

        return {
            "state_sequence": state_sequence,
            "word_indices": word_indices,
            "state_sequence_with_words": state_sequence_with_words
        }


if __name__ == "__main__":
    # model = Model()
    # print(model.get_most_likely_state_sequence("I want to go to the store"))
    pass