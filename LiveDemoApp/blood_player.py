import threading
import os
import time
import logging
import platform
import serial
import sys


try:
    if platform.system() == 'Windows':
        serial_obj_scale = serial.Serial('COM12', 9600)
    elif platform.system() == 'Darwin':
        serial_obj_scale = serial.Serial('/dev/tty.usbserial-14120', 9600)
    print('go on')

except Exception as e:
    print('Exception Thrown: ' + str(e), file=sys.stderr)
    print('Please connect the sensor', file=sys.stderr)
    exit()


class Bloodplayer:

    def __init__(self, verbose=True):
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.callback_function = None
        self.verbose = verbose

        self.idx = 0
        self.grams_prev = 0
        self.d_grams = 0
        self.time_old = 0
        self.d_volume_blood_sum = 0
        self.volume_accumulated = 0
        self.delta = [0.0]
        self.volume = [0.0]

    def callback_function_default(self, v):
        os.write(1, f"\r                       \r{v}".encode())

    def processing_function(self):
        self.idx += 1
        while not self.stop_event.wait(0):
            try:
                time_now = time.time()

                # read the weight from Hx711
                serial_obj_scale.flushInput()
                grams = serial_obj_scale.readline()
                grams = float(grams.decode("utf-8"))

                self.d_grams = grams - self.grams_prev
                self.grams_prev = grams

                if self.d_grams < 0:
                    self.d_grams = 0

                d_volume_blood = self.d_grams / 1.060

                # accumulate delta until we print it
                self.d_volume_blood_sum += int(d_volume_blood)

                # compute accumulated blood volume
                self.volume_accumulated = int(grams / 1.060)

                # print with ~1 Hz
                if (time_now - self.time_old) >= 1:
                    self.delta.append(self.d_volume_blood_sum)
                    self.volume.append(self.volume_accumulated)
                    if len(self.delta) > 100:
                        self.delta.pop(0)
                        self.volume.pop(0)
                    logging.debug('index: ' + str(self.idx) + ', delta: ' + str(self.d_volume_blood_sum) +
                                  ", volume: " + str(self.volume_accumulated))
                    # reset timer
                    self.time_old = time_now

                    # reset delta
                    self.d_volume_blood_sum = 0

                    v = self.delta[-1]
                    if self.verbose:
                        os.write(1, f"\r{self.idx}:{self.idx}                   ".encode())
                    if callable(self.callback_function):
                        self.callback_function(self)
                    else:
                        self.callback_function_default(v)

                    self.idx += 1

            except Exception as exc:
                print(str(exc))
                print('Could not read sensor output')
                time.sleep(0.5)

        print("done.")

    def set_callback(self, fn):
        self.callback_function = fn

    def create_thread(self):
        thread_name = "BloodPlayer-thread"
        # check first if it already exists
        if thread_name in [t.name for t in threading.enumerate()]:
            print("create_thread: thread is already existing, stop first")
        else:
            self.stop_event.clear()
            self.producer = threading.Thread(name=thread_name, target=self.processing_function, args=[])
            self.producer.start()

    def stop_thread(self):
        self.stop_event.set()
