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
            "relu_multilayer_l2": 1,
                                "relu_2layer_0regularization": 2,
                                "relu_2layer_l1l2": 3,
                                "relu_1layer_l2": 4,
                                "new_multi_analysis_l2": 5,
                                "new_multi_analysis_2layer_0regularization": 6,
                                "new_scaled_l2": 7,
                                "new_scaled_l2_60m": 7,
                                "new_scaled_l2_5m": 7,
                                "new_scaled_2layer_0regularization": 8,
                                "scaled_2layer": 9,
                                "test_2layer": 10,
                                "SPY_relu_multilayer_l2": 11,
                                "new_scaled_2layer": 12,
                                "new_scaled_2layer_v2": 13,
                                }
        self.model_name = choice
        self.model_choice: str = self.get_mapping(choice)
        self.model = None
        self.cp_callback: callbacks.ModelCheckpoint = None

    def get_mapping(self, choice: str):
        return self.model_map_names[choice]

    def create_model(self, is_training=True):
        print(f"[INFO] Model choice is set to {self.model_choice}")
        if 0 < self.model_choice <= 4 or self.model_choice == 11:
            nn_input = Input(shape=(1, 126))  # 14 * 9 cols
        elif 5 <= self.model_choice <= 6:
            nn_input = Input(shape=(1, 130))  # 5 * 26 cols
        elif 7 <= self.model_choice <= 11:
            nn_input = Input(shape=(1, 55))  # 5 * 11 cols
        elif 12 <= self.model_choice <= 15:
            nn_input = Input(shape=(14, 5))  # 5 * 14 cols
        """
         These are legacy models... Takes in 14 days worth of data, then attempts to create a model to predict 1 datapoint outwards
        Model Struct:
        OUT 1
            - Input 9 columns worth of data
                + 'Close EMA14 Distance'
                + 'Close EMA30 Distance'
                + 'Close Fib1 Distance'
                + 'Close Fib2 Distance'
                + 'Num Consec Candle Dir'
                + 'Upper Keltner Close Diff'
                + 'Lower Keltner Close Diff'
                + 'Open'
                + 'Close'
       """
        if 0 < self.model_choice <= 4 or self.model_choice == 11:
            if self.model_choice == 1:
                nn = custom_layers.TrainableDropout(0.5).call(nn_input,is_training)
                nn = layers.Dense(64, activation=layers.LeakyReLU(alpha=0.3))(nn)
                nn2 = layers.Dense(1, activation='linear', activity_regularizer=regularizers.l2(0.01))(
                    nn)
                nn2 = layers.Dense(1, activation='linear',)(
                    nn)

            elif self.model_choice == 2:
                nn = layers.Dense(64, activation=layers.LeakyReLU(alpha=0.3),activity_regularizer=regularizers.l1(0.02))(nn_input)
                nn = custom_layers.TrainableDropout(0.5).call(nn,is_training)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.2))(nn)
                nn2 = layers.Dense(1, activation='linear', activity_regularizer=regularizers.l2(0.01))(
                    nn)
                nn2 = layers.Dense(1, activation='linear',)(
                    nn)
            elif self.model_choice == 3:
                nn = custom_layers.TrainableDropout(0.5).call(nn_input,is_training)
                nn = layers.Dense(48, activation=layers.LeakyReLU(alpha=0.2))(nn)
                nn = custom_layers.TrainableDropout(0.25).call(nn,is_training)
                nn = layers.Dense(12, activation=layers.LeakyReLU(alpha=0.2),
                                  kernel_regularizer=regularizers.l1_l2(0.02, 0.005))(nn)
                nn2 = layers.Dense(1, activation='linear')(nn)

            elif self.model_choice == 4:
                nn = custom_layers.TrainableDropout(0.25).call(nn_input,is_training)
                nn = layers.Dense(64, activation=layers.LeakyReLU(alpha=0.3))(nn)
                nn2 = layers.Dense(1, activation='linear')(nn)
            elif self.model_choice == 11:
                nn = layers.Dense(126, activation=layers.LeakyReLU(alpha=0.3),
                                  )(
                    nn_input)
                nn = custom_layers.TrainableDropout(0.5).call(nn,is_training)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.3),
                                  activity_regularizer=regularizers.l2(0.01))(nn)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.3),
                                  )(nn)
                nn2 = layers.Dense(1, activation='linear', activity_regularizer=regularizers.l2(0.01))(
                    nn)

            nn = Model(inputs=nn_input, outputs=[nn2])
            nn.compile(optimizer=optimizers.Adam(learning_rate=0.01, beta_1=0.90, beta_2=0.997), loss='mean_squared_error',
                           metrics=['MeanSquaredError'])

        elif 5 <= self.model_choice <= 6:
            """
            OUT 2
               Newer model to-be implemented, which includes the following to record 3 data points ahead...
                Model Struct:
                    - Input 26 Columns worth of data
                        + Last2Volume Cur Volume Diff
                        + Open Upper Kelt Diff
                        + Open Lower Kelt Diff
                        + High Upper Kelt Diff
                        + High Lower Kelt Diff
                        + Low Upper Kelt Diff
                        + Low Lower Kelt Diff
                        + Close Upper Kelt Diff
                        + Close Lower Kelt Diff
                        + EMA 14 30 Diff
                        + Base Fib High Diff
                        + Base Fib Low Diff
                        + Next1 Fib High Diff
                        + Next1 Fib Low Diff
                        + Next2 Fib High Diff
                        + Next2 Fib Low Diff
                        + Open
                        + High
                        + Low
                        + Close
                        + Last3High Base Fib
                        + Last3Low Base Fib
                        + Last3High Next1 Fib
                        + Last3Low Next1 Fib
                        + Last3High Next2 Fib
                        + Last3Low Next2 Fib
            """
            if self.model_choice == 5:
                nn = layers.Dense(130, activation=layers.LeakyReLU(alpha=0.3),
                                  activity_regularizer=regularizers.l2(0.01))(
                    nn_input)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.3),
                                  activity_regularizer=regularizers.l2(0.01))(nn)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.3),
                                  activity_regularizer=regularizers.l2(0.01))(nn)
                nn2 = layers.Dense(4, activation='linear', activity_regularizer=regularizers.l2(0.01))(
                    nn)

            elif self.model_choice == 6:
                nn = custom_layers.TrainableDropout(0.5).call(nn_input,is_training)
                nn = layers.Dense(64, activation=layers.LeakyReLU(alpha=0.2),activity_regularizer=regularizers.l1(0.005))(
                    nn)
                nn = custom_layers.TrainableDropout(0.5).call(nn_input,is_training)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.2))(nn)
                nn2 = layers.Dense(4, activation='linear')(
                    nn)
            nn = Model(inputs=nn_input, outputs=[nn2])
            nn.compile(optimizer=optimizers.Adam(learning_rate=0.001, beta_1=0.90, beta_2=0.998), loss='mean_squared_error',
                       metrics=['MeanSquaredError'])
        elif 7 <= self.model_choice <= 11:
            """
            OUT 3
               Newer model to-be implemented, which includes the following to record 5 data points ahead...
                Model Struct:
                    - Input 11 Columns worth of data
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
            """
            if self.model_choice == 7:
                nn = layers.Dense(16, kernel_initializer='he_uniform', bias_initializer=HeUniform(seed=None),
                                  activation=layers.LeakyReLU(alpha=0.3))(
                    nn_input)
                nn = layers.Dense(8, activation=layers.LeakyReLU(alpha=0.35))(nn)

            elif self.model_choice == 8:
                nn = custom_layers.TrainableDropout(0.5).call(nn_input,is_training)
                nn = layers.Dense(32, activation=layers.LeakyReLU(alpha=0.2))(
                    nn)
            elif self.model_choice == 9:
                nn = layers.Dense(32, activation=layers.LeakyReLU(alpha=0.2),bias_initializer=HeUniform(seed=None))(
                    nn_input)
                nn = custom_layers.TrainableDropout(0.5).call(nn,is_training)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.2))(nn)
            elif self.model_choice == 10:
                nn = custom_layers.TrainableDropout(0.25).call(nn_input,is_training)
                nn = layers.Dense(16, activation=layers.LeakyReLU(alpha=0.4))(
                    nn)
                nn = custom_layers.TrainableDropout(0.5).call(nn_input,is_training)
                nn = layers.Dense(16, activation=layers.LeakyReLU(alpha=0.4))(nn) # change back to 12 for orig model
            nn2 = layers.Dense(4, activation='linear')(nn)
            nn = Model(inputs=nn_input, outputs=[nn2])
            nn.compile(optimizer=optimizers.Adam(learning_rate=0.003, beta_1=0.95, beta_2=0.998), loss='mean_squared_error',
                       metrics=['MeanSquaredError'])
        elif 12 <= self.model_choice <= 15:
            """
            OUT 4
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
            if self.model_choice == 12:
                # nn = custom_layers.TrainableDropout(0.2).call(nn_input, is_training)
                nn = layers.LSTM(64,input_shape=(5,14),return_sequences=True)(
                    nn_input)
                # nn = custom_layers.TrainableDropout(0.25).call(nn, is_training)
                nn = layers.LSTM(8,input_shape=(64,1,1))(
                    nn)
                # nn = layers.Dense(8, activation=layers.LeakyReLU(alpha=0.3))(nn_input)
            # if self.model_choice == 12:
            #     # ORIGINAL 67 percent accuracy model
            #     # To test, need to revert normalization for out == 4
            #     nn = custom_layers.TrainableDropout(0.5).call(nn_input, is_training)
            #     nn = layers.Dense(32, activation=layers.LeakyReLU(alpha=0.2))(
            #         nn)
            #     nn = layers.Dense(8, activation=layers.LeakyReLU(alpha=0.2))(nn)
            elif self.model_choice == 13:
                nn = layers.LSTM(48,input_shape=(5,14),return_sequences=True)(
                    nn_input)
                nn = layers.LSTM(6,input_shape=(48,1,1))(
                    nn)
            nn2 = layers.Dense(4, activation='linear')(nn)
            nn = Model(inputs=nn_input, outputs=[nn2])
            nn.compile(optimizer=optimizers.Adam(learning_rate=0.003, beta_1=0.9, beta_2=0.998), loss='mean_squared_error',
                       metrics=['MeanSquaredError'])

            # Convert to a model
        self.model = nn
        return nn
    """
    Initialize keras modelcheckpoint, used for saving weights
    """
    def model_checkpoint_callback(self,ck_path: str):
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
