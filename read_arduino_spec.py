# import packages
import serial
import platform
import time
import csv
from os import path
import keyboard

# serial communication
if platform.system() == 'Windows':
    sobj = serial.Serial('COM6', 115200)

elif platform.system() == 'Darwin':
    # Mac serial call goes here - add your COM Port
    sobj = serial.Serial('/dev/tty.usbserial-14110', 115200)


with open(path.join('calibration/', 'log_calibration' + str(time.time()) + '.csv'), 'w', newline='') as csv_file:

    csv_writer = csv.writer(csv_file, delimiter=',', dialect='excel')
    csv_writer.writerow(['610 nm', '680 nm', '730 nm', '760 nm', '810 nm', '860 nm', '560 nm', '585 nm', '645 nm',
                        '705 nm', '900 nm', '940 nm', '410 nm', '435 nm', '460 nm', '485 nm', '510 nm', '535 nm'])

    while True:

        output = sobj.readline()
        output = output.decode("utf-8")

        result = [x.strip() for x in output.split(',')]
        measurements = result[1::2]

        if keyboard.is_pressed('ctrl'):  # if key 'q' is pressed
            csv_writer.writerow(measurements)
            print("writing...")

        if keyboard.is_pressed('esc'):
            csv_writer.close()
            break

        print(measurements)
