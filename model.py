from keras import Sequential
from keras.layers import Conv2D, Dropout, Flatten, Dense, LeakyReLU
from keras.optimizer_v2.adam import Adam

def create_model():
    model = Sequential(layers=[
        Conv2D(filters=16, kernel_size=(3,3), activation='relu', input_shape=(11, 11, 3)),
        Conv2D(filters=32, kernel_size=(3,3), activation='relu'),
        # Conv2D(filters=8, kernel_size=(2,2), activation='relu'),
        Flatten(),
        Dropout(0.5),
        Dense(32, activation="relu"),
        Dense(4)
    ], name="Battlesnake_trainer")

    model.compile(optimizer="adam", loss="mse")
    model.build()
    model.summary()
    return model

def create_models():
    value_model = create_model()
    target_model = create_model()
    target_model.set_weights(value_model.weights)
    return (value_model, target_model)

def create_model_mk2():
    model = Sequential(layers=[
        Conv2D(filters=8, kernel_size=(3,3), activation=LeakyReLU(), input_shape=(11, 11, 3)),
        Conv2D(filters=16, kernel_size=(3,3), activation=LeakyReLU()),
        Conv2D(filters=32, kernel_size=(3,3), activation=LeakyReLU()),
        Flatten(),
        Dropout(0.5),
        Dense(32, activation="relu"),
        Dense(32, activation="relu"),
        Dense(4)
    ], name="Battlesnake_trainer_mk2")

    model.compile(optimizer=Adam(learning_rate=0.00025), loss="mse")
    model.build()
    model.summary()
    return model

def create_mk2_models():
    value_model = create_model_mk2()
    target_model = create_model_mk2()
    target_model.set_weights(value_model.weights)
    return (value_model, target_model)
