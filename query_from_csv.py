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
    parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=57120, help="The port the OSC server is listening on")
    args = parser.parse_args()
    client = udp_client.SimpleUDPClient(args.ip, args.port)


df = pd.read_csv('logs/log_refactored_correction_factor.csv', na_values=['no info', '.'], delimiter=',')
df_indexed = df.reset_index(drop=False)

delta = df_indexed['Delta']
d_delta = df_indexed['Delta of Delta']
volume = df_indexed['Blood Accumulated']

delta_min = delta.min()
delta_max = delta.max()

d_delta_min = d_delta.min()
d_delta_max = d_delta.max()

volume_min = volume.min()
volume_max = volume.max()

print("min delta = " + str(delta_min))
print("max delta = " + str(delta_max))

print("min d_delta = " + str(d_delta_min))
print("max d_delta = " + str(d_delta_max))

print("min volume = " + str(volume_min))
print("max volume = " + str(volume_max))

client.send_message("/root/init", [delta_min, delta_max, d_delta_min, d_delta_max, volume_min, volume_max])
client.send_message("/root/play", 1)
for i in range(df_indexed.size):
    try:
        osc_msg = df_indexed.loc[i, :]
        client.send_message("/root/msg", osc_msg)
        print(osc_msg)
        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        client.send_message("/root/play", 0)
        print("Manual break by user!")
        raise


""""

"plt.hist(delta, bins=20)"
"plt.show()"
"""


