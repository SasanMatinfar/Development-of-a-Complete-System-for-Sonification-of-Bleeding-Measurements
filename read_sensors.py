# import packages
import serial
import platform
import time
import sys
import numpy as np
import pandas as pd

import nn_util.nn_util as nn_util


# parameters
checkpoint_path = "trained_network/cp.ckpt"
num_keys = 18

# load the pre-trained model
model = nn_util.build_model(num_keys)
model.load_weights(checkpoint_path)


# serial communication
try:
    if platform.system() == 'Windows':
        sobj_spectro = serial.Serial('COM6', 115200)
        sobj_scale = serial.Serial('COM10', 9600)

    elif platform.system() == 'Darwin':
        # Mac serial call goes here - add your COM Port
        sobj_spectro = serial.Serial('/dev/tty.usbmodem141101', 115200)
        sobj_scale = serial.Serial('/dev/tty.usbserial-14110', 9600)
except Exception as e:
    print('Exception Thrown: ' + str(e), file=sys.stderr)
    print('Please connect both sensors', file=sys.stderr)
    exit()


# initialization
max_grams = 0
output_volume = 0
d_volume_old = 0
dd_volume = 0
d_grams = 0
volume_accumulated = 0
water_accumulated = 0
time_now = 0
time_old = 0
d_volume_blood_sum = 0
measurements = 0

column_names = ['channel_1', 'channel_2', 'channel_3', 'channel_4', 'channel_5', 'channel_6',
                'channel_7', 'channel_8', 'channel_9', 'channel_10', 'channel_11', 'channel_12',
                'channel_13', 'channel_14', 'channel_15', 'channel_16', 'channel_17', 'channel_18',
                'target']


# apply correction factor from spectroscope sensor
def get_correction(d_volume):

    # read and decode the signal
    output = sobj_spectro.readline()
    output = output.decode("utf-8")
    result = [x.strip() for x in output.split(',')]
    measure = result[1::2]
    measurements_np = np.asarray(measure).astype(float)

    # normalize the data
    measurements_normalized = nn_util.norm(measurements_np)

    measure_df = pd.DataFrame(measurements_normalized).transpose()

    prediction = model.predict(measure_df).flatten()

    # apply the pre-trained network to get the correction factor
    correction_factor = prediction / 100

    if correction_factor > 1:
        correction_factor = 1
    elif correction_factor < 0:
        correction_factor = 0

    # print('Estimated correction factor: ' + str(correction_factor))

    return d_volume * correction_factor, prediction, measurements_np


# run data acquisition loop
while True:

    time_now = time.time()
    time.sleep(0.05)

    # read the weight from Hx711
    # sobj_scale.flush()
    grams = sobj_scale.readline()

    grams = float(grams.decode("utf-8"))
    # print(grams)

    if grams > max_grams:
        d_grams = grams - max_grams
        max_grams = grams
    else:
        d_grams = 0

    # apply correction factor from spectrometer to only get the blood amount and convert to volume
    d_volume_blood, pred, measure_np = get_correction(d_grams)
    d_volume_blood /= 1.060
    # d_volume_water = get_correction(d_grams) / 0.997

    # accumulate delta until we print it
    d_volume_blood_sum += d_volume_blood

    # compute accumulated blood volume
    volume_accumulated += d_volume_blood
    # water_accumulated += d_volume_water

    # trend of volume change
    dd_volume = d_volume_blood_sum - d_volume_old

    # print with ~1 Hz
    if (time_now - time_old) >= 1:

        # output
        print('----------------------------------------------------')
        print('Spectrogram output: ' + str(measure_np))
        print('Predicted blood percentage: ' + str(pred))
        print('----------------------------------------------------')
        print('Grams: ' + str(int(grams)))
        print("Accumulated: " + str(int(volume_accumulated)))
        # print("Water accumulated: " + str(int(water_accumulated)))
        print("Delta: " + str(int(d_volume_blood_sum)))
        print("Trend: " + str(int(dd_volume)))

        # reset timer
        time_old = time_now

        # reset helper variables
        d_volume_old = d_volume_blood_sum
        d_volume_blood_sum = 0
