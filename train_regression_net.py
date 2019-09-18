from __future__ import absolute_import, division, print_function, unicode_literals

import os
import tensorflow as tf
from tensorflow import keras

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import nn_util.nn_util as nn_util

# parameters
EPOCHS = 1000
checkpoint_path = "trained_network/cp.ckpt"
dataset_path = 'calibration3/all_data.csv'

# script options
performance_plots = 0
dataset_plots = 0
test_loading = 1


# normalize data
def norm(x):
    return (x - train_stats['mean']) / train_stats['std']


# Display training progress by printing a single dot for each completed epoch
class PrintEpochs(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        if epoch % 100 == 0:
            print('Epoch: ' + str(epoch))


checkpoint_dir = os.path.dirname(checkpoint_path)

# Create checkpoint callback
cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, save_weights_only=True, verbose=1)


def plot_history(history_):
    hist = pd.DataFrame(history_.history)
    hist['epoch'] = history_.epoch

    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Abs Error [MPG]')
    plt.plot(hist['epoch'], hist['mean_absolute_error'],
             label='Train Error')
    plt.plot(hist['epoch'], hist['val_mean_absolute_error'],
             label='Val Error')
    plt.legend()

    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Square Error [$MPG^2$]')
    plt.plot(hist['epoch'], hist['mean_squared_error'],
             label='Train Error')
    plt.plot(hist['epoch'], hist['val_mean_squared_error'],
             label='Val Error')
    plt.legend()
    plt.show()


def plot_test_performance():
    plt.figure()
    plt.scatter(test_labels, test_predictions)
    plt.xlabel('True Values [MPG]')
    plt.ylabel('Predictions [MPG]')
    plt.axis('equal')
    plt.axis('square')
    plt.xlim([0, plt.xlim()[1]])
    plt.ylim([0, plt.ylim()[1]])
    _ = plt.plot([-100, 100], [-100, 100])
    plt.show()

    plt.figure()
    error = test_predictions - test_labels
    plt.hist(error, bins=25)
    plt.xlabel("Prediction Error [MPG]")
    _ = plt.ylabel("Count")
    plt.show()


# import spectrometer data
column_names = ['channel_1', 'channel_2', 'channel_3', 'channel_4', 'channel_5', 'channel_6',
                'channel_7', 'channel_8', 'channel_9', 'channel_10', 'channel_11', 'channel_12',
                'channel_13', 'channel_14', 'channel_15', 'channel_16', 'channel_17', 'channel_18',
                'target']
raw_dataset = pd.read_csv(dataset_path, names=column_names, na_values="?", comment='\t', sep=",",
                          skipinitialspace=True)
dataset = raw_dataset.copy()

# drop rows that could not be read
dataset = dataset.dropna()

# split data into train and test set and randomize training data
train_dataset = dataset.sample(frac=0.8, random_state=0)
test_dataset = dataset.drop(train_dataset.index)

# inspect the data
if dataset_plots:
    sns.pairplot(train_dataset[["MPG", "Cylinders", "Displacement", "Weight"]], diag_kind="kde")
    plt.show()

# show statistics of the training data set
train_stats = train_dataset.describe()
train_stats.pop("target")
train_stats = train_stats.transpose()
train_stats.to_csv('nn_util/train_stats.csv')

# Split features from labels
train_labels = train_dataset.pop('target')
test_labels = test_dataset.pop('target')

# Normalize the data
normed_train_data = norm(train_dataset)
normed_test_data = norm(test_dataset)

# build the model
model = nn_util.build_model(len(train_dataset.keys()))

# inspect the model
model.summary()

# try the model
example_batch = normed_train_data[:10]
example_result = model.predict(example_batch)
print(example_result)

# train the model with early stopping regularization
early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=50)

history = model.fit(normed_train_data, train_labels, epochs=EPOCHS,
                    validation_split=0.2, verbose=1, callbacks=[early_stop, PrintEpochs(), cp_callback])

# evaluate
if performance_plots:
    plot_history(history)

loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=0)
print("Testing set Mean Abs Error: {:5.2f} percent".format(mae))

# predict using test set
test_predictions = model.predict(normed_test_data).flatten()

# performance evaluation plots
if performance_plots:
    plot_test_performance()

if test_loading:
    # test model loading
    model = nn_util.build_model(len(train_dataset.keys()))

    _, mae, _ = model.evaluate(normed_test_data, test_labels, verbose=0)
    print("Untrained model, Mean Abs Error: {:5.2f} percent".format(mae))

    model.load_weights(checkpoint_path)
    _, mae, _ = model.evaluate(normed_test_data, test_labels, verbose=0)
    print("Restored model, Mean Abs Error: {:5.2f} percent".format(mae))

    # predict two example measurements
    np_data_100 = normed_test_data.iloc[-1].to_frame().transpose()
    np_data_0 = normed_test_data.iloc[0].to_frame().transpose()
    pred_0 = model.predict(np_data_0)
    pred_100 = model.predict(np_data_100)
    print(str(pred_0))
    print(str(pred_100))
