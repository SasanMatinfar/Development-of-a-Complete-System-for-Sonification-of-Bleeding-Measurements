import threading
import training_model
import os
import time
import csv

from os import path
from time import gmtime, strftime

import logging


class Bloodplayer:

    def __init__(self, pulse_time=1, verbose=True):
        self.volume_accumulated = 0
        self.lock = threading.RLock()
        self.stopevent = threading.Event()
        self.callback_fn = None
        self.idx = 0
        self.verbose = verbose
        self.pulse_time = pulse_time
        self.checkpoint_path = "trained_network/cp.ckpt"
        self.oneD_regression_only = 1
        self.model = training_model.build_model(18)
        self.model.load_weights(self.checkpoint_path)
        self.column_names = ['channel_1', 'channel_2', 'channel_3', 'channel_4', 'channel_5', 'channel_6',
                             'channel_7', 'channel_8', 'channel_9', 'channel_10', 'channel_11', 'channel_12',
                             'channel_13', 'channel_14', 'channel_15', 'channel_16', 'channel_17', 'channel_18',
                             'target']
        self.max_grams = 0
        self.output_volume = 0
        self.d_volume_old = 0
        self.dd_volume = 0
        self.d_grams = 0
        self.water_accumulated = 0
        self.time_old = 0
        self.d_volume_blood_sum = 0
        self.measurements = 0
        self.delta = [0]
        self.volume = [0]
        self.correction_factor_current = 0
        self.vs0 = [None]
        self.vs1 = [None]
        self.vs2 = [None]
        self.xs = [None]
        self.ts = [None]
        self.ys = [None]
        self.deltas = [0]

    def callback_fn_default(self, v):
        os.write(1, f"\r                       \r{v}".encode())

    def get_correction(self, d_volume):
        # init
        measurements_np = []
        self.correction_factor_current = 1

        return d_volume * self.correction_factor_current, self.correction_factor_current, measurements_np

    def procfn(self):
        self.idx = 0
        while not self.stopevent.wait(0):
            try:
                time_now = time.time()

                # read the weight from Hx711
                training_model.sobj_scale.flushInput()
                grams = training_model.sobj_scale.readline()
                grams = float(grams.decode("utf-8"))

                if grams > self.max_grams:
                    self.d_grams = grams - self.max_grams
                    self.max_grams = grams
                else:
                    self.d_grams = 0

                # apply correction factor from spectrometer to only get the blood amount and convert to volume
                self.d_volume_blood, pred, measure_np = self.get_correction(self.d_grams)
                self.d_volume_blood /= 1.060

                # accumulate delta until we print it
                self.d_volume_blood_sum += self.d_volume_blood

                # compute accumulated blood volume
                self.volume_accumulated += self.d_volume_blood

                # trend of volume change
                self.dd_volume = self.d_volume_blood_sum - self.d_volume_old

                # print with ~1 Hz
                if (time_now - self.time_old) >= 1:
                    self.delta.append(self.d_volume_blood_sum)
                    v = self.delta[-1]
                    self.volume.append(self.volume_accumulated)
                    if len(self.delta) > 150:
                        self.delta.pop(0)
                        self.volume.pop(0)

                    # reset timer
                    self.time_old = time_now

                    # reset helper variables
                    self.d_volume_old = self.d_volume_blood_sum
                    self.d_volume_blood_sum = 0

                    if self.verbose:
                        os.write(1, f"\r{self.idx}:{self.idx}                   ".encode())
                    if callable(self.callback_fn):
                        self.callback_fn(self)
                    else:
                        self.callback_fn_default(v)
                    self.idx += self.pulse_time
                    time.sleep(self.pulse_time)

            except Exception as e:
                print(str(e))
                print('Could not read sensor output')
                time.sleep(0.5)

        print("done.")

    def set_callback(self, fn):
        self.callback_fn = fn

    def create_thread(self):
        threadname = "BloodPlayer-thread"
        # check first if it already exists
        if threadname in [t.name for t in threading.enumerate()]:
            print("create_thread: thread is already existing, stop first")
        else:
            self.stopevent.clear()
            self.producer = threading.Thread(name=threadname, target=self.procfn, args=[])
            self.producer.start()

    def stop_thread(self):
        self.stopevent.set()