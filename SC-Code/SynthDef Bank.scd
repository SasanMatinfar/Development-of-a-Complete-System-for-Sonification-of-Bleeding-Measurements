//This file includes different SynthDefs for algorithmic music

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
}).play;
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


//Wave, subtractive synthesis
(
SynthDef(\wave, {
	arg freq = 500, amp = 0.3;
	var sig, env;

	env = EnvGen.ar(Env.perc(0.5, 2, 0.5, -5), 1, amp, timeScale: 1.5, doneAction: 2);
	sig = LPF.ar(WhiteNoise.ar(1), freq);

	sig = sig * env;
	sig = FreeVerb.ar(sig, mix: 0.6, room: 0.3, damp: 1, mul: 1.0, add: 0.0);

	Out.ar(0, Balance2.ar(sig, sig));
}
).play;
)

//Frequency modulation synthesis

(
SynthDef(\freq_mod, {
	arg freqRatio, levelScale;
	var carrFreq, carrFreqEnv, carrFreqCtl, modFreq, modIndex, modIndexEnv, modIndexCtl, carrier, modulator, amp, ampEnv, ampCtl;

	//preset
	carrFreqEnv = Env.new([ 905, 905, 905, 905, 905, 905, 905, 905 ],[ 0.294, 0.315, 0.294, 0.294, 0.294, 0.315, 0.294 ]);
	modIndexEnv = Env.new([ 3.7, 3.5, 3.2, 3.1, 2.8, 2.4, 2, 0 ],[ 0.21, 0.252, 0.252, 0.294, 0.231, 0.546, 0.315 ]);
	ampEnv = Env.new([ 0, 1, 0.58, 0.31, 0.18, 0.09, 0.05, 0 ],[ 0.042, 0.084, 0.231, 0.315, 0.462, 0.504, 0.462]);
	freqRatio = 5/6.4;

	carrFreqCtl = carrFreqEnv.asArray;
	carrFreq = EnvGen.kr(carrFreqCtl);

	modIndexCtl = modIndexEnv.asArray;
	modIndex = EnvGen.kr(modIndexCtl);

	ampCtl = ampEnv.asArray;
	amp = EnvGen.kr(ampCtl, doneAction: 2, levelScale: 0.05);

	modFreq = carrFreq * freqRatio.reciprocal;

	modulator = SinOsc.ar(freq: modFreq, mul: modIndex * modFreq);
	carrier = SinOsc.ar(freq: carrFreq + modulator, mul: amp);

	Out.ar(0, [carrier, carrier]);

}).play;
)

//Kick

(
SynthDef(\kick1, {
    var snd;
    snd = DC.ar(0);
    snd = snd + (SinOsc.ar(XLine.ar(800, 400, 0.01)) * Env.perc(0.0005, 0.01).ar);
    snd = snd + (BPF.ar(Hasher.ar(Sweep.ar), XLine.ar(800, 100, 0.01), 0.6) * Env.perc(0.001, 0.02).delay(0.001).ar);
    snd = snd + (SinOsc.ar(XLine.ar(172, 50, 0.01)) * Env.perc(0.0001, 0.3, 1, \lin).delay(0.005).ar(2));
    snd = snd.tanh;
    Out.ar(\out.kr(0), Pan2.ar(snd, \pan.kr(0), \amp.kr(0.1)));
}).play;
)

(
SynthDef(\kick2, {
    var snd;
    snd = DC.ar(0);
    snd = snd + (HPF.ar(Hasher.ar(Sweep.ar), 1320) * Env.perc(0.003, 0.03).ar * 0.5);
    snd = snd + (SinOsc.ar(XLine.ar(750, 161, 0.02)) * Env.perc(0.0005, 0.02).ar);
    snd = snd + (SinOsc.ar(XLine.ar(167, 52, 0.04)) * Env.perc(0.0005, 0.3).ar(2));
    snd = snd.tanh;
    Out.ar(\out.kr(0), Pan2.ar(snd, \pan.kr(0), \amp.kr(0.1)));
}).play;
)

(
SynthDef(\kick3, {
    var snd;
    snd = DC.ar(0);
    snd = snd + (SinOsc.ar(XLine.ar(1500, 800, 0.01)) * Env.perc(0.0005, 0.01, curve: \lin).ar);
    snd = snd + (BPF.ar(Impulse.ar(0) * SampleRate.ir / 48000, 6100, 1.0) * 3.dbamp);
    snd = snd + (BPF.ar(Hasher.ar(Sweep.ar), 300, 0.9) * Env.perc(0.001, 0.02).ar);
    snd = snd + (SinOsc.ar(XLine.ar(472, 60, 0.045)) * Env.perc(0.0001, 0.3, curve: \lin).delay(0.005).ar(2));
    snd = snd.tanh;
    Out.ar(\out.kr(0), Pan2.ar(snd, \pan.kr(0), \amp.kr(0.1)));
}).play;
)

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
