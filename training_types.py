from battlesnake_types import TurnRequest

class RoundHistoryElement():
    move: int
    state: TurnRequest
    score: int
    terminal: bool

    def __init__(self, move: int, state: dict, score: int, terminal: bool = False):
        self.move = move
        self.state = state
        self.score = score
        self.terminal = terminal