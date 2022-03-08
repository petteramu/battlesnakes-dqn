
from collections import deque
import json
from keras.models import load_model
from os import system
import subprocess
from typing import Deque, Dict, List
from DQN_agent import DQN_agent
from battlesnake_types import TurnRequest
from data_transformation import DataTransformer
from model import create_mk2_models, create_models
from rewarders import OnlyWinsRewarder, RewardWinsPunishLossRewarder, SurvivalRewarder
from training_types import RoundHistoryElement

ROUNDS = 15000

FIT_EVERY = 1
SAVE_MODEL_EVERY = 200
COPY_WEIGHT_EVERY = 500

class Trainer():
    round_history: Dict[str, List[RoundHistoryElement]]
    round_winners: Dict[str, List[int]]
    live_stats: Dict[str, Deque[int]]
    survival: Dict[str, List[int]]
    agents: Dict[str, DQN_agent]

    def __init__(self):
        data_transformer = DataTransformer()
        winner_value_model = load_model(f"./models/winner.model")
        winner_target_model = load_model(f"./models/winner.model")
        # punisher_value_model = load_model(f"./models/initial-punisher.model")
        # punisher_target_model = load_model(f"./models/initial-punisher.model")
        survivor_value_model = load_model(f"./models/survivor.model")
        survivor_target_model = load_model(f"./models/survivor.model")
        mk2_punsiher_value_model = load_model(f"./models/mk2_punisher.model")
        mk2_punisher_target_model = load_model(f"./models/mk2_punisher.model")
        mk2_winner_value_model = load_model(f"./models/mk2_winner.model")
        mk2_winner_target_model = load_model(f"./models/mk2_winner.model")

        # (winner_value_model, winner_target_model) = create_models()
        # (punisher_value_model, punisher_target_model) = create_models()
        # (survivor_value_model, survivor_target_model) = create_models()
        # (mk2_punsiher_value_model, mk2_punisher_target_model) = create_mk2_models()
        # (mk2_winner_value_model, mk2_winner_target_model) = create_mk2_models()
        self.agents = {
            "winner": DQN_agent(winner_value_model, winner_target_model, data_transformer, OnlyWinsRewarder(), 0.01),
            # "punisher": DQN_agent(punisher_value_model, punisher_target_model, data_transformer, RewardWinsPunishLossRewarder(), 1),
            "survivor": DQN_agent(survivor_value_model, survivor_target_model, data_transformer, SurvivalRewarder(), 0.01),
            "mk2_punisher": DQN_agent(mk2_punsiher_value_model, mk2_punisher_target_model, data_transformer, RewardWinsPunishLossRewarder(), 0.01),
            "mk2_winner": DQN_agent(mk2_winner_value_model, mk2_winner_target_model, data_transformer, OnlyWinsRewarder(),0.01)
        }
        self.round_history = dict()
        self.round_winners = dict()
        self.live_stats = dict()
        self.survival = dict()
        for agent in self.agents:
            self.round_winners[agent] = list()
            self.live_stats[agent] = deque(maxlen=100)
            self.survival[agent] = [0]
            self.round_history[agent] = list()

    def add_round_result(self, snake_name: str, move: int, state: TurnRequest, terminal: bool = False):
        rhe = RoundHistoryElement(move, state, 0, terminal)
        self.round_history[snake_name].append(rhe)
        self.increment_survival(snake_name)

    def add_winner(self, winner: str):
        for snake_name in self.round_winners:
            self.round_winners[snake_name].append(
                1 if snake_name == winner else 0)
            self.live_stats[snake_name].append(
                1 if snake_name == winner else 0)

    def increment_survival(self, snake_name: str):
        self.survival[snake_name][-1] += 1

    def prepare_new_round(self, ):
        for snake_name in self.round_history:
            self.round_history[snake_name].clear()
            self.survival[snake_name].append(0)

    def run_battlesnake(self):
        self.prepare_new_round()
        params = ["./battlesnake.exe", "play", "-W", "11", "-H", "11"]

        for snake_name in self.agents:
            params = [*params, *["--name", snake_name,
                                 "--url", "http://localhost:8000"]]

        subprocess.run(params, capture_output=True)

    def print_stats(self):
        print(f"Last 100:")
        for snake_name in self.live_stats:
            print(f"{snake_name}: {sum(self.live_stats[snake_name])}")

    def save_history(self, history_type: str, source_dict: Dict[str, List[int]]):
        for snake_name in source_dict:
            existing = []
            try:
                with open(f"./models/{snake_name}-{history_type}.json", 'r') as f:
                    existing = json.load(f)
            except:
                pass
            if not existing:
                existing = []

            # Save only the data generated since the last save
            combined = [*existing, *source_dict[snake_name]]
            with open(f"./models/{snake_name}-{history_type}.json", 'w') as f:
                json.dump(combined, f)
            # Purge the history, but keep 100 to have live stats
            source_dict[snake_name].clear()

    def train(self):
        for round in range(1, ROUNDS + 1):
            system("cls")
            print(f"ROUND: {round}/{ROUNDS}")
            self.print_stats()
            self.run_battlesnake()
            print(
                f"Game lasted {self.round_history[list(self.agents.keys())[0]][-1].state.turn} rounds")
            if round % FIT_EVERY == 0:
                print(f"\nFitting models...")

            if round % SAVE_MODEL_EVERY == 0:
                print(f"\Saving models...")

            for snake_name in self.round_history:
                agent = self.agents[snake_name]
                agent.add_history(self.round_history[snake_name])

                if round % FIT_EVERY == 0:
                    agent.fit_model()

                if round % COPY_WEIGHT_EVERY == 0:
                    agent.target_network.set_weights(
                        agent.value_network.weights)

                if round % SAVE_MODEL_EVERY == 0:
                    agent.value_network.save(f'models/{snake_name}.model')
                    self.save_history("history", self.round_winners)
                    self.save_history("surival-history", self.survival)

                agent.decay_epsilon()

    def select_greedy_option(self, snake_name: str, state: TurnRequest):
        return self.agents[snake_name].select_greedy_option(state)
