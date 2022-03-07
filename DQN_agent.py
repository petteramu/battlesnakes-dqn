
from collections import deque
from random import random, randrange, sample
from typing import Deque, List
import numpy as np
from keras import Sequential
from battlesnake_types import TurnRequest
from data_transformation import DataTransformer
from rewarders import Rewarder
from training_types import RoundHistoryElement

EPSILON_DECAY = 0.9975
MIN_EPSILON = 0.01
DISCOUNT = 0.99
REPLAY_MEMORY_BATCH = 32

class DQN_agent():
    epsilon = 1
    replay_memory: Deque
    rewarder: Rewarder
    data_transformer: DataTransformer
    value_network: Sequential
    target_network: Sequential

    def __init__(self, value_network: Sequential, target_network: Sequential, data_transformer: DataTransformer, rewarder: Rewarder, epsilon_start: int):
        self.value_network = value_network
        self.target_network = target_network
        self.data_transformer = data_transformer
        self.rewarder = rewarder
        self.epsilon = epsilon_start
        self.replay_memory = deque(maxlen=100000)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon * EPSILON_DECAY, MIN_EPSILON)

    def transform_bs_state_to_input_space(self, state: TurnRequest):
        input_space = np.array(self.data_transformer.state_to_input_space(state.board, state.you))
        return input_space
    
    def select_from_replay_memory(self):
        # return sample(self.replay_memory, 1)
        return sample(self.replay_memory, REPLAY_MEMORY_BATCH)
    
    def compute_q_value(self, reward: float, max_future_q: float):
        return reward + DISCOUNT * max_future_q
    
    def predict_qs(self, state):
        return self.target_network.predict(np.array([state]))
    
    def select_greedy_option(self, state):
        if random() < self.epsilon:
            return randrange(0, 4, step=1)
        
        input_space = self.transform_bs_state_to_input_space(state)
        return np.argmax(self.predict_qs(input_space))
    
    def is_terminal_state(self, state: TurnRequest):
        if not state.board.snakes:
            return True
        
    def fit_model(self):
        inputs = list()
        labels = list()

        if len(self.replay_memory) < REPLAY_MEMORY_BATCH:
            return

        selected_memory = self.select_from_replay_memory()

        for memory in selected_memory:
            reward = memory[2]
            if memory[4]: # The resulting state is a terminal state, there is no next state to predict q's from
                target_value = reward
            else:
                predicted_future_q = max(self.predict_qs(memory[3]))
                future_q_value = self.compute_q_value(reward, predicted_future_q)
                target_value = future_q_value[memory[1]]

            labels.append(target_value)
            inputs.append(memory[0])

        inputs = np.array(inputs)
        labels = np.asarray(labels)
        self.value_network.fit(inputs, labels, shuffle=False, batch_size=REPLAY_MEMORY_BATCH, verbose=0)
    
    def add_history(self, round_history: List[RoundHistoryElement]):
        for turn, snake_step in enumerate(round_history):
            if snake_step.terminal:
                continue # The game was over from the previous action

            resulting_state = round_history[turn + 1]
            reward = self.rewarder.determine_reward(resulting_state.state, resulting_state.state.you.name)

            current_transformed_state = self.transform_bs_state_to_input_space(snake_step.state)
            next_transformed_state = None if resulting_state.terminal else self.transform_bs_state_to_input_space(resulting_state.state)

            memory = (current_transformed_state, snake_step.move, reward, next_transformed_state, resulting_state.terminal)
            self.replay_memory.append(memory)
