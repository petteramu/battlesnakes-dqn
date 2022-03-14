from battlesnake_types import Battlesnake, Board
from simulator.board import BoardOutput, SnakeOutput

def flatten(t):
    return [item for sublist in t for item in sublist]

class DataTransformer():
    input_shape = (11, 11, 3)
    # input space =
    # [0, 1] for height, width, where 0 is open, 1 is another snake (or obstacle)
    # [0, 1] for height, width, where 0 is no food, or health / 100 if there is food there
    # [0, 1] for height, width, where 0 is open, 1 is self
    def state_to_input_space(self, board: BoardOutput, self_snake: SnakeOutput):
        input_space = []
        for width in range(0, board.width):
            # [self, other snakes, food]
            input_space.append([[0, 0, 0]] * board.height)
        
        for body_part in self_snake.body:
            input_space[body_part.x][body_part.y][0] = 1
        input_space[self_snake.head.x][self_snake.head.y][0] = -1

        for snake in board.snakes:
            for body_part in snake.body:
                input_space[body_part.x][body_part.y][1] = 1
            input_space[snake.head.x][snake.head.y][1] = -1

        for food in board.food:
            input_space[food.x][food.y][2] = 1 - self_snake.health / 100

        return input_space

class BorderedDataTransformer(DataTransformer):
    input_shape = (13, 13, 3)

    def state_to_input_space(self, board: BoardOutput, self_snake: SnakeOutput):
        input_space = []
        for width in range(0, board.width + 2):
            # [self, other snakes, food]
            input_space.append([[0, 0, 0]] * (board.height + 2))
        
        # Fill borders with -1
        for x in range(0, len(input_space)):
            for y in range(0, len(input_space[x])):
                if x == 0 or y == 0 or x == len(input_space) - 1 or y == len(input_space[x]) - 1:
                    input_space[x][y] = [-1, -1, -1]

        # Heads are represented with 5, bodies with 1
        for body_part in self_snake.body:
            input_space[body_part.x][body_part.y][0] = 1
        input_space[self_snake.head.x][self_snake.head.y][0] = 5

        # Heads are represented with 5, bodies with 1
        for snake in board.snakes:
            for body_part in snake.body:
                input_space[body_part.x][body_part.y][1] = 1
            input_space[snake.head.x][snake.head.y][1] = 5

        for food in board.food:
            input_space[food.x][food.y][2] = 1 - self_snake.health / 100

        return input_space
