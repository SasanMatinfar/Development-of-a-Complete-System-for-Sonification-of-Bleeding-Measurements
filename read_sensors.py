"""Script for prediction of blood volume for the surgical suction

Serial communication with sensors:
 -- blood/water ratio predicted from AMS AS7265X Sensor output
 -- weight read from HX711 ADC

Change parameter 'linear_regression_only' to:
    -- 'True' to use sum of sine fit
    -- 'False'  to use neural network
"""

# import packages
import serial
import platform
import time
import sys
import numpy as np
import pandas as pd
import nn_util.nn_util as nn_util

# option to use simple 1D linear regression instead of neural network
linear_regression_only = 1

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
        sobj_scale = serial.Serial('COM4', 9600)

    elif platform.system() == 'Darwin':
        # Mac serial call goes here - add your COM Port
        sobj_spectro = serial.Serial('/dev/tty.usbmodem143101', 115200)
        sobj_scale = serial.Serial('/dev/tty.usbserial-1410', 9600)

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
correction_factor_current = 0


# apply correction factor from spectroscope sensor
def get_correction(d_volume):

    # init
    global correction_factor_current
    measurements_np = []

    # read and decode the signal
    sobj_spectro.flushInput()  # flush the buffer
    output = sobj_spectro.readline()
    output = output.decode("utf-8")
    result = [x.strip() for x in output.split(',')]
    measure = result[1::2]
    try:

        # convert to np array
        measurements_np = np.asarray(measure).astype(float)

        # normalize the data
        measurements_normalized = nn_util.norm(measurements_np)

        if linear_regression_only:
            # we use a second order sum of sine fit
            x = measurements_np[4]
            a1 = 316.6398
            b1 = 4.9845e-04
            c1 = 2.3296
            a2 = 97.1001
            b2 = 0.0019
            c2 = 3.2029
            correction_factor = (a1 * np.sin(b1 * x + c1) + a2 * np.sin(b2 * x + c2)) / 100
        else:
            # predict blood/water ratio with neural net
            measure_df = pd.DataFrame(measurements_normalized).transpose()
            prediction = model.predict(measure_df).flatten()
            correction_factor = prediction / 100

        if correction_factor > 1:
            correction_factor = 1
        elif correction_factor < 0:
            correction_factor = 0

        correction_factor_current = correction_factor

    except Exception as exc:
        # spectrometer overflow indicates water only
        correction_factor_current = 0
        print(str(exc))
        print('Spectrometer overflow')

    return d_volume * correction_factor_current, correction_factor_current, measurements_np


# run data acquisition loop
while True:

    try:
        time_now = time.time()
        time.sleep(0.05)

        # read the weight from Hx711
        sobj_scale.flushInput()  # flush the buffer
        grams = sobj_scale.readline()
        grams = float(grams.decode("utf-8"))

        # assert no negative measurements
        if grams > max_grams:
            d_grams = grams - max_grams
            max_grams = grams
        else:
            d_grams = 0

        # apply correction factor from spectrometer to only get the blood amount and convert to volume
        d_volume_blood, pred, measure_np = get_correction(d_grams)
        d_volume_blood /= 1.060

        # accumulate delta until we print it
        d_volume_blood_sum += d_volume_blood

        # trend of volume change
        dd_volume = d_volume_blood_sum - d_volume_old

        # print with ~1 Hz
        if (time_now - time_old) >= 1:

            # output
            print('----------------------------------------------------')
            print('Spectrogram output: ' + str(measure_np))
            print('Predicted correction factor: ' + str(pred))
            print('----------------------------------------------------')
            print('Grams: ' + str(int(grams)))
            print("Accumulated blood: " + str(int(d_volume_blood_sum)))
            # print("Water accumulated: " + str(int(water_accumulated)))
            print("Delta: " + str(int(d_volume_blood_sum)))
            print("Trend: " + str(int(dd_volume)))

            # reset timer
            time_old = time_now

            # reset helper variables
            d_volume_old = d_volume_blood_sum
            d_volume_blood_sum = 0

    except Exception as e:
        print(str(e))
        print('Could not read sensor output')
        time.sleep(0.5)
