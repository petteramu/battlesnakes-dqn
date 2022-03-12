import random
from typing import Dict, List, Tuple
from simulator.snake import Snake
from simulator.types import BoardOutput, Point, SnakeOutput, TurnOutput

class Board():
    width: int = 11
    height: int = 11
    food: List[Tuple[int, int]]
    snake_start_size: int = 3
    snakes: List[Snake]
    turn: int

    def __init__(self, snakes: List[Snake]) -> None:
        self.food = []
        self.snakes = snakes
        self.turn = 0
        
        self.place_snakes()
        self.place_food()

    def place_snakes(self) -> None:
        # Create start 8 points
        mn = 1
        md = (self.width-1)/2
        mx = self.width-2
        startPoints = [
            (mn, mn),
            (mn, md),
            (mn, mx),
            (md, mn),
            (md, mx),
            (mx, mn),
            (mx, md),
            (mx, mx),
        ]

        # Sanity check
        if len(self.snakes) > len(startPoints):
            raise Exception("Error, didn't create enough start positions for snakes")

        # Randomly order them
        random.shuffle(startPoints)

        # Assign to snakes in order given
        for i in range(len(self.snakes)):
            for j in range(0, self.snake_start_size):
                self.snakes[i].body.append(startPoints[i])

    def place_food(self) -> None:
        centerCoord = (int((self.width - 1) / 2), int((self.height - 1) / 2))

        # Place 1 food within exactly 2 moves of each snake, but never towards the center
        for i in range(0, len(self.snakes)):
            snakeHead = self.snakes[i].body[0]
            possibleFoodLocations = [
                ( snakeHead[0] - 1, snakeHead[1] - 1 ),
                ( snakeHead[0] - 1, snakeHead[1] + 1 ),
                ( snakeHead[0] + 1, snakeHead[1] - 1 ),
                ( snakeHead[0] + 1, snakeHead[1] + 1 ),
            ]

            # Remove any positions already occupied by food or closer to center
            availableFoodLocations = []
            for p in possibleFoodLocations:
                isOccupiedAlready = False
                for food in self.food:
                    if food[0] == p[0] and food[1] == p[1]:
                        isOccupiedAlready = True
                        break

                if isOccupiedAlready:
                    continue

                # Food must be away from center on at least one axis
                isFarFromCenter = False
                if p[0] < snakeHead[0] and snakeHead[0] < centerCoord[0]:
                    isFarFromCenter = True
                elif centerCoord[0] < snakeHead[0] and snakeHead[0] < p[0]:
                    isFarFromCenter = True
                elif p[1] < snakeHead[1] and snakeHead[1] < centerCoord[1]:
                    isFarFromCenter = True
                elif centerCoord[1] < snakeHead[1] and snakeHead[1] < p[1]:
                    isFarFromCenter = True
                
                if isFarFromCenter:
                    availableFoodLocations.append(p)

            if len(availableFoodLocations) <= 0:
                return None

            # Select randomly from available locations
            placedFood = availableFoodLocations[random.randint(0, len(availableFoodLocations) - 1)]
            self.food.append(placedFood)

        # Finally, always place 1 food in center of board for dramatic purposes
        isCenterOccupied = True
        unoccupiedPoints = self.getUnoccupiedPoints(True)
        for point in unoccupiedPoints:
            if point == centerCoord:
                isCenterOccupied = False
                break

        if isCenterOccupied:
            return None

        self.food.append(centerCoord)

        return None

    def getUnoccupiedPoints(self, includePossibleMoves: bool) -> List[Tuple[int, int]]:
        pointIsOccupied: Dict[int, Dict[int, bool]] = dict()
        for p in self.food:
            if not p[0] in pointIsOccupied.keys():
                pointIsOccupied[p[0]] = dict()

            pointIsOccupied[p[0]][p[1]] = True
        
        for snake in self.snakes:
            if snake.elimination_reason != None:
                continue

            for i, p in enumerate(snake.body):
                if not p[0] in pointIsOccupied.keys():
                    pointIsOccupied[p[0]] = dict()

                pointIsOccupied[p[0]][p[1]] = True

                if i == 0 and not includePossibleMoves:
                    nextMovePoints = [
                        { "X": p[0] - 1, "Y": p[1]},
                        { "X": p[0] + 1, "Y": p[1]},
                        { "X": p[0], "Y": p[1] - 1},
                        { "X": p[0], "Y": p[1] + 1},
                    ]
                    for nextP in nextMovePoints:
                        if not nextP["X"] in pointIsOccupied.keys():
                            pointIsOccupied[nextP["X"]] = dict()

                        pointIsOccupied[nextP["X"]][nextP["Y"]] = True

        unoccupiedPoints: List[Tuple[int, int]] = []
        for x in range(0, self.width):
            for y in range(0, self.height):
                if x in pointIsOccupied.keys():
                    if y in pointIsOccupied[x].keys():
                        if pointIsOccupied[x][y]:
                            continue

                unoccupiedPoints.append((x, y))

        return unoccupiedPoints

    def createNextBoardState(self):
        # We specifically want to copy prevState, so as not to alter it directly.

        # bvanvugt: We specifically want this to happen before elimination for two reasons:
        # 1) We want snakes to be able to eat on their very last turn and still survive.
        # 2) So that head-to-head collisions on food still remove the food.
        #    This does create an artifact though, where head-to-head collisions
        #    of equal length actually show length + 1 and full health, as if both snakes ate.
        self.maybeFeedSnakes()
        self.maybeSpawnFood()
        self.maybeEliminateSnakes()

    def maybeFeedSnakes(self) -> None:
        newFood = []
        for food in self.food:
            foodHasBeenEaten = False
            for snake in self.snakes:
                # Ignore eliminated and zero-length snakes, they can't eat.
                if snake.elimination_reason != None or len(snake.body) == 0:
                    continue

                if snake.body[0][0] == food[0] and snake.body[0][0] == food[1]:
                    snake.health = 100
                    foodHasBeenEaten = True

            # Persist food to next BoardState if not eaten
            if not foodHasBeenEaten:
                newFood.append(food)

        self.food = newFood
        return None

    def maybeSpawnFood(self):
        numCurrentFood = len(self.food)
        if numCurrentFood < 1:
            return self.placeFoodRandomly()
        elif random.randint(0, 99) < 15:
            return self.placeFoodRandomly()

        return None

    # PlaceFoodRandomly adds up to n new food to the board in random unoccupied squares
    def placeFoodRandomly(self):
        unoccupiedPoints = self.getUnoccupiedPoints(False)
        if len(unoccupiedPoints) > 0:
            newFood = unoccupiedPoints[random.randint(0, len(unoccupiedPoints) - 1)]
            self.food.append(newFood)

    def maybeEliminateSnakes(self):
        # First order snake indices by length.
        # In multi-collision scenarios we want to always attribute elimination to the longest snake.
        snakeIndicesByLength = range(0, len(self.snakes))
        sorted(snakeIndicesByLength, key=lambda i: len(self.snakes[snakeIndicesByLength[i]].body))

        # First, iterate over all non-eliminated snakes and eliminate the ones
        # that are out of health or have moved out of bounds.
        for snake in self.snakes:
            if snake.elimination_reason != None:
                continue

            if len(snake.body) <= 0:
                raise Exception("ErrorZeroLengthSnake")

            if snake.health <= 0:
                snake.elimination_reason = "EliminatedByOutOfHealth"
                continue
            
            if self.snakeIsOutOfBounds(snake):
                snake.elimination_reason = "EliminatedByOutOfBounds"
                continue

        # Next, look for any collisions. Note we apply collision eliminations
        # after this check so that snakes can collide with each other and be properly eliminated.
        collisionEliminations = []
        for snake in self.snakes:
            if snake.elimination_reason != None:
                continue

            if len(snake.body) <= 0:
                raise Exception("ErrorZeroLengthSnake")

            # Check for self-collisions first
            if self.snakeHasBodyCollided(snake, snake):
                collisionEliminations.append({
                    "ID":    snake.ID,
                    "Cause": "EliminatedBySelfCollision",
                    "By":    snake.ID,
                })
                continue

            # Check for body collisions with other snakes second
            hasBodyCollided = False
            for otherIndex in snakeIndicesByLength:
                other = self.snakes[otherIndex]
                if other.elimination_reason != None:
                    continue

                if snake.ID != other.ID and self.snakeHasBodyCollided(snake, other):
                    collisionEliminations.append({
                        "ID":    snake.ID,
                        "Cause": "EliminatedByCollision",
                        "By":    other.ID,
                    })
                    hasBodyCollided = True
                    break

            if hasBodyCollided:
                continue

            # Check for head-to-heads last
            hasHeadCollided = False
            for otherIndex in snakeIndicesByLength:
                other = self.snakes[otherIndex]
                if other.elimination_reason != None:
                    continue

                if snake.ID != other.ID and self.snakeHasLostHeadToHead(snake, other):
                    collisionEliminations.append({
                        "ID":    snake.ID,
                        "Cause": "EliminatedByHeadToHeadCollision",
                        "By":    other.ID,
                    })
                    hasHeadCollided = True
                    break

            if hasHeadCollided:
                continue
 
        # Apply collision eliminations
        for elimination in collisionEliminations:
            for snake in self.snakes:
                if snake.ID == elimination["ID"]:
                    snake.elimination_reason = elimination["Cause"]
                    snake.eliminated_by = elimination["By"]
                    break

        return None

    def snakeIsOutOfBounds(self, s: Snake) -> bool:
        for point in s.body:
            if (point[0] < 0) or (point[0] >= self.width):
                return True

            if (point[1] < 0) or (point[1] >= self.height):
                return True
            
        return False

    def snakeHasBodyCollided(self, s: Snake, other: Snake) -> bool:
        head = s.body[0]
        for i, body in enumerate(other.body):
            if i == 0:
                continue
            elif head[0] == body[0] and head[1] == body[1]:
                return True

        return False

    def snakeHasLostHeadToHead(self, s: Snake, other: Snake) -> bool:
        if s.body[0][0] == other.body[0][0] and s.body[0][1] == other.body[0][1]:
            return len(s.body) <= len(other.body)

        return False

    def createTurnStateForSnake(self, snake: Snake) -> Dict:
        snake_state = self.createSnakeOutputState(snake)
        board_state = self.createBoardOutputState()

        state = TurnOutput()
        state.you = snake_state
        state.board = board_state
        state.turn = self.turn
        return state
    
    def createSnakeOutputState(self, snake: Snake) -> Dict:
        state = SnakeOutput()
        state.id = snake.ID
        state.name = snake.name
        state.health = snake.health
        state.body = list(map(self.tupleToPoint, snake.body[1:]))
        state.latency = 0
        state.head = self.tupleToPoint(snake.body[0])
        state.length = len(snake.body)
        state.shout = ""
        state.squad = ""
        state.customizations = dict()

        return state
    
    def tupleToPoint(self, tuple: Tuple[int, int]) -> Point:
        return Point(tuple)

    def createBoardOutputState(self) -> Dict:
        snakes_alive = []
        for snake in self.snakes:
            if snake.elimination_reason == None:
                snakes_alive.append(self.createSnakeOutputState(snake))
        
        if len(snakes_alive) == 0:
            snakes_alive = None

        state = BoardOutput()
        state.height = self.height
        state.width = self.width
        state.food = list()
        for food in self.food:
            state.food.append(self.tupleToPoint(food))
        state.snakes = snakes_alive
        return state
