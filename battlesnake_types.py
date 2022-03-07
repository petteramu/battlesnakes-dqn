from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class Royale(BaseModel):
    shrinkEveryNTurns: int

class Squad(BaseModel):
    allowBodyCollisions: bool
    sharedElimination: bool
    sharedHealth: bool
    sharedLength: bool

class Settings(BaseModel):
    foodSpawnChance: int
    minimumFood: int
    hazardDamagePerTurn: int
    map: Optional[str]
    royale: Royale
    squad: Squad

class Ruleset(BaseModel):
    name: str
    version: str
    settings: Settings

class Game(BaseModel):
    id: str
    ruleset: Ruleset
    timeout: int
    source: str

class Point(BaseModel):
    x: int
    y: int

class Customizations(BaseModel):
    apiversion: str
    author: Optional[str]
    color: Optional[str]
    head: Optional[str]
    tail: Optional[str]
    version: Optional[str]

class Battlesnake(BaseModel):
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

class Board(BaseModel):
    height: int
    width: int
    food: List[Point]
    snakes: Optional[List[Battlesnake]]
    hazards: List[Point]

class TurnRequest(BaseModel):
    game: Game
    turn: int
    board: Board
    you: Battlesnake
