import tensorflow as tf
from tensorflow import keras
from tensorflow.contrib.keras import layers
import pandas as pd

# PARAMETERS
units = 64

# load the training statistics from the last training from log file
train_stats = pd.read_csv('nn_util/train_stats.csv')

# model definition
def build_model(num_keys):
    keras_model = keras.Sequential([
        layers.Dense(units, activation=tf.nn.relu, input_shape=[]),
        layers.Dense(units, activation=tf.nn.relu),
        layers.Dense(units, activation=tf.nn.relu),
        layers.Dense(units, activation=tf.nn.relu),
        layers.Dense(1)
    ])

    optimizer = tf.keras.optimizers.RMSprop(0.001)

    keras_model.compile(loss='mean_squared_error',
                        optimizer=optimizer,
                        metrics=['mean_absolute_error', 'mean_squared_error'])
    return keras_model

# normalize data
def norm(x):
    return (x - train_stats['mean']) / train_stats['std']
