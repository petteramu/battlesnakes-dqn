from trainer import Trainer

# t = Trainer()
# t.train(500)

from tensorflow.python.client import device_lib 
print(device_lib.list_local_devices())