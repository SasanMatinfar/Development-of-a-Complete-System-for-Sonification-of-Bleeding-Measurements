# import packages
import serial
import math
import sc3nb

# initialization
sobj = serial.Serial('COM5', 115200)
x_sensor = 333.16
max_volume = 0
output_volume = 0
d_volume_old = 0
dd_volume = 0
d_volume = 0
volume_accumulated = 0


def diameter_x(x):
    output = (x_sensor-x)/335*(122.5-109.1)+109.1
    return output


def get_correction(d_volume, correction_factor=1):
    return d_volume * correction_factor


# run data acquisition loop
while True:

    # read the distance from HC-SR04
    distance = sobj.readline()
    distance = float(distance.decode("utf-8"))
    # print(distance)

    # fluid volume
    if distance < x_sensor:

        # for medela PSU 3L
        volume = 1/3 * math.pi * (x_sensor - distance) * ((109.1/2) ** 2 + 109.1/2 * diameter_x(distance)/2 + (diameter_x(distance)/2) ** 2)
        volume_ml = 1e-3 * volume

        if volume_ml > max_volume:
            d_volume = volume_ml - max_volume
            max_volume = volume_ml
            output_volume = volume_ml
        else:
            output_volume = max_volume
            d_volume = 0

        # apply correction factor from spectrometer to only get the blood amount
        d_volume = get_correction(d_volume)

        # compute accumulated blood volume
        volume_accumulated += d_volume

        # trend of volume change
        dd_volume = d_volume - d_volume_old
        d_volume_old = d_volume

    # output
    print("Accumulated: " + str(int(output_volume)))
    print("Delta: " + str(int(d_volume)))
    print("Trend: " + str(int(dd_volume)))

