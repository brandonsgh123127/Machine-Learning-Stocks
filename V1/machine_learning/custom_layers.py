import keras.layers
import tensorflow as tf

"""
Trainable Dropout

Used for when model needs dropout.
If needed, when called, requires training value, else disables dropout.

"""
class TrainableDropout(keras.layers.Layer):
    def __init__(self, rate, **kwargs):
        super(TrainableDropout, self).__init__(**kwargs)
        self.rate = rate

    def call(self, inputs, training=None):
        if training:
            return tf.nn.dropout(inputs, rate=self.rate)
        return inputs