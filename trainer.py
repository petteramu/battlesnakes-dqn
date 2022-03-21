
from collections import deque
import json
from keras.models import load_model
from os import system
from typing import Deque, Dict, List
from DQN_agent import DQN_agent
from battlesnake_types import TurnRequest
from data_transformation import BorderedDataTransformer, DataTransformer
from dqn_move_policy import DQNMovePolicy
from logger import Logger
from model import create_bordered_models, create_mk2_models, create_models
from rewarders import OnlyWinsRewarder, RewardWinsPunishLossRewarder, SurvivalRewarder
from simulator.play import Game
from simulator.snake import Snake
from training_types import RoundHistoryElement

ROUNDS = 200

FIT_EVERY = 1
WARMUP = 100
SAVE_MODEL_EVERY = 200
COPY_WEIGHT_EVERY = 500
LOG_EVERY = 50

class Trainer():
    live_stats: Dict[str, Deque[int]]
    agents: Dict[str, DQN_agent]
    logger: Logger

    def __init__(self, new_models=False):
        self.logger = Logger()
        data_transformer = DataTransformer()
        bordered_data_transformer = BorderedDataTransformer()
        if new_models:
            epsilon = 1
            # (winner_value_model, winner_target_model) = create_models()
            (survivor_value_model, survivor_target_model) = create_models()
            (mk2_punisher_value_model, mk2_punisher_target_model) = create_mk2_models()
            (mk2_winner_value_model, mk2_winner_target_model) = create_mk2_models()
            (bordered_value_model, bordered_target_model) = create_bordered_models()
        else:
            epsilon = 0.01
            # winner_value_model = load_model(f"./models/winner.h5")
            # winner_epsilon = 0.01
            # winner_target_model = load_model(f"./models/winner.h5")
            survivor_value_model = load_model(f"./models/survivor.h5")
            survivor_target_model = load_model(f"./models/survivor.h5")
            mk2_punisher_value_model = load_model(f"./models/mk2_punisher.h5")
            mk2_punisher_target_model = load_model(f"./models/mk2_punisher.h5")
            mk2_winner_value_model = load_model(f"./models/mk2_winner.h5")
            mk2_winner_target_model = load_model(f"./models/mk2_winner.h5")
            bordered_value_model = load_model(f"./models/bordered.h5")
            bordered_target_model = load_model(f"./models/bordered.h5")

        bordered_agent = DQN_agent("bordered", bordered_value_model, bordered_target_model, bordered_data_transformer, OnlyWinsRewarder(), epsilon)
        survivor_agent = DQN_agent("survivor", survivor_value_model, survivor_target_model, data_transformer, SurvivalRewarder(), epsilon)
        mk2_punisher_agent = DQN_agent("mk2_punisher", mk2_punisher_value_model, mk2_punisher_target_model, data_transformer, RewardWinsPunishLossRewarder(), epsilon)
        mk2_winner_agent = DQN_agent("mk2_winner", mk2_winner_value_model, mk2_winner_target_model, data_transformer, OnlyWinsRewarder(), epsilon)
        self.agents = {
            # "winner": DQN_agent("winner", winner_value_model, winner_target_model, data_transformer, OnlyWinsRewarder(), winner_epsilon),
            "bordered": bordered_agent,
            "bordered2": bordered_agent,
            "survivor": survivor_agent,
            "survivor2": survivor_agent,
            "mk2_punisher": mk2_punisher_agent,
            "mk2_punisher2": mk2_punisher_agent,
            "mk2_winner": mk2_winner_agent,
            "mk2_winner2": mk2_winner_agent,
        }
        self.live_stats = dict()
        for agent in self.agents:
            self.live_stats[agent] = deque(maxlen=100)

    def add_winner(self, winner: str):
        """Adds the winner to the live stats"""
        for snake_name in self.agents:
            self.live_stats[snake_name].append(
                1 if snake_name == winner else 0)

    def run_battlesnake(self):
        """Starts a round of battlesnake, with the dqn agents acting as snakes. Returns the moves each snake made during the game"""
        snakes: List[Snake] = []
        for agent in self.agents:
            policy = DQNMovePolicy(self.agents[agent])
            snake = Snake(policy, agent)
            snakes.append(snake)
        
        game = Game(snakes)
        result = game.play()

        self.add_winner(result.winner)

        histories: Dict[str, List[RoundHistoryElement]] = dict()
        for snake in snakes:
            histories[snake.name] = snake.policy.history
            self.logger.keep(snake.policy.agent.name, snake.policy.history)
        
        return histories

    def print_stats(self):
        """Prints how many wins each snake had in the last 100 games"""
        print(f"Last 100:")
        for snake_name in self.live_stats:
            print(f"{snake_name}: {sum(self.live_stats[snake_name])}")

    def save_history(self):
        """Saves the result of the games since last save to a log file"""
        for agent_name in self.agents:
            self.logger.dump(self.agents[agent_name].name)

    def train(self, rounds: int = ROUNDS):
        """ This is the actual training logic. The training will go for x amount of rounds, where each round will run a battlesnake game.
            The snakes moves are then passed to the dqn agents which will keep them in the replay memory, which again will be sampled every round
            for training.
        """
        for round in range(1, rounds + 1):
            system("cls")
            print(f"ROUND: {round}/{rounds}")
            self.print_stats()
            histories = self.run_battlesnake()

            fit = round >= WARMUP and round % FIT_EVERY == 0
            save_logs = round % LOG_EVERY == 0
            save_model = round % SAVE_MODEL_EVERY == 0

            if fit:
                print(f"\nFitting models...")
            if save_model:
                print(f"\Saving models...")
            if save_logs:
                print(f"\Saving logs...")

            for snake_name in histories:
                agent = self.agents[snake_name]
                agent.add_history(histories[snake_name])

                if fit:
                    agent.fit_model()

                if round % COPY_WEIGHT_EVERY == 0:
                    agent.target_network.set_weights(
                        agent.value_network.weights)

                if save_model:
                    agent.value_network.save(f'models/{agent.name}.h5', save_format="h5")
                
                if save_logs:
                    self.save_history()

                agent.decay_epsilon()

    def select_greedy_option(self, snake_name: str, state: TurnRequest):
        return self.agents[snake_name].select_greedy_option(state)
