import pandas as pd
import argparse
from pythonosc import udp_client


class OscClient:

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=57120, help="The port the OSC server is listening on")
        args = parser.parse_args()
        self.client = udp_client.SimpleUDPClient(args.ip, args.port)

        self.df = pd.read_csv('logs/log_refactored_correction_factor.csv', na_values=['no info', '.'], delimiter=',')
        self.df_indexed = self.df.reset_index(drop=False)

        self.delta = self.df_indexed['Delta']
        self.d_delta = self.df_indexed['Delta of Delta']
        self.volume = self.df_indexed['Blood Accumulated']

        self.delta_min = self.delta.min()
        self.delta_max = self.delta.max()
        self.d_delta_min = self.d_delta.min()
        self.d_delta_max = self.d_delta.max()
        self.volume_min = self.volume.min()
        self.volume_max = self.volume.max()

        # print("min delta = " + str(self.delta_min))
        # print("max delta = " + str(self.delta_max))

        # print("min d_delta = " + str(self.d_delta_min))
        # print("max d_delta = " + str(self.d_delta_max))

        # print("min volume = " + str(self.volume_min))
        # print("max volume = " + str(self.volume_max))

        self.client.send_message("/root/init", [self.delta_min, self.delta_max, self.d_delta_min, self.d_delta_max, self.volume_min, self.volume_max])
        self.client.send_message("/root/play", 1)
        print("init and play sent")

    def run(self, i):
        try:
            osc_msg = self.df_indexed.loc[i, :]
            self.client.send_message("/root/msg", osc_msg)
            print(osc_msg)
        except (KeyboardInterrupt, SystemExit):
            self.client.send_message("/root/play", 0)
            print("Manual break by user or data missed!")
            raise

    def stop(self):
        self.client.send_message("/root/play", 0)
        print("stop sent")
