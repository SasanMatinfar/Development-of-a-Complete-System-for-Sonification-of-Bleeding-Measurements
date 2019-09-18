# import packages
import serial
import platform
import time
import csv
from os import path
import sys
import numpy as np
import keyboard

import nn_util.nn_util as nn_util
import pandas as pd

# script options
classify = 1

if classify:
    # parameters
    checkpoint_path = "trained_network/cp.ckpt"
    num_keys = 18

    # load the pre-trained model
    model = nn_util.build_model(num_keys)
    model.load_weights(checkpoint_path)

# serial communication
try:
    if platform.system() == 'Windows':
        sobj = serial.Serial('COM6', 115200)

    elif platform.system() == 'Darwin':
        # Mac serial call goes here - add your COM Port
        sobj = serial.Serial('/dev/tty.usbmodem141101', 115200)
except Exception as e:
    print(e, file=sys.stderr)
    exit()

with open(path.join('calibration/calibration3/', 'log_calibration' + str(time.time()) + '.csv'), 'w', newline='') as csv_file:

    csv_writer = csv.writer(csv_file, delimiter=',', dialect='excel')
    csv_writer.writerow(['610 nm', '680 nm', '730 nm', '760 nm', '810 nm', '860 nm', '560 nm', '585 nm', '645 nm',
                         '705 nm', '900 nm', '940 nm', '410 nm', '435 nm', '460 nm', '485 nm', '510 nm', '535 nm'])
    while True:

        try:

            sobj.flushInput()
            sobj.flushOutput()
            output = sobj.readline()
            output = output.decode("utf-8")

            result = [x.strip() for x in output.split(',')]
            measurements = result[1::2]

            #if keyboard.is_pressed('ctrl'):  # if key 'q' is pressed
            csv_writer.writerow(measurements)
                #print("writing...")

            if keyboard.is_pressed('esc'):
                csv_writer.close()
                break

            measurements_np = np.asarray(measurements).astype(float)

            print(measurements_np)

            if classify:

                # normalize the data
                measurements_normalized = nn_util.norm(measurements_np)

                # predict blood/water ratio with nn
                measure_df = pd.DataFrame(measurements_normalized).transpose()
                prediction = model.predict(measure_df).flatten()
                correction_factor = prediction / 100

                if correction_factor > 1:
                    correction_factor = 1
                elif correction_factor < 0:
                    correction_factor = 0

                print('Estimated correction factor: ' + str(correction_factor))

        except Exception as e:
            print(str(e))
            print('could not read sensor')

