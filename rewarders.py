from battlesnake_types import TurnRequest

class Rewarder():
    def determine_reward(self, resulting_state: TurnRequest, snake_name: str):
        return 0

class OnlyWinsRewarder(Rewarder):
    def determine_reward(self, resulting_state: TurnRequest, snake_name: str):
        if not resulting_state.board.snakes or len(resulting_state.board.snakes) > 1:
            return 0

        if resulting_state.board.snakes[0].name == snake_name:
            return 1

        return 0

class RewardWinsPunishLossRewarder(Rewarder):
    def determine_reward(self, resulting_state: TurnRequest, snake_name: str):
        if not resulting_state.board.snakes:
            return -1
        
        if len(resulting_state.board.snakes) > 1:
            snake_names = map(lambda snake: snake.name, resulting_state.board.snakes)
            if snake_name in snake_names:
                return 0
            else:
                return -1

        if resulting_state.board.snakes[0].name == snake_name:
            return 1
        
        return 0

class SurvivalRewarder(Rewarder):
    def determine_reward(self, resulting_state: TurnRequest, snake_name: str):
        if not resulting_state.board.snakes:
            return 0
        
        if len(resulting_state.board.snakes) > 1:
            snake_names = map(lambda snake: snake.name, resulting_state.board.snakes)
            if snake_name in snake_names:
                return 1
        
        return 0


class HatesLosingRewarder(Rewarder):
    dead = False

    def determine_reward(self, resulting_state: TurnRequest, snake_name: str):
        if not resulting_state.board.snakes:
            return -1
        
        if len(resulting_state.board.snakes) > 1:
            snake_names = map(lambda snake: snake.name, resulting_state.board.snakes)
            if snake_name in snake_names:
                self.dead = False
                return 1
            elif snake_name not in snake_names and not self.dead:
                self.dead = True
                return -100
            else:
                return 0

        return 0        
