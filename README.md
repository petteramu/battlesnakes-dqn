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
>
> pip install tensorflow keras numpy fastapi pandas matplotlib uvicorn

Almost everything is installed now, the only thing missing is the actual battlesnakes game, which you can get from [https://github.com/BattlesnakeOfficial/rules/releases]
Place the battlesnakes.exe file in the root folder of battlesnakes-dqn

**To start training**

> uvicorn server:app

Then make a GET request to localhost:8000/train
