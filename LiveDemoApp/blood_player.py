import threading
import os
import time
import matlab.engine


class Bloodplayer:

    def __init__(self, data, verbose=False):
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
        self.start = 50.0
        self.stop = 50.0
        self.eng.plot_square()

    def callback_fn_default(self, v):
        os.write(1, f"\r                       \r{v}".encode())

    def procfn(self):
        self.idx = 0
        while not self.stopevent.wait(0) and self.idx < self.length - 1:
            v = self.data[self.idx]
            if self.verbose:
                os.write(1, f"\r{self.idx}:{self.idx}                   ".encode())
            if callable(self.callback_fn):
                self.callback_fn(self)
            else:
                self.callback_fn_default(v)
            self.idx += 1
            time.sleep(1)
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
