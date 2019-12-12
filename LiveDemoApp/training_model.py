import pandas as pd
import platform
import serial
import sys
import tensorflow as tf
from tensorflow import keras
from tensorflow.contrib.keras import layers


try:
    if platform.system() == 'Windows':
        # sobj_spectro = serial.Serial('COM6', 115200)
        sobj_scale = serial.Serial('COM12', 9600)

    elif platform.system() == 'Darwin':
        # Mac serial call goes here - add your COM Port
        # sobj_spectro = serial.Serial('/dev/tty.usbmodem14301', 115200)
        sobj_scale = serial.Serial('/dev/tty.usbserial-14310', 9600)
except Exception as e:
    print('Exception Thrown: ' + str(e), file=sys.stderr)
    print('Please connect both sensors', file=sys.stderr)
    exit()

units = 18
# load the training statistics from the last training from log file
train_stats = pd.read_csv('nn_util/train_stats.csv')


# model definition
def build_model(num_keys):
    keras_model = keras.Sequential([
        layers.Dense(units, activation=tf.nn.relu, input_shape=[num_keys]),
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
