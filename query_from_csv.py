"""
OSC client
"""

import pandas as pd
import numpy as np
import argparse
import random
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client

import matplotlib.pyplot as plt
from scipy.stats import norm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=57120,
        help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)


df = pd.read_csv('logs/log_refactored.csv', delimiter = ',')
delta = df['Delta']
max_delta = delta.max()
min_delta = delta.min()
print("delta min = " + str(min_delta), "delta max = " + str(max_delta))

plt.hist(delta, bins=20)

plt.show()


"""""
for row in delta:
    try:
        d = round(row, 2)
        client.send_message("/root/delta", d)
        print(d)
        time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        print("Manual break by user!")
        raise
"""""









