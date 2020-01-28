import time
import os
import numpy as np
import sc3nb as scn
import logging
import sys
import matplotlib
import matplotlib.pyplot as plt


from matplotlib.animation import FuncAnimation
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from blood_player import Bloodplayer
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


from IPython.display import clear_output
from ipywidgets import interact, interactive, fixed, interact_manual, Layout

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation



logger = logging.getLogger()
fhandler = logging.FileHandler(filename='mylog.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)


sc = scn.startup()

#sc.cmd("s.plotTree")
#sc.cmd("s.meter")


# Buffers
buffers = [
    sc.Buffer().load_file("samples-normalized/water-shake.wav"),
    sc.Buffer().load_file("samples-normalized/rain.wav"),
    sc.Buffer().load_file("samples-normalized/thunder.wav"),
    sc.Buffer().load_file("samples-normalized/seagulls_tuned.wav"),
    sc.Buffer().load_file("samples-normalized/bell.wav"),
    sc.Buffer().load_file("samples-normalized/bell2.wav"),
    sc.Buffer().load_file("samples-normalized/Kalimba_Dry_fadeIO.wav"),
]

water = buffers[0].bufnum
rain = buffers[1].bufnum
thunder = buffers[2].bufnum
seagulls = buffers[3].bufnum
bell = buffers[4].bufnum
bell2 = buffers[5].bufnum
kalimba_dry = buffers[6].bufnum

bufnums = [[water, seagulls, rain],
           [seagulls]]

# buffer in SC
sc.cmd("""
~b = Buffer.read(s, "/Users/sasan/Desktop/MasterThesis/arduinoserial/LiveDemoApp/samples-normalized/bell.wav");
""")

# WaveTables
sc.cmd("""
~wt_sig = 10.collect({
    arg i;
    var numSegs = i.linexp(0,9,4,40).round;

    Env(
        [0]++({1.0.rand}.dup(numSegs-1) * [1,-1]).scramble++[0],
        {exprand(1,i.linexp(0,9,1,50))}.dup(numSegs),
        {[\sine,0,exprand(1,20) * [1,-1].choose].wchoose([9-i,3,i].normalizeSum)}.dup(numSegs)
    ).asSignal(1024);
});

~wt_buf = Buffer.allocConsecutive(10, s, 2048, 1, {
    arg buf, index;
    buf.setnMsg(0, ~wt_sig[index].asWavetable);
});
""")

# SynthDefs
sc.cmd("""
SynthDef("pb-simple", { 
    arg out=0, bufnum=0, rate=1, pan=0, amp=0.3, loop=1, 
    lgrt=2, lgamp=0.5, cf=1000, rq=1, mix=0, room=0, damp=0.5; 
    
    var sig;
    
    sig = PlayBuf.ar(2, bufnum, rate.lag(lgrt)*BufRateScale.kr(bufnum), loop: loop, doneAction: 2);
    sig = BPF.ar(sig, cf, rq);
    sig = FreeVerb2.ar(sig, sig, mix, room, damp);
    
    Out.ar(out, Pan2.ar(sig, pan, amp.lag(lgamp)));
}).add;

SynthDef("bell", {
    |fs=1, t60=1, pitchy=1, amp=0.25, gate=1|
    var sig, exciter;
    //exciter = Impulse.ar(0);
    exciter = WhiteNoise.ar() * EnvGen.ar(Env.perc(0.001, 0.05), gate) * 0.25;
    sig = Klank.ar(
        `[
            [1, 2, 2.803, 3.871, 5.074, 7.81, 10.948, 14.421],   // freqs
            [1, 0.044, 0.891, 0.0891, 0.794, 0.1, 0.281, 0.079], // amplitudes
            [1, 0.205, 1, 0.196, 0.339, 0.047, 0.058, 0.047]*t60     // ring times
        ],
        exciter,
        freqscale:fs*pitchy);
    sig = FreeVerb.ar(sig) * amp;
    DetectSilence.ar(sig, 0.001, 0.5, doneAction:2);
    Out.ar(0, sig!2);
}).add;

SynthDef("bpfsaw", {
    arg atk=2, sus=0, rel=3, c1=1, c2=(-1),
    freq=500, detune=0.2, pan=0, cfhzmin=0.1, cfhzmax=0.3,
    cfmin=500, cfmax=2000, rqmin=0.1, rqmax=0.2,
    lsf=200, ldb=0, amp=1, out=0;
    
    var sig, env;
    
    env = EnvGen.kr(Env([0,1,1,0],[atk,sus,rel],[c1,0,c2]),doneAction:2);
    
    sig = Saw.ar(freq * {LFNoise1.kr(0.5,detune).midiratio}!2);
    sig = BPF.ar(
        sig,
        {LFNoise1.kr(
            LFNoise1.kr(4).exprange(cfhzmin,cfhzmax)
        ).exprange(cfmin,cfmax)}!2,
        {LFNoise1.kr(0.1).exprange(rqmin,rqmax)}!2
    );
    sig = BLowShelf.ar(sig, lsf, 0.5, ldb);
    sig = Balance2.ar(sig[0], sig[1], pan);
    sig = sig * env * amp;
    
    Out.ar(out, sig);
}).add;

SynthDef("bpfsine", {
    arg atk=2, sus=0, rel=3, c1=1, c2=(-1),
    freq=500, detune=0.2, pan=0, cfhzmin=0.1, cfhzmax=0.3,
    cfmin=500, cfmax=2000, rqmin=0.1, rqmax=0.2,
    lsf=200, ldb=0, amp=1, out=0;
    var sig, env;
    env = EnvGen.kr(Env([0,1,1,0],[atk,sus,rel],[c1,0,c2]),doneAction:2);
    sig = SinOsc.ar(freq * {LFNoise1.kr(0.5,detune).midiratio}!2);
    sig = BPF.ar(
        sig,
        {LFNoise1.kr(
            LFNoise1.kr(4).exprange(cfhzmin,cfhzmax)
        ).exprange(cfmin,cfmax)}!2,
        {LFNoise1.kr(0.1).exprange(rqmin,rqmax)}!2
    );
    sig = BLowShelf.ar(sig, lsf, 0.5, ldb);
    sig = Balance2.ar(sig[0], sig[1], pan);
    sig = sig * env * amp;
    Out.ar(out, sig);
}).add;

SynthDef(\osc, {
    arg buf=0, freq=200, detune=0.2,
    amp=0.2, pan=0, out=0, rout=0, rsend=(-20),
    atk=0.01, sus=1, rel=0.01, c0=1, c1=(-1);
    var sig, env, detuneCtrl;
    env = EnvGen.ar(
        Env([0,1,1,0],[atk,sus,rel],[c0,0,c1]),
        doneAction:2
    );
    
    detuneCtrl = LFNoise1.kr(0.1!8).bipolar(detune).midiratio;
    sig = Osc.ar(buf, freq * detuneCtrl, {Rand(0,2pi)}!8);

    sig = Splay.ar(sig);
    sig = LeakDC.ar(sig);
    sig = Balance2.ar(sig[0], sig[1], pan, amp);
    sig = sig * env;
    Out.ar(out, sig);
    Out.ar(rout, sig * rsend.dbamp);
}).add;

﻿SynthDef(\\bpfbuf, {
    arg atk=0, sus=0, rel=3, c1=1, c2=(-1),
    buf=0, rate=1, spos=0, freq=440, rq=1, bpfmix=0,
    pan=0, amp=1, out=0;
    var sig, env;
    env = EnvGen.kr(Env([0,1,1,0],[atk,sus,rel],[c1,0,c2]),doneAction:2);
    sig = PlayBuf.ar(1, buf, rate*BufRateScale.ir(buf),startPos:spos);
    sig = XFade2.ar(sig, BPF.ar(sig, freq, rq, 1/rq.sqrt), bpfmix*2-1);
    sig = sig * env;
    sig = Pan2.ar(sig, pan, amp);
    Out.ar(out, sig);
}).add;

SynthDef("reverb", {
    arg in, predelay=0.1, revtime=1.8,
    lpf=4500, mix=0.15, amp=1, out=0;
    
    var dry, wet, temp, sig;
    
    dry = In.ar(in,2);
    temp = In.ar(in,2);
    wet = 0;
    temp = DelayN.ar(temp, 0,2, predelay);
    16.do{
        temp = AllpassN.ar(temp, 0.05, {Rand(0.001,0.05)}!2, revtime);
        temp = LPF.ar(temp, lpf);
        wet = wet + temp;
    };
    
    sig = XFade2.ar(dry, wet, mix*2-1, amp);
    
    Out.ar(out, sig);
}).add;
""")

# Busses
sc.cmd("""
~bus = Dictionary.new;
~bus.add(\\reverb -> Bus.audio(s,2));
""")

time.sleep(1)

# Reverb
sc.cmd("""
~out = 0;
~mainGroup = Group.new;
~reverbGroup = Group.after(~mainGroup);
~reverbSynth = Synth.new(\\reverb, [
        \\amp, 1,
        \predelay, 0.8,
        \\revtime, 0.5,
        \lpf, 4500,
        \mix, 0.4,
        \in, ~bus[\\reverb],
        \out, ~out,
    ], ~reverbGroup
);
""")

# Pbinds
sc.cmd("""
~paddur_min = 4.5;
~paddur_max = 5.5;
~volume_scale = 1;
~bufnum = 1;
~detune_factor = 1;
~mdur_min = 0.99;
~mdur_max = 1;
~mfreq = 1;
~mdetune = 0;
~mrq_min = 0.005;
~mrq_max = 0.008;
~mcf = 1;
~matk = 3;
~msus = 1;
~mrel = 5;
~mamp = 0.9;
~mpan_min = 0;
~mpan_max = 0;


e = Dictionary.new;

e.add(\pad_sine_lf -> {
    ~chords = Pbind(
        \instrument, \osc,
        \dur, Pwhite(Pfunc{~paddur_min}, Pfunc{~paddur_max}),
        \midinote, Pxrand([
            [23,35,54,63,64],
            [45,52,54,59,61,64],
            [28,40,47,56,59,63],
            [42,52,57,61,63]
        ], inf),
        \detune, Pexprand(0.05,0.1) * Pfunc{~detune_factor},
        \\atk, Pexprand(2,4),
        \sus, 0,
        \\rel, Pexprand(4,6),
        \c0, Pexprand(1,2),
        \c1, Pexprand(1,2).neg,
        \pan, Pwhite(-0.4,0.4),
        \\amp, Pexprand(0.001,0.002) * Pfunc{~volume_scale},
        \\buf, Pfunc{~bufnum},
        \group, ~mainGroup,
        \out, ~bus[\\reverb],
    ).play;
    
    ~marimba = Pbind(
        \instrument, "bpfsaw",
        \dur, Pwhite(Pfunc{~mdur_min}, Pfunc{~mdur_max}),
        \\freq, Prand([1/2, 2/3, 1], inf) * Pfunc{~mfreq},
        \detune, Pfunc({~mdetune}),
        \\rqmin, Pfunc{~mrq_min},
        \\rqmax, Pfunc{~mrq_max},
        \cfmin, Prand((Scale.major.degrees+64).midicps,inf) *
        (Prand(([1,2,4]), inf) * round((Pfunc{~mcf}))),
        \cfmax, Pkey(\cfmin) * Pwhite(1.008,1.025),
        \\atk, Pfunc{~matk},
        \sus, Pfunc{~msus},
        \\rel, Pfunc{~mrel},
        \\amp, Pfunc{~mamp},
        \pan, Pwhite(Pfunc{~mpan_min},Pfunc{~mpan_max}),
        \group, ~mainGroup,
        \out, ~bus[\\reverb],
    ).collect({ |event|
    ~marimba_oneEvent = event;
    }).play;
});

e.add(\oneshot -> {
    ~glocke = Pbind(
        \instrument, "bpfbuf",
        \dur, Pexprand(1, 2),
        \\atk, Pexprand(0.1, 2),
        \sus, Pexprand(2.5, 6),
        \\rel, Pexprand(1.0, 5.0),
        \c1, Pexprand(1, 8),
        \c2, Pexprand(-8, -1),
        \\buf, ~b,
        \\rate, Pexprand(1, 2),
        \\freq, (Scale.major.degrees.choose+64 + [-12,0,12,24].choose).midicps,
        \\rq, Pexprand(0.002,0.02),
        \\bpfmix, 0,
        \\amp, Pexprand(0.5, 1),
        \spos, Pexprand(0, 100000),
        \out, ~bus[\\reverb],
        \group, ~mainGroup,
    ).play;
});


e.add(\stop -> {
    ~marimba.stop;
    ~chords.stop;
});

""")


if __name__ == '__main__':
    bloodplayer = Bloodplayer()
    factor_v0 = 1
    factor_v1 = 1
    factor_v2 = 1
    v0 = [0, 0]
    v1 = [0, 0]
    v2 = [0, 0]
    v4 = [0, 0]
    takt = [0, 0]
    amp = [0, 0, 0]
    rate = [0, 0, 0]
    pan = [0, 0, 0]
    node_base_cont = 5000
    node_base_event = 5010
    node_base_clock = 5050

    ##############################################    GUI PARAMETERS    #############################################

    bloodplayer.volume_accumulated = 0
    volume_max = 1000
    volume_threshold = 0  # ml threshold for volume

    delta_scale = 1
    delta_max = 20

    marimba_amp_range = [0.5, 1.5]

    tau4_amp = 0
    tau4_range = [1, 10]
    tau4_amp_range = [0, 0.5]
    tau4_rate = 1
    thrs_delta_tau4 = 0

    clock_event_amp = 0.05
    clock_event_rate = 1.5
    #thrs_tau4_glocke = 2

    tau = [5, 20, 40, 5]
    takt_rate = 200  # one beat per each takt_rate ml

    #################################################################################################################
    # TODO make GUI for all required parameter and save them in .npy file to recreate the parameter settings:
    # TODO https://towardsdatascience.com/what-is-npy-files-and-why-you-should-use-them-603373c78883
    # TODO make executable file
    # TODO set minus values of volume to zero
    # TODO test with while instead of threading
    # TODO make clean up!!! in code and Gitlab repo. etc.
    # GUI Qt5
    #app = QApplication([])
    #window = QWidget()
    #main_layout = QHBoxLayout()
    #layout_left = QVBoxLayout()
    #layout_right = QVBoxLayout()
    #main_layout.addLayout(layout_left)
    #main_layout.addLayout(layout_right)
#
    #slider_clock_event_amp = QSlider(Qt.Horizontal)
    #slider_clock_event_amp.setFocusPolicy(Qt.StrongFocus)
    #slider_clock_event_amp.setTickPosition(QSlider.TicksAbove)
    #slider_clock_event_amp.setTickInterval(10)
    #slider_clock_event_amp.setSingleStep(1)
#
    #def slider_value_changed():
    #    global clock_event_amp
    #    value = slider_clock_event_amp.value() / 100
    #    line_edit.setText(str(value))
    #    clock_event_amp = value
    #slider_clock_event_amp.valueChanged.connect(slider_value_changed)
    #layout_left.addWidget(slider_clock_event_amp)
#
    #line_edit = QLineEdit()
    #layout_left.addWidget(line_edit)
#
    #window.setLayout(main_layout)
    #window.show()

    fig = plt.figure()
    ax = plt.axes(xlim=(-2, 4), ylim=(-2, 4))
    scat = ax.scatter(1, 1, s=10, c='r')


    def animate(i):
        scat.set_sizes([10 + i * 1000])
        return scat,


    def init(buff_list):
        if not buff_list:
            os.write(1, "no buffer needed to initiate for this sonification   ".encode())
        else:
            for i, buffer in enumerate(buff_list):
                sc.msg("/s_new", ["pb-simple", (node_base_cont + i), 1, 1, "bufnum", buffer, "rate", 1, "amp", 0])
                print('buffer initiated')

    def clock_event(buff, v, r, amp_clock):
        if v < volume_threshold:
            pass
        elif v >= volume_threshold:
            sc.msg("/s_new", ["pb-simple", node_base_clock, 1, 1, "bufnum", buff, "rate", r, "amp", amp_clock, "loop", 0])

    def sonification_algomusic_one(self):
        global revtime, mix, predelay, amp, tau4_amp, tau4_rate
        global paddur_min, paddur_max, mamp
        global mdur_min, mdur_max, mfreq, mdetune, mrq_min, mrq_max, mcf, matk, msus, mrel, mpan_min, mpan_max
        global takt_rate, freq, pasamp, passcf, volume_scale, detune_factor, bufnum, takt, anim

        delta_val = self.delta[-1] * delta_scale
        volume_val = self.volume[-1]

        revtime = scn.linlin(volume_val, 0, volume_max, 1.8, 0.8)
        revtime = np.clip(revtime, 0.8, 1.8)
        mix = scn.linlin(volume_val, 0, volume_max, 0.5, 0.1)
        mix = np.clip(mix, 0.1, 0.5)
        predelay = scn.linlin(volume_val, 0, volume_max, 0.4, 0.1)
        predelay = np.clip(predelay, 0.1, 0.4)
        amp = scn.linlin(volume_val, 0, volume_max, 0.8, 0.4)
        amp = np.clip(amp, 0.4, 0.8)
        paddur_min = 4.5 - (scn.linlin(delta_val, 0, delta_max, 0, 4))
        paddur_min = np.clip(paddur_min, 0.5, 4.5)
        paddur_max = 5.5 - (scn.linlin(delta_val, 0, delta_max, 0, 4))
        paddur_max = np.clip(paddur_max, 1.5, 5.5)
        volume_scale = scn.linlin(volume_val, 0, volume_max, 1, 10)
        volume_scale = np.clip(volume_scale, 1, 10)
        detune_factor = scn.linlin(volume_val, 0, volume_max, 1, 5)
        detune_factor = np.clip(detune_factor, 1, 5)
        bufnum = scn.linlin(volume_val, 0, volume_max, 2, 5)
        bufnum = np.clip(bufnum, 2, 5)
        mdur_min = scn.linlin(delta_val, 0, delta_max, 0.99, 0.05)
        mdur_min = np.clip(mdur_min, 0.05, 0.99)
        mdur_max = scn.linlin(delta_val, 0, delta_max, 1, 0.1)
        mdur_max = np.clip(mdur_max, 0.1, 1)
        mfreq = scn.linlin(delta_val, 0, delta_max, 1, 4)
        mfreq = np.clip(mfreq, 1, 4)
        mdetune = scn.linlin(delta_val, 0, delta_max, 0, 2)
        mdetune = np.clip(mdetune, 0, 2)
        mrq_min = scn.linlin(volume_val, 0, volume_max, 0.005, 0.09)
        mrq_min = np.clip(mrq_min, 0.005, 0.09)
        mrq_max = scn.linlin(volume_val, 0, volume_max, 0.008, 0.2)
        mrq_max = np.clip(mrq_max, 0.008, 0.2)
        mcf = scn.linlin(delta_val, 0, delta_max, 1, 5)
        mcf = np.clip(mcf, 1, 5)
        matk = scn.linlin(volume_val, 0, volume_max, 3, 2)
        matk = np.clip(matk, 2, 3)
        msus = scn.linlin(volume_val, 0, volume_max, 1, 0.5)
        msus = np.clip(msus, 0.5, 1)
        mrel = scn.linlin(volume_val, 0, volume_max, 5, 3)
        mrel = np.clip(mrel, 3, 5)

        if delta_val == 0:
            mamp = 0
        else:
            mamp = scn.linlin(delta_val, 0.1, delta_max, marimba_amp_range[0], marimba_amp_range[1])
            mamp = np.clip(mamp, marimba_amp_range[0], marimba_amp_range[1])
        mpan_min = scn.linlin(delta_val, 0, delta_max, 0, -1)
        mpan_min = np.clip(mpan_min, 0, -1)
        mpan_max = scn.linlin(delta_val, 0, delta_max, 0, 1)
        mpan_max = np.clip(mpan_max, 0, 1)

        sc.cmd("""~reverbSynth.set(\\revtime, ^revtime, \mix, ^mix, \predelay, ^predelay, \\amp, ^amp)""")
        sc.cmd("""~paddur_min = ^paddur_min""")
        sc.cmd("""~paddur_max = ^paddur_max""")
        sc.cmd("""~volume_scale = ^volume_scale""")
        sc.cmd("""~detune_factor = ^detune_factor""")
        sc.cmd("""~bufnum = ^bufnum.asInteger""")
        sc.cmd("""~mdur_min = ^mdur_min""")
        sc.cmd("""~mdur_max = ^mdur_max""")
        sc.cmd("""~mfreq = ^mfreq""")
        sc.cmd("""~mdetune = ^mdetune""")
        sc.cmd("""~mrq_min = ^mrq_min""")
        sc.cmd("""~mrq_max = ^mrq_max""")
        sc.cmd("""~mcf = ^mcf""")
        sc.cmd("""~matk = ^matk""")
        sc.cmd("""~msus = ^msus""")
        sc.cmd("""~mrel = ^mrel""")
        sc.cmd("""~mamp = ^mamp""")
        sc.cmd("""~mpan_min = ^mpan_min""")
        sc.cmd("""~mpan_max = ^mpan_max""")

        # tau 4 = 10 seconds *** seagulls ***
        if len(self.volume) <= tau[3]:
            v4[0] = ((self.volume[-1] - self.volume[0]) / tau[3]) * factor_v1
        else:
            v4[0] = ((self.volume[-1] - self.volume[-(tau[3] + 1)]) / tau[3]) * factor_v1

        if self.delta[-1] < thrs_delta_tau4:
            tau4_amp = 0
            sc.msg("/n_set", [node_base_cont, "rate", 1, "amp", tau4_amp])
        else:
            tau4_amp = scn.linlin(v4[0], tau4_range[0], tau4_range[1], tau4_amp_range[0], tau4_amp_range[1])
            tau4_amp = np.clip(tau4_amp, tau4_amp_range[0], tau4_amp_range[1])
            tau4_rate = scn.linlin(v4[0], tau4_range[0], tau4_range[1], 1, 1.25)
            tau4_rate = np.clip(tau4_rate, 1, 1.25)
            sc.msg("/n_set", [node_base_cont, "rate", tau4_rate, "amp", tau4_amp])

        # clock-event for every 50 ml blood loss
        takt[0] = int(self.volume[-1] / takt_rate)
        if takt[0] > 0 and takt[0] != takt[1]:
            clock_event(kalimba_dry, self.volume[-1], clock_event_rate, clock_event_amp)
            #sc.cmd("""e[\oneshot].value;""")
        takt[1] = takt[0]

        anim = FuncAnimation(fig, animate, frames=30, interval=30, repeat=False)
        plt.pause(1)
        print("another loop iteration")

        os.write(1, f'\r{self.idx}, delta: {float(delta_val):4.2},  volume: {float(volume_val):4.2},  '
                    f'v4: {float(v4[0]):4.2},     '.encode())

    def start_algomus():
        global bloodplayer
        print("start")
        init(bufnums[1])
        bloodplayer.set_callback(sonification_algomusic_one)
        bloodplayer.create_thread()
        sc.cmd("""e[\pad_sine_lf].value;""")

    def quit_t():
        sc.msg("/n_free", node_base_cont)
        sc.msg("/n_free", node_base_cont + 1)
        sc.msg("/n_free", node_base_cont + 2)
        sc.msg("/n_free", node_base_event)

    start_algomus()
    #sys.exit(app.exec_())




    def event_off(buf_node):
        sc.msg("/n_set", [buf_node, "rate", 0.4, "amp", 0.2, "lgrt", 1, "lgamp", 1])
        time.sleep(1)
        sc.msg("/n_free", [buf_node])

    def tau_zero(self):
        # *** water *** tau 0 = 5 seconds
        if len(self.volume) <= tau[0]:
            v0[0] = ((self.volume[-1] - self.volume[0]) / tau[0]) * factor_v0
        else:
            v0[0] = ((self.volume[-1] - self.volume[-(tau[0] + 1)]) / tau[0]) * factor_v0
        amp[0] = scn.linlin(v0[0], 0, 1.5, 0.1, 0.5)
        amp[0] = np.clip(amp[0], 0.1, 0.5)
        sc.msg("/n_set", [node_base_cont, "rate", 1, "amp", amp[0], "lgrt", 3, "lgamp", 1])
        if v0[0] >= 1.5 * factor_v0:
            amp[0] = scn.linlin(v0[0], 1.5, 4, 0.5, 1)
            amp[0] = np.clip(amp[0], 0.5, 1)
            rate[0] = scn.linlin(v0[0], 1.5, 4, 1.5, 4)
            rate[0] = np.clip(rate[0], 1.5, 4)
            sc.msg("/n_set", [node_base_cont, "rate", rate[0]])

        # Event *** thunder ***
        if self.volume[-1] >= volume_threshold:

            if v0[1] < 4 * factor_v0 < v0[0]:
                sc.msg("/s_new",
                       ["pb-simple", node_base_event, 1, 1, "bufnum", thunder, "rate", 0.9, "amp", 0.6, "loop", 1,
                        "lgrt", 2, "lgamp", 2, "cf", 500])
            if v0[0] < 4 * factor_v0 < v0[1]:
                event_off(node_base_event)
            v0[1] = v0[0]

    def sonification_nature(self):
        # tau 0 = 5 seconds *** water ***
        tau_zero(self)

        # tau 1 = 30 seconds *** seagulls ***
        amp_volume = scn.linlin(self.volume[-1], 0, volume_max, 0, 1)
        amp_volume = np.clip(amp_volume, 0, 1)

        if len(self.volume) <= tau[1]:
            v1[0] = ((self.volume[-1] - self.volume[0]) / tau[1]) * factor_v1
        else:
            v1[0] = ((self.volume[-1] - self.volume[-(tau[1] + 1)]) / tau[1]) * factor_v1

        if v1[0] < 0.5 * factor_v1:
            amp[1] = (v1[0] / 2) * amp_volume
            sc.msg("/n_set", [node_base_cont + 1, "rate", 1, "amp", amp[1]])
        if v1[0] >= 0.5 * factor_v1:
            amp[1] = scn.linlin(v1[0], 0.5, 2, 0.25, 1)
            amp[1] = np.clip(amp[1], 0.25, 1) * amp_volume
            rate[1] = scn.linlin(v1[0], 0.5, 2, 1, 1.75)
            rate[1] = np.clip(rate[1], 1, 1.75)
            sc.msg("/n_set", [node_base_cont + 1, "rate", rate[1], "amp", amp[1]])

        # tau 2 = 2 minutes *** rain ***
        if len(self.volume) <= tau[2]:
            v2[0] = ((self.volume[-1] - self.volume[0]) / tau[2]) * factor_v2
        else:
            v2[0] = ((self.volume[-1] - self.volume[-(tau[2] + 1)]) / tau[2]) * factor_v2

        if v2[0] < 0.75 * factor_v2:
            sc.msg("/n_set", [node_base_cont + 2, "rate", 0.6, "amp", 0.05])

        elif v2[0] >= 0.75 * factor_v2:
            amp[2] = scn.linlin(v2[0], 0.75, 1, 0.05, 0.5)
            amp[2] = np.clip(amp[2], 0.05, 0.5) * amp_volume
            rate[2] = scn.linlin(v2[0], 0.75, 1, 0.6, 1.2)
            rate[2] = np.clip(rate[2], 0.6, 1.2)
            sc.msg("/n_set", [node_base_cont + 2, "rate", rate[2], "amp", amp[2]])

        os.write(1, f'\r{self.idx}, delta: {self.delta[-1]}, volume: {self.volume[-1]}, tau0: {float(v0[0]):4.2},  '
                    f'tau1: {float(v1[0]):4.2},  tau2: {float(v2[0]):4.2},   '.encode())

        # Volume clock-event for every 100 ml blood loss
        takt[0] = int(self.volume[-1] / takt_rate)
        if takt[0] > 0 and takt[0] != takt[1]:
            clock_event(bell, self.volume[-1], 1, 0.7)
        takt[1] = takt[0]

    def start_nature():
        global bloodplayer
        print("start")
        init(bufnums)
        bloodplayer.set_callback(sonification_nature)
        bloodplayer.create_thread()


