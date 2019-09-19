# import packages
import serial
import platform
import sys
import numpy as np
import pandas as pd
import nn_util.nn_util as nn_util

# script options
classify = 1
regression_1d = 1

# init
correction_factor = 0

if ~regression_1d:
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

# run the data acquisition loop and estimate the 
while True:

    try:

        sobj.flushInput()
        sobj.flushOutput()
        output = sobj.readline()
        output = output.decode("utf-8")

        result = [x.strip() for x in output.split(',')]
        measurements = result[1::2]

        measurements_np = np.asarray(measurements).astype(float)
        print(measurements_np)

        if classify:

            if regression_1d:
                x = measurements_np[4]
                a1 = 316.6398
                b1 = 4.9845e-04
                c1 = 2.3296
                a2 = 97.1001
                b2 = 0.0019
                c2 = 3.2029
                correction_factor = (a1 * np.sin(b1 * x + c1) + a2 * np.sin(b2 * x + c2)) / 100

            else:
                # normalize the data
                measurements_normalized = nn_util.norm(measurements_np)

                # predict blood/water ratio with nn
                measure_df = pd.DataFrame(measurements_normalized).transpose()
                prediction = model.predict(measure_df).flatten()
                print("Prediction: " + str(prediction))
                correction_factor = prediction / 100

            if correction_factor > 1:
                correction_factor = 1
            elif correction_factor < 0:
                correction_factor = 0

    except Exception as e:
        print(str(e))
        print('could not read sensor')

    print('Estimated correction factor: ' + str(correction_factor))
