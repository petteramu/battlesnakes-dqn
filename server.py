from fastapi import FastAPI
from battlesnake_types import TurnRequest
from trainer import Trainer

OPTIONS = ["left", "right", "up", "down"]

app = FastAPI()

trainer = Trainer()
is_training = False

@app.get("/")
def root():
    return {
        "apiversion": "1",
        "author": "Petter",
        "color": "#888888",
        "head": "default",
        "tail": "default",
        "version": "0.0.1-training"
    }

@app.post("/start")
def post_start(data: TurnRequest):
    return "ok"

@app.post("/end")
def post_end(data: TurnRequest):
    if is_training:
        trainer.add_round_result(data.you.name, None, data, terminal=True)
        if data.board.snakes and data.board.snakes[0].name == data.you.name:
            trainer.add_winner(data.you.name)
    return "ok"

@app.post("/move")
def post_move(data: TurnRequest):
    greedy_option = trainer.select_greedy_option(data.you.name, data)
    move = OPTIONS[greedy_option]
    if is_training:
        trainer.add_round_result(data.you.name, greedy_option, data)
    return { "move": move, "shout": "Moving on!" }

@app.get("/train")
def get_train():
    global is_training
    if not is_training:
        print("Running battlesnake game")
        is_training = True
        trainer.train()
    else:
        return "Busy, already training"
