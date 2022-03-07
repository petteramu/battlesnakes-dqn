from battlesnake_types import Battlesnake, Board

def flatten(t):
    return [item for sublist in t for item in sublist]

class DataTransformer():
    # input space =
    # [0, 1] for height, width, where 0 is open, 1 is another snake (or obstacle)
    # [0, 1] for height, width, where 0 is no food, or health / 100 if there is food there
    # [0, 1] for height, width, where 0 is open, 1 is self
    def state_to_input_space(self, board: Board, self_snake: Battlesnake):
        input_space = []
        for width in range(0, board.width):
            # [self, other snakes, food]
            input_space.append([[0, 0, 0]] * board.height)
        
        input_space[self_snake.head.x][self_snake.head.y][0] = -1
        for body_part in self_snake.body:
            input_space[body_part.x][body_part.y][0] = 1

        for snake in board.snakes:
            input_space[snake.head.x][snake.head.y][1] = -1
            for body_part in snake.body:
                input_space[body_part.x][body_part.y][1] = 1

        for food in board.food:
            input_space[food.x][food.y][2] = 1 - self_snake.health / 100

        return input_space
