import os
from abc import ABC
from pathlib import Path
from random import random

from keras import regularizers, layers, initializers, optimizers, callbacks
import keras.backend as k
from keras import Input
from keras.initializers.initializers_v1 import HeUniform
from keras.models import Model, load_model
import V1.machine_learning.custom_layers as custom_layers

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class NN_Model(ABC):
    def __init__(self, choice: str):
        self.nn_input = None
        self.path = Path(os.getcwd()).absolute()
        self.model_map_names = {
            "new_scaled_2layer": 1,
            "new_scaled_2layer_v2": 2,
        }
        self.model_name = choice
        self.model_choice: str = self.get_mapping(choice)
        self.model = None
        self.cp_callback: callbacks.ModelCheckpoint = None

    def get_mapping(self, choice: str):
        return self.model_map_names[choice]

    def create_model(self, is_training=True):
        print(f"[INFO] Model choice is set to {self.model_choice}")
        nn_input = Input(shape=(3,11))  # 80 *11
        if 1 <= self.model_choice <= 4:
            """
            OUT 1
               Newer model to-be implemented, which includes the following to record 5 data points ahead...
                Model Struct:
                    - Input 14 Columns worth of data
                        +  Upper Kelt
                        +  Lower Kelt 
                        +  Middle Kelt 
                        +  EMA 14 
                        +  EMA 30 
                        + Open
                        + High
                        + Low
                        + Close
                        + Last3High 
                        + Last3Low
                        + Base Fib 
                        + Next1 Fib
                        + Next2 Fib 
            """
            if self.model_choice == 1:
                # nn = custom_layers.TrainableDropout(0.2).call(nn_input, is_training)
                nn = layers.LSTM(24, input_shape=(3, 11), activation="relu",return_sequences=True)(
                    nn_input)
                nn = layers.LSTM(6, activation="linear")(
                    nn)
                # nn = custom_layers.TrainableDropout(0.25).call(nn, is_training)
            # if self.model_choice == 2:
            #     # ORIGINAL 67 percent accuracy model
            #     # To test, need to revert normalization for out == 4
            #     nn = custom_layers.TrainableDropout(0.5).call(nn_input, is_training)
            #     nn = layers.Dense(32, activation=layers.LeakyReLU(alpha=0.2))(
            #         nn)
            #     nn = layers.Dense(8, activation=layers.LeakyReLU(alpha=0.2))(nn)
            elif self.model_choice == 2:
                nn = layers.LSTM(128, input_shape=(20, 5, 14), return_sequences=True)(
                    nn_input)
                nn = layers.LSTM(96, input_shape=(128, 1, 1))(
                    nn)
            nn2 = layers.Dense(4, activation='relu')(nn)
            nn = Model(inputs=nn_input, outputs=[nn2])
            # loss_weights = [3.0,
            #                 1.0,
            #                 1.0,
            #                 5.0]
            nn.compile(optimizer=optimizers.Adam(learning_rate=0.002, beta_1=0.9, beta_2=0.998),
                       loss="logcosh",
                       metrics=['accuracy'],
                       # loss_weights=loss_weights
                       )

            # Convert to a model
        self.model = nn
        return nn

    """
    Initialize keras modelcheckpoint, used for saving weights
    """

    def model_checkpoint_callback(self, ck_path: str):
        self.cp_callback = callbacks.ModelCheckpoint(
            filepath=f'{ck_path}/cp.ckpt',
            save_weights_only=True,
            verbose=1,
            monitor='mean_squared_error',
            mode='auto',
            save_best_only=True)

    def save_model(self):
        # Ensure model is saved without training phase set
        # k.set_learning_phase(0)
        print(f"[INFO] Saving model to `{self.path}/data/{self.model_name}`")
        self.model.save(f'{self.path}/data/{self.model_name}')
        # Resume training phase after saving
        # k.set_learning_phase(1)

    def choose_random_ticker(self, csv_file: str):
        with open(csv_file) as f:
            ticker = random.choice(f.readlines())
            ticker = ticker[0:ticker.find(',')]
            print(ticker)
            return ticker

    def load_model(self, name=None, is_training=True):
        try:
            # When training a model, we want to ensure dropout is set when loading the model up
            # if is_training:
            #     k.set_learning_phase(1)
            # else:
            #     k.set_learning_phase(0
            self.model_name = name
            nn = load_model(
                f'{self.path}/data/{name}')
            for model_choice, name_loc in self.model_map_names.items():
                if name == name_loc:
                    self.model_choice = model_choice
            self.model = nn
            return nn
        except:
            print(f'[INFO] No model exists for {name}, creating new model...')
