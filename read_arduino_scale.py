# import packages
import serial
import platform
import sc3nb

# serial communication
if platform.system() == 'Windows':
    sobj = serial.Serial('COM5', 9600)
elif platform.system() == 'Darwin':
    # Mac serial call goes here - add your COM Port
    sobj = serial.Serial('/dev/tty.usbserial-14310', 115200)

# initialization
max_grams = 0
output_volume = 0
d_volume_old = 0
dd_volume = 0
d_grams = 0
volume_accumulated = 0


def get_correction(d_volume, correction_factor=1):
    return d_volume * correction_factor


# run data acquisition loop
while True:

    # read the weight from Hx711
    grams = sobj.readline()
    grams = float(grams.decode("utf-8"))
    # print(grams)

    if grams > max_grams:
        d_grams = grams - max_grams
        max_grams = grams
    else:
        d_grams = 0

    # apply correction factor from spectrometer to only get the blood amount
    d_volume_blood = get_correction(d_grams) / 1.060

    # compute accumulated blood volume
    volume_accumulated += d_volume_blood

    # trend of volume change
    dd_volume = d_volume_blood - d_volume_old
    d_volume_old = d_volume_blood

    # output
    print("Accumulated: " + str(int(volume_accumulated)))
    print("Delta: " + str(int(d_volume_blood)))
    print("Trend: " + str(int(dd_volume)))

