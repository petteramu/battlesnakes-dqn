from genericpath import exists
from typing import Dict, List
from training_types import RoundHistoryElement

class Logger():
    path: str
    games: Dict[str, List[List[RoundHistoryElement]]]
    
    def __init__(self, path="./logs/") -> None:
        self.path = path
        self.games = dict()

    def keep(self, agent_name: str, game: List[RoundHistoryElement]):
        if not agent_name in self.games.keys():
            self.games[agent_name] = list()
        
        self.games[agent_name].append(game)

    def dump(self, agent_name: str):
        file_path = f"{self.path}{agent_name}.csv"

        if not exists(file_path):
            with open(file_path, "w") as f:
                f.write("name,survived,won,elim_reason\n")

        with open(file_path, "a") as f:
            for game in self.games[agent_name]:
                won = game[-1].elimination_reason == None
                survival_mod = 0 if won else 1 # The winner survived the last round, the others didn't
                survived = len(game) - survival_mod
                output = f"{agent_name},{survived},{won},{game[-1].elimination_reason}\n"
                f.write(output)
        
        self.games[agent_name].clear()
