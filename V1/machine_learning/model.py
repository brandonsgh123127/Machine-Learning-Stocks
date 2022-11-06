import os
from abc import ABC
from pathlib import Path
from random import random

from keras import regularizers, layers, initializers, optimizers, callbacks
from tensorflow.python.keras import Input
from tensorflow.python.keras.models import Model, load_model

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from V1.data_generator.generate_sample import Sample


class NN_Model(ABC):
    def __init__(self, choice: int):
        self.nn_input = None
        self.path = Path(os.getcwd()).absolute()
        self.model_map_names = {"relu_multilayer_l2": 1, "relu_2layer_0regularization": 2,
                                "relu_2layer_dropout_l2_noout": 3, "relu_2layer_l1l2": 4,
                                "relu_1layer_l2": 5, "relu_2layer_dropout_l2_out": 6}
        self.model_name = self.get_mapping(choice)
        self.model_choice: int = choice
        self.model=None

    def get_mapping(self, choice: int):
        return list(self.model_map_names.keys())[list(self.model_map_names.values()).index(choice)]

    def create_model(self):
        if 0 < self.model_choice <= 6:
            nn_input = Input(shape=(1, 126))  # 14 * 8 cols
        elif 6 < self.model_choice <= 12:
            nn_input = Input(shape=(1, 126))  # 14 * 8 cols

        if 0 < self.model_choice <= 6:
            if self.model_choice == 1:
                nn = layers.Dense(126, activation=layers.LeakyReLU(alpha=0.3),
                                        activity_regularizer=regularizers.l2(0.01))(
                    nn_input)
                nn = layers.Dropout(0.25)(nn)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.3),
                                        activity_regularizer=regularizers.l2(0.01))(nn)
                nn2 = layers.Dense(1, activation='linear', activity_regularizer=regularizers.l2(0.01))(
                    nn)

            elif self.model_choice == 2:
                nn = layers.Dense(126, activation=layers.LeakyReLU(alpha=0.3))(
                    nn_input)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.3))(nn)
                nn = layers.Dropout(0.25)(nn)
                nn = layers.Dense(24, activation=layers.LeakyReLU(alpha=0.2))(nn)
                nn2 = layers.Dense(1, activation='linear')(nn)

            elif self.model_choice == 3:
                nn = layers.Dense(126, activation=layers.LeakyReLU(alpha=0.3),
                                        activity_regularizer=regularizers.l2(0.01))(
                    nn_input)
                nn = layers.Dropout(0.25)(nn)
                nn = layers.Dense(56, activation=layers.LeakyReLU(alpha=0.3),
                                        activity_regularizer=regularizers.l2(0.01))(nn)
                nn = layers.Dense(22, activation=layers.LeakyReLU(alpha=0.3),
                                        activity_regularizer=regularizers.l2(0.01))(nn)
                nn = layers.Dropout(0.25)(nn)
                nn2 = layers.Dense(1, activation='linear')(
                    nn)

            elif self.model_choice == 4:
                nn = layers.Dense(126,
                                        kernel_initializer=initializers.GlorotNormal(seed=None))(
                    nn_input)
                nn = layers.Dense(44, activation=layers.LeakyReLU(alpha=0.5))(nn)
                nn = layers.Dropout(0.25)(nn)
                nn = layers.Dense(12, activation=layers.LeakyReLU(alpha=0.2),
                                        kernel_regularizer=regularizers.l1_l2(0.01, 0.002))(nn)
                nn2 = layers.Dense(1, activation='sigmoid')(nn)

            elif self.model_choice == 5:
                nn = layers.Dense(126, activation=layers.LeakyReLU(alpha=0.3))(
                    nn_input)
                nn = layers.Dense(36, activation=layers.LeakyReLU(alpha=0.3))(nn)
                nn2 = layers.Dense(1, activation='sigmoid')(nn)

            elif self.model_choice == 6:
                nn = layers.Dense(126, activation=layers.LeakyReLU(alpha=0.3))(
                    nn_input)
                nn = layers.Dropout(0.33)(nn)
                nn = layers.Dense(84, activation=layers.LeakyReLU(alpha=0.3))(nn)
                nn = layers.Dense(10, activation=layers.LeakyReLU(alpha=0.3))(nn)
                nn2 = layers.Dense(1, activation='softmax')(
                    nn)

            # Convert to a model
            nn = Model(inputs=nn_input, outputs=[nn2])
            nn.compile(optimizer=optimizers.Adam(lr=0.01, beta_1=0.90, beta_2=0.997), loss='mse',
                       metrics=['MeanAbsoluteError', 'MeanSquaredError'])

        elif 6 < self.model_choice <= 12:
            if self.model_choice == 1:
                nn = layers.Dense(126,
                                        kernel_initializer=initializers.GlorotNormal(seed=None),
                                        activity_regularizer=regularizers.l1(0.03))(
                    nn_input)
                # nn = layers.Dropout(0.1)(nn)
                regularizers.l2(0.01)
                nn = layers.Dense(64, activation=layers.LeakyReLU(alpha=0.3))(nn)
                nn2 = layers.Dense(1, activation='linear')(nn)
            # Convert to a model
            nn = Model(inputs=nn_input, outputs=[nn2])
            nn = nn.compile(optimizer=optimizers.Adam(lr=0.01, beta_1=0.90, beta_2=0.997), loss='mse',
                       metrics=['MeanAbsoluteError', 'MeanSquaredError'])
        self.model = nn
        return nn
    def save_model(self):
        self.model.save(f'{self.path}/data/{self.model_name}')
    def choose_random_ticker(self, csv_file:str):
        with open(csv_file) as f:
            ticker = random.choice(f.readlines())
            ticker = ticker[0:ticker.find(',')]
            print(ticker)
            return ticker
    def load_model(self, name=None):
        try:
            self.model_name = name
            nn = load_model(
                f'{self.path}/data/{name}')
            for model_choice, name_loc in self.model_map_names.items():
                if name == name_loc:
                    self.model_choice = model_choice
            self.model=nn
            return nn
        except:
            print(f'[INFO] No model exists for {name}, creating new model...')
