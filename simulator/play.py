from typing import List
from simulator.board import Board
from simulator.snake import Snake

class GameResult():
    winner: str
    draw: bool

    def __init__(self, draw: bool, winner: Snake) -> None:
        if winner != None:
            self.winner = winner.name
        else:
            self.winner = None
        self.draw = draw

class Game():
    snake_states: List[Snake]
    board_state: Board

    def __init__(self, snakes: List[Snake]) -> None:
        self.snake_states = snakes
        self.board_state = Board(snakes)
        pass
    
    def play(self) -> GameResult:
        while not self.isGameOver():
            self.board_state.turn += 1
            self.createNextBoardState()

        isDraw = True
        winner: Snake = None
        for snake in self.snake_states:
            snake.policy.end_state(self.board_state.createTurnStateForSnake(snake), snake.elimination_reason)
            if snake.elimination_reason == None:
                isDraw = False
                winner = snake

        if isDraw:
            print(f"[DONE]: Game completed after {self.board_state.turn} turns. It was a draw.")
        else:
            print(f"[DONE]: Game completed after {self.board_state.turn} turns. {winner.name} is the winner.")

        return GameResult(isDraw, winner)

    def isGameOver(self) -> bool:
        numSnakesRemaining = 0
        for snake in self.snake_states:
            if snake.elimination_reason == None:
                numSnakesRemaining += 1

        return numSnakesRemaining <= 1
    
    def createNextBoardState(self) -> Board:
        states = []
        for index, snake in enumerate(self.snake_states):
            state = self.board_state.createTurnStateForSnake(snake)
            states.append(state)

        for index, snake in enumerate(self.snake_states):
            if snake.elimination_reason == None:
                snake.move(states[index])
        
        self.board_state.createNextBoardState()
