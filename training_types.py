from battlesnake_types import TurnRequest

class RoundHistoryElement():
    move: int
    state: TurnRequest
    terminal: bool
    elimination_reason: str

    def __init__(self, move: int, state: dict, terminal: bool = False, elimination_reason: str = None):
        self.move = move
        self.state = state
        self.terminal = terminal
        self.elimination_reason = elimination_reason
