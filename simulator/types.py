from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

class SnakeMove():
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

class Point():
    x: int
    y: int

    def __init__(self, tuple: Tuple[int, int]) -> None:
        self.x = int(tuple[0])
        self.y = int(tuple[1])

class SnakeOutput():
    id: str
    name: str
    health: int
    body: List[Point]
    latency: str
    head: Point
    length: int
    shout: str
    squad: str
    customizations: Dict[Any, Any]

class BoardOutput():
    height: int
    width: int
    food: List[Point]
    snakes: Optional[List[SnakeOutput]]
    hazards: List[Point]

class TurnOutput():
    you: SnakeOutput
    board: BoardOutput
    turn: int