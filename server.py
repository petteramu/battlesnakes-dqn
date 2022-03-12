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
    return "ok"

@app.post("/move")
def post_move(data: TurnRequest):
    greedy_option = trainer.select_greedy_option(data.you.name, data)
    move = OPTIONS[greedy_option]
    return { "move": move, "shout": "Moving on!" }
