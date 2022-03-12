from simulator.types import TurnOutput

class SnakeMovePolicy():

    def move(self, state: TurnOutput) -> int:
        """Decides the next move for a snake. Options are: 0, 1, 2, 3 which maps to left, right, up, down"""
        return 0

    def end_state(self):
        pass