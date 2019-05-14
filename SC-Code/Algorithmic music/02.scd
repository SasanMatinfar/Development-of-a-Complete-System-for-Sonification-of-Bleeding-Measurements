(
//First: Server Configuration
s = Server.local;
s.options.outDevice_(
	"Built-in Output"
);
s.options.numOutputBusChannels_(2);
s.options.sampleRate_(44100);
s.options.memSize_(2.pow(20));
s.newBusAllocators;
ServerBoot.removeAll;
ServerTree.removeAll;
ServerQuit.removeAll;

//Second: Global Variables Initialization
~out = 0;

~delta = 0;
~dDelta = 0;
~volume = 0;

~deltaMin = 0;
~deltaMax = 0;
~dDeltaMin = 0;
~dDeltaMax = 0;
~volumeMin = 0;
~volumeMax = 0;

//Third: Piece Related Functions Definition
~makeBusses = {
	~bus = Dictionary.new;
	~bus.add(\reverb -> Bus.audio(s,2));
};

~cleanup = {
	s.newBusAllocators;
	ServerBoot.removeAll;
	ServerTree.removeAll;
	ServerQuit.removeAll;
};

~makeNodes = {
	s.bind({
		~mainGroup = Group.new;
		~reverbGroup = Group.after(~mainGroup);
		~reverbSynth = Synth.new(
			\reverb,
			[
				\amp, 1,
				\predelay, 0.1,
				\revtime, 1.8,
				\lpf, 4500,
				\mix, 0.5,
				\in, ~bus[\reverb],
				\out, ~out,
			],
			~reverbGroup
		);
	});
};

~makeEvents = {

	OSCdef.new(\init, {
		arg msg;
		~deltaMin = msg[1];
		~deltaMax = msg[2];
		~dDeltaMin = msg[3];
		~dDeltaMax = msg[4];
		~volumeMin = msg[5];
		~volumeMax = msg[6];
	},
	'/root/init'
	);

	OSCdef.new(\play, {
		arg msg;
		if (msg[1] == 1)
		{e[\pad_sine_lf].value;"\pad_sine_lf".postln;}
		{e[\event_stop].value;s.freeAll;
			~delta = 0;
			~dDelta = 0;
			~volume = 0;
			~deltaMin = 0;
			~deltaMax = 0;
			~dDeltaMin = 0;
			~dDeltaMax = 0;
			~volumeMin = 0;
			~volumeMax = 0;
			"\stop".postln;}
	},
	'/root/play'
	);

	OSCdef.new(\blood, {
		arg msg;
		~volume = msg[2].linlin(~volumeMin, ~volumeMax, 0, 1);
		~delta = msg[3].linlin(~deltaMin, ~deltaMax, 0, 1);
		~dDelta = msg[4].linlin(~deltaMax.neg, ~deltaMax, -1, 1);
	},
	'/root/msg'
	);

	e = Dictionary.new;

	e.add(\pad_sine_lf -> {

		~chords = Pbind(
			\instrument, \bpfsine,
			\dur, Pwhite(4.5-(Pfunc{~delta}*4),5.5-(Pfunc{~delta}*4)),
			\midinote, Pxrand([
				[23,35,54,63,64],
				[45,52,54,59,61,64],
				[28,40,47,56,59,63],
				[42,52,57,61,63]
			], inf),
			\detune, Pexprand(0.05,0.2),
			\cfmin, 500,
			\cfmax, 1000,
			\rqmin, Pexprand(0.01,0.02),
			\rqmax, Pexprand(0.2,0.3),
			\atk, Pwhite(2.0,2.5),
			\rel, Pwhite(6.5,10.0),
			\ldb, 6,
			\amp, 0.3,
			\group, ~mainGroup,
			\out, ~bus[\reverb],
		).play;

		~kalimba = Pbind(
			\instrument, \kalimba,
			\root, 4,
			\octave, 4,
			\dur, Pexprand(0.05,0.2),
			\stretch, 4,
			\amp, 0.5*(2**Pgauss(0, 0.1)),
			\degree, Prand([Rest(1),1,5,8], inf),
			\mix, ~volume
		).play;

		~marimba = Pbind(
			\instrument, \bpfsaw,
			\dur, Pwhite(2.01-(Pfunc{~delta}*2), 4.01-(Pfunc{~delta}*3)),
			\freq, Prand([1/2,2/3,1,4/3,2,5/3,5/2,3,4],inf),
			\detune, Pfunc({~delta.linlin(0,1,0,2)}),
			\rqmin, 0.005,
			\rqmax, 0.008,
			\cfmin, Prand((Scale.major.degrees+64).midicps,inf) * (Prand(([0.5,1,2]), inf) * round((Pfunc{~delta}*4)+1)),
			\cfmax, Pkey(\cfmin) * Pwhite(1.008,1.025),
			\atk, 3,
			\sus, 1,
			\rel, 5,
			\amp, 1,
			\pan, Pwhite(Pfunc{~delta}*(-1),Pfunc{~delta}),
			\group, ~mainGroup,
			\out, ~bus[\reverb],
		).play;
	});
	e.add(\event_stop -> {
		~chords.stop;
		~marimba.stop;
		~kalimba.stop;
	});
	e.add(\oneshot -> {
		12.do{
			Synth(
				\bpfsaw,
				[
					\atk, exprand(0.5,1.5),
					\rel, exprand(2.0,8.0),
					\c1, exprand(4,10.0),
					\c2, exprand(2.0,5).neg,
					\freq, exprand(8,60),
					\detune, rrand(0.1,4),
					\cfmin, 30,
					\cfmax, 400,
					\rqmin, 0.02,
					\rqmax, 0.08,
					\amp, exprand(0.5,0.9),
					\pan, rrand(-0.5,0.5),
					\out, ~bus[\reverb],
				],
				~mainGroup
			);
		}
	})
};

//Fourth: ServerBoot/Quit Function Reservation
ServerBoot.add(~makeBusses);
ServerQuit.add(~cleanup);

//Fifth: Boot Server
s.waitForBoot({

	s.sync;

	//Sixth (a): Synthsizer Definitions
	SynthDef(\bpfsaw, {
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

	SynthDef(\bpfsine, {
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

	SynthDef(\gliss, {
		arg f1, f2, f3, detune = 0.5,
		atk = 2, rel = 2, cfmin = 500, cfmax = 2000, rqmin = 0.1, rqmax = 0.3, cfhzmin = 0.01,
		cfhzmax = 0.02, amp = 1, pan = 0, lsf = 200, ldb = 0;
		var sig, env, envFreq;

		env = EnvGen.kr(Env([0,1,1,0],[0.2,3.3,0.5],[3,-3]), doneAction:2);
		envFreq = EnvGen.kr(Env([f1, f2, f2, f3],[1.5,1,1.5],[3,0,-3]), doneAction:2);

		sig = SinOsc.ar(envFreq * {LFNoise1.kr(2,detune).midiratio}!2);
		sig = BPF.ar(sig,
			{LFNoise1.kr(
				LFNoise1.kr(4).exprange(cfhzmin,cfhzmax)
			).exprange(cfmin,cfmax)}!2,
			{LFNoise1.kr(0.1).exprange(rqmin,rqmax)}!2
		);
		sig = BLowShelf.ar(sig, lsf, 0.5, ldb);
		sig = Balance2.ar(sig[0], sig[1], pan);

		sig = sig * amp;
		Out.ar(0, sig);
	}).add;

	SynthDef(\kalimba, {
		|out = 0, freq = 440, amp = 0.1, mix = 0.1|
		var bTone, click;

		// Basic tone is a SinOsc
		bTone = SinOsc.ar(freq) * EnvGen.ar(Env.perc(0.03, Rand(3.0, 4.0), 1, -7), doneAction: 2);
		bTone = BPF.ar(bTone, 500, 0.3);

		// The "clicking" sounds are modeled with a bank of resonators excited by enveloped white noise
		click = DynKlank.ar(`[
			// the resonant frequencies are randomized a little to add variation
			// there are two high resonant freqs and one quiet "bass" freq to give it some depth
			[250*ExpRand(0.75, 1.05), 1250*ExpRand(0.8, 1.01), 3500*ExpRand(0.65, 1.2)],
			[-1, -10, -20].dbamp,
			[0.8, 0.07, 0.08]
		], BPF.ar(PinkNoise.ar, 6500, 0.1) * EnvGen.ar(Env.perc(0.001, 0.01))) * 0.5;
		bTone = (bTone*mix) + (click*(1-mix));
		bTone = Mix(bTone);
		Out.ar(out, Pan2.ar(bTone, 0, amp));
	}).add;

	SynthDef(\reverb, {
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

	s.sync;

	//Sixth (b): Remaining Functions Registration
	ServerTree.add(~makeNodes);
	ServerTree.add(~makeEvents);
	s.freeAll;

	s.sync;

	"Now You Can Run!".postln;

	Window.closeAll;
	w = Window("Sonification of Bleeding level", Rect(850, 400, 600, 200)).front.alwaysOnTop_(true);
	~delta = 0;
	~volume = 0;
	~sliderDelta = Slider(w, Rect(30, 30, 250, 40)).background_(Color.rand).action_({
		arg obj;
		~delta = obj.value;
		~reverbSynth.set(\predelay,
			(~delta.linlin(0,1,0.1,0.4)));
	});
	~sliderVolume = Slider(w, Rect(30, 80, 250, 40)).background_(Color.rand).action_({
		arg obj;
		~volume = obj.value;

	});

	StaticText(w, Rect(300, 35, 300, 30))
	.string_("spontaneous blood values, 0-10 ml/s");
	StaticText(w, Rect(300, 85, 300, 30))
	.string_("total value of bleeding, 0-2500 ml");
	Button(w, Rect(350, 120, 60, 60)).states_([["Play", Color.black,
		Color.gray]]).action_({e[\pad_sine_lf].value;"\pad_sine_lf".postln;});
	Button(w, Rect(430, 120, 60, 60)).states_([["Stop", Color.black,
		Color.gray]]).action_({e[\event_stop].value;
		s.freeAll;~delta=0;"\stop".postln;});
});
)




e[\event_stop].value;"\event_stop".postln;
e[\pad_saw].value;"\pad_saw".postln;

e[\pad_saw_lf].value;"\pad_saw_lf".postln;
e[\oneshot].value;"\oneshot".postln;



