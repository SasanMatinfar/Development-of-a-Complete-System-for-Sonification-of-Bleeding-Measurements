s.plotTree;
s.meter;

//GUI
~freq; ~amp; ~pan; ~dur;
(
Window.closeAll;
w = Window("Control Pattern", Rect(750, 50, 570, 400)).front.alwaysOnTop_(true);

~sliderFreq = Slider(w, Rect(30, 30, 250, 40)).background_(Color(0.2, 0.75, 0.95)).action_({
	arg obj;
	var freq;
	freq = obj.value;
	~freq = freq;
});
~sliderAmp = Slider(w, Rect(30, 80, 250, 40)).background_(Color(0.75, 0.75, 0.95)).action_({
	arg obj;
	var amp;
	amp = obj.value;
	~amp = amp;
});
~sliderPan = Slider(w, Rect(30, 130, 250, 40)).background_(Color(0.3, 0.75, 0.2)).action_({
	arg obj;
	var pan;
	pan = obj.value;
	~pan = pan;
});
~sliderDur = Slider(w, Rect(30, 180, 250, 40)).background_(Color(0.9, 0.5, 0.95)).action_({
	arg obj;
	var dur;
	dur = obj.value;
	~dur = dur;
});
~sliderBpf = Slider(w, Rect(30, 230, 250, 40)).background_(Color(0.5, 0.5, 0.95)).action_({
	arg obj;
	var bpf;
	bpf = obj.value;
	~bpf = bpf;
});
~sliderDur = Slider(w, Rect(30, 280, 250, 40)).background_(Color(0.5, 0.5, 0.1)).action_({
	arg obj;
	var all;
	all = obj.value;
	~freq = all;
	~amp = all;
	~pan = all;
	~dur = all;
});

StaticText(w, Rect(10, 320, 70, 70))
.string_("Signal low").font("Monaco", 9);
StaticText(w, Rect(230, 320 , 70, 70))
	.string_("Signal high").font("Monaco", 9);

StaticText(w, Rect(300, 35, 300, 30))
.string_("Frequency 50:50.5 -- 75:125.5 Hz");
StaticText(w, Rect(300, 85, 300, 30))
.string_("Amplitude 0.05:0.2 -- 0.55:0.8");
StaticText(w, Rect(300, 135, 300, 30))
.string_("Pan 50:50 -- 10:90 left,right %");
StaticText(w, Rect(300, 185, 300, 30))
.string_("Duration 1.1:0.9 -- 0.4:0.01 of second");
StaticText(w, Rect(300, 235, 300, 30))
.string_("Bandpass Filter 440 -- 20 Hz");
StaticText(w, Rect(300, 285, 300, 30))
.string_("All parameters together");
)

//Synthdefs
(
SynthDef(\pad, {
    var snd, freq;
    freq = \freq.kr(300);

	// Four pulse waves (two one octave down) with randomly modulated pitches and pulse widths
    snd = Pulse.ar(
        freq * ({ LFNoise2.kr(3).range(-0.05, 0.05).midiratio }.dup(4)) * [1, 1/2, 1/2, 4],
        { LFNoise2.kr(3).range(0, 1) }.dup(4)
    );

	// Spread across stereo field
    snd = Splay.ar(snd);

	// Sharp hi cut made by cascading three lowpass filters
    4.do { snd = LPF.ar(snd, \ffreq.kr(1500)); };
    snd = snd * Env.asr(3, 1, 3, 0).ar(Done.freeSelf, \gate.kr(1));
    Out.ar(\out.kr(0-1), Balance2.ar(snd[0], snd[1], \pan.kr(0), \amp.kr(0.1)));
}).add;
)

//Organ, additive synthesis
l = [[0, 1, 0.85, 0, 0],
	[0, 1, 0.59, 0, 0],
	[0, 0.82, 0.42, 0.49, 0],
	[0, 1, 0.77, 0.21, 0],
	[0, 1, 0.393, 0.11, 0],
	[0, 1, 0.115, 0.29, 0]];
t = [[0.0125, 0.7, 0.2875, 0],
	[0.0225, 0.825, 0.1525, 0],
	[0.175, 0.475, 0.1, 0.25],
	[0.035, 0.45, 0.275, 0.24],
	[0.025, 0.3, 0.5, 0.175],
	[0.0225, 0.2, 0.3, 0.4775]];
(
SynthDef(\organ, {
	arg freq = 55, amp = 0.2, sus = 1;

	Out.ar(0, (Mix.ar({arg i;
		var k = 2;
		SinOsc.ar(freq*(2**i),
			mul: EnvGen.kr(
				Env.new(levels: [l[i][0], l[i][1], l[i][2], l[i][3], l[i][4]],
					times: [t[i][0], t[i][1], t[i][2], t[i][3]],
					curve: 0!(t[0]).size
				),
				doneAction: k,
				timeScale: sus,
				levelScale: 1/l.size
			)
		)
	}.dup(l.size))!2
	)*amp)}
).add;
)

//blips
(
SynthDef(\blips1, {arg out = 0, freq = 25, numharm = 10, atk = 0.01, rel = 1, amp = 0.1, pan = 0.5, beatsPercentage = 1.001, bpf = 440;
	var snd, env;
	env = Env.perc(atk, rel, amp).kr(doneAction: Done.freeSelf);
	snd = BPF.ar(LeakDC.ar(Mix(Blip.ar([freq, freq*beatsPercentage], numharm, env))), bpf);
	Out.ar(out, Pan2.ar(snd, pan));

//80's like synth
//By Bruno Ruviaro
//https://github.com/brunoruviaro/SynthDefs-for-Patterns/blob/master/blips.scd
//Edits by Zé Craum
}).play;
)

//variables for pad (chord progressions)
~prog1 = Pseq([[0, 4, 6],[0, 3, 5],[-1, 3, 5],[-1, 2, 4]], inf);
~prog2 = Pseq([[0, 4, 6],[0, 5, 8],[-1, 5, 7],[-1, 2, 5]], inf);
~prog3 = Pseq([[0, 3, 5],[0, 2, 5],[-1, 2, 4],[-1, 1, 1]], inf);
~degree_pad = Prand([~prog1, ~prog2, ~prog3], inf);
~degree_organ = Pseq([[-7, 0], [-7, 0], [-8, -1], [-8, -1], [-9, -2], [-9, -2], [-6, -1]], inf);
~dur_organ = Pseq([4, 4, 4, 4, 4, 4, 8], inf);

(
var a, b, c;
//musical patterns for pad:
//pad
a = Pbind(*[
	instrument: \pad,
	amp: Pexprand(-40, -25, inf).dbamp,
	octave: 4,
	dur: 4,
	legato: 1,
	ffreq: Pseq([1000, 500], inf),
	degree: ~degree_pad
]).play;

//organ
b = Pbind(*[
	instrument: \organ,
	amp: Pexprand(-50, -35, inf).dbamp,
	octave: 3,
	legato: 1,
	sus: ~dur_organ,
	dur: ~dur_organ,
	degree: ~degree_organ
]).play;

//blips for bleeding
c = Pbind(*[
	instrument: \blips1,
	out: 0,
	freq: Pwhite(50+(Pfunc{~freq}*25), 50.5+(Pfunc{~freq}*75), inf),
	numharm: 20,
	atk: 0.1,
	rel: 2,
	amp: Pexprand(0.05+(Pfunc{~amp}*0.5), 0.2+(Pfunc{~amp}*0.6), inf),
	pan: Pexprand(0.5-(Pfunc{~pan}*0.4), 0.5+(Pfunc{~pan}*04), inf),
	beatsPercentage: 1.005,
	dur: Pexprand(1.1-(Pfunc{~dur}*0.7), 0.9-(Pfunc{~dur}*0.89), inf),
	bpf: Pfunc{~bpf}
]).play;

//run all Pbinds together
Ppar([a, b, c]).play;

)

