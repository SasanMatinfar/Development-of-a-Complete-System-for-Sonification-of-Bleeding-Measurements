import threading
import os
import time
import logging
import matplotlib.pyplot as plt
import random

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from time import sleep
import matlab.engine


class Bloodplayer:

    def __init__(self, data, verbose=True):
        self.volume_accumulated = 0
        self.lock = threading.RLock()
        self.stopevent = threading.Event()
        self.callback_fn = None
        self.idx = 0
        self.verbose = verbose
        self.data = data
        self.length = data.shape[0]

        self.vs0 = [None]
        self.vs1 = [None]
        self.vs2 = [None]
        self.xs = [0]
        self.ts = [None]
        self.ys = [None]

        self.eng = matlab.engine.start_matlab()
        self.start = 150.0
        self.i = 0

    def callback_fn_default(self, v):
        os.write(1, f"\r                       \r{v}".encode())

    def procfn(self):
        self.idx += 1
        while not self.stopevent.wait(0):
            try:
                self.idx = 0
                while not self.stopevent.wait(0) and self.idx < self.length - 1:
                    v = self.data[self.idx]
                    if self.verbose:
                        os.write(1, f"\r{self.idx}:{self.idx}                   ".encode())
                    if callable(self.callback_fn):
                        self.callback_fn(self)
                    else:
                        self.callback_fn_default(v)
                    self.idx += self.idx
                    time.sleep(1)
                print("done.")
                time_now = time.time()
                self.i += 1
                print("loop iteration: " + str(self.i))
                if self.i % 2 == 1:
                    stop = self.start + 500.0
                    self.eng.plot_anim(self.start, stop)
                    print("start: " + str(self.start ))
                    self.start = self.start + 500.0
                    print("stop: " + str(self.start ))
                else:
                    stop = self.start - 500.0
                    self.eng.plot_anim(self.start , stop)
                    print("start: " + str(self.start ))
                    self.start = self.start - 500.0
                    print("stop: " + str(self.start ))
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
