# Battlensnakes DQN

## Install

Clone repository

> git clone https://github.com/petteramu/battlesnakes-dqn
>
> cd ./battlesnakes-dqn
>
> python -m venv ./venv

Windows:

> ./venv/scripts/activate

Mac:

> source ./venv/bin/activate

Then install dependencies:
> pip install tensorflow keras numpy fastapi pandas matplotlib uvicorn


**To start training**

> py run.py

You might want to alter the run.py script to set the amount of rounds to train for now. Also, to create new models for training instead of using the ones check in to the repo, set new_models=True

Or, alternatively, run it from the history notebook.

To see stats, see the history notebook

**Note that there have been some issues with loading models with differing python versions. It worked a bit better with .h5 models. The current models were creating with python 3.8.6**

Also note that there is some code from earlier when a http api was used to communicate with a different battlesnakes simulator
