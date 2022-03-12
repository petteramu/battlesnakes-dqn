from typing import List, Tuple

from numpy import random
from simulator.snake_move_policy import SnakeMovePolicy
from simulator.types import SnakeMove, TurnOutput

class Snake():
    ID: str
    name: str
    policy: SnakeMovePolicy
    body: List[Tuple[int, int]]
    elimination_reason: str = None
    eliminated_by: str = None
    health: int

    def __init__(self, policy: SnakeMovePolicy, name: str) -> None:
        self.ID = str(random.randint(0, 100000))
        self.policy = policy
        self.health = 100
        self.name = name
        self.body = list()

    def move(self, state: TurnOutput) -> int:
        move = self.policy.move(state)

        if self.elimination_reason != None:
            print("Eliminated snake attempts to move")
            return

        if move == SnakeMove.UP:
            x = self.body[0][0]
            y = self.body[0][1] + 1

        if move == SnakeMove.DOWN:
            x = self.body[0][0]
            y = self.body[0][1] - 1

        if move == SnakeMove.LEFT:
            x = self.body[0][0] - 1
            y = self.body[0][1]

        if move == SnakeMove.RIGHT:
            x = self.body[0][0] + 1
            y = self.body[0][1]

        newHead = (int(x), int(y))
        # Append new head, pop old tail
        self.body = [newHead, *self.body[:-1]]
        self.health = self.health - 1

    def end_state(self, state: TurnOutput):
        self.policy.end_state(state)