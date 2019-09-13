# import packages
import serial
import platform
import time
import csv
import os
import sys


# serial communication
try:
    if platform.system() == 'Windows':
        sobj = serial.Serial('COM12', 9600)
    elif platform.system() == 'Darwin':
        # Mac serial call goes here - add your COM Port
        sobj = serial.Serial('/dev/tty.usbserial-14110', 9600)
except Exception as e:
    print(e, file=sys.stderr)
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


# apply correction factor from spectroscope sensor
def get_correction(d_volume, correction_factor=1):
    return d_volume * correction_factor


# open csv file
with open(os.path.join('logs/', 'log_bleedinglevel_' + str(time.time()) +
                                                                            '.csv'), 'w') as csv_file:

    csv_writer = csv.writer(csv_file, delimiter=',')
    csv_writer.writerow(['Time', 'Grams', 'Blood Accumulated', 'Water accumulated', 'delta', 'delta delta'])

    # run data acquisition loop
    while True:

        time_now = time.time()

        # read the weight from Hx711
        sobj.flushInput()
        grams = sobj.readline()
        grams = float(grams.decode("utf-8"))
        # print(grams)

        if grams > max_grams:
            d_grams = grams - max_grams
            max_grams = grams
        else:
            d_grams = 0

        # apply correction factor from spectrometer to only get the blood amount and convert to volume
        d_volume_blood = get_correction(d_grams) / 1.060
        d_volume_water = get_correction(d_grams) / 0.997

        # accumulate delta until we print it
        d_volume_blood_sum += d_volume_blood

        # compute accumulated blood volume
        volume_accumulated += d_volume_blood
        water_accumulated += d_volume_water

        # trend of volume change
        dd_volume = d_volume_blood_sum - d_volume_old

        # print with ~1 Hz
        if (time_now - time_old) >= 1:
            # write csv file
            csv_writer.writerow([str(time_now), str(grams), str(volume_accumulated), str(water_accumulated),
                                 str(d_volume_blood_sum), str(dd_volume)])

            # output
            print('Grams: ' + str(int(grams)))
            print("Accumulated: " + str(int(volume_accumulated)))
            print("Water accumulated: " + str(int(water_accumulated)))
            print("Delta: " + str(int(d_volume_blood_sum)))
            print("Trend: " + str(int(dd_volume)))
            print("\n")

            # reset timer
            time_old = time_now

            # reset helper variables
            d_volume_old = d_volume_blood_sum
            d_volume_blood_sum = 0

