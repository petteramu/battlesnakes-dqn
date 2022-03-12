from typing import List
from DQN_agent import DQN_agent
from simulator.board import TurnOutput
from simulator.snake_move_policy import SnakeMovePolicy
from training_types import RoundHistoryElement

class DQNMovePolicy(SnakeMovePolicy):
    agent: DQN_agent
    history: List[RoundHistoryElement]

    def __init__(self, agent: DQN_agent) -> None:
        super().__init__()
        self.agent = agent
        self.history = list()

    def move(self, state: TurnOutput) -> int:
        move = self.agent.select_greedy_option(state)
        rhe = RoundHistoryElement(move, state, False)
        self.history.append(rhe)
        return move

    def end_state(self, state: TurnOutput, elimination_reason: str):
        rhe = RoundHistoryElement(None, state, True, elimination_reason)
        self.history.append(rhe)
