(
//Server Configuration
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

//Global Variables Initialization
~init = {
	~out = 0;
	~delta = 0; ~volume = 0;
	~deltaMin = 0; ~deltaMax = 0;
	~volumeMin = 0; ~volumeMax = 0;
	("global variables are initialized").postln;
};

//Piece Related Functions Definition
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
				\predelay, 0.4,
				\revtime, 1.8,
				\lpf, 4500,
				\mix, 0.5,
				\in, ~bus[\reverb],
				\out, ~out,
			], ~reverbGroup
		);
	});
};

~makeEvents = {

	OSCdef.new(\init, {
		arg msg;
		~deltaMin = msg[1];
		~deltaMax = msg[2];
		~volumeMin = msg[5];
		~volumeMax = msg[6];
		~init;
	},
	'/root/init'
	);

	OSCdef.new(\play, {
		arg msg;
		if (msg[1] == 1,
		{e[\pad_sine_lf].value;"\pad_sine_lf".postln;},
		{e[\event_stop].value;s.freeAll;~init;
				"\stop".postln;})
	},
	'/root/play'
	);

	OSCdef.new(\blood_data, {
		arg msg;
		~volume = msg[2].linlin(~volumeMin, ~volumeMax, 0, 1).postln;
		~delta = msg[3].linlin(~deltaMin, ~deltaMax, 0, 1).postln;

		~reverbSynth.set(\revtime, (~volume.linlin(0,1,1.8,0.5)));
		~reverbSynth.set(\mix, (~volume.linlin(0,1,0.5,0.1)));
		~reverbSynth.set(\predelay, (~volume.linlin(0,1,0.4,0.1)));
		~reverbSynth.set(\amp, (~volume.linexp(0,1,0.8,0.2)));
		~reverbSynth.set(\lpf, (~delta.linlin(0,1,1500,5000)));
	},
	'/root/msg'
	);

	e = Dictionary.new;

	e.add(\pad_sine_lf -> {

		~chords = Pbind(
			\instrument, \bpfsine,
			\dur, Pwhite(4.5-(Pfunc{~delta.linlin(0,1,0,4)}),5.5-(Pfunc{~delta.linlin(0,1,0,4)})),
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

		~marimba = Pbind(
			\instrument, \bpfsaw,
			\dur, Pwhite(Pfunc{~delta.linlin(0,1,0.99,0.05)},
				Pfunc{~delta.linlin(0,1,1,0.1)}).trace,
			\freq, Prand([1/2,2/3,1]*(~delta.explin(0,1,1,4)),inf),
			\detune, Pfunc({~delta.linlin(0,1,0,2)}),
			\rqmin, Pfunc{~volume.linlin(0,1,0.005,0.09)},
			\rqmax, Pfunc{~volume.linlin(0,1,0.008,0.2)},
			\cfmin, Prand((Scale.major.degrees+64).midicps,inf) *
			(Prand(([1,2,4]), inf) * round((Pfunc{~delta.linlin(0,1,1,5)}))),
			\cfmax, Pkey(\cfmin) * Pwhite(1.008,1.025),
			\atk, Pfunc{~volume.linlin(0,1,3,1.5)},
			\sus, Pfunc{~volume.linlin(0,1,1,0.5)},
			\rel, Pfunc{~volume.linlin(0,1,5,2.5)},
			\amp, 0.9,
			\pan, Pwhite(Pfunc{~delta.linlin(0,1,0,-1)},Pfunc{~delta}),
			\group, ~mainGroup,
			\out, ~bus[\reverb],
		).play;
	});
	e.add(\event_stop -> {
		~chords.stop;
		~marimba.stop;
	});
};

//ServerBoot/Quit Function Reservation
ServerBoot.add(~makeBusses);
ServerQuit.add(~cleanup);

//Boot Server
s.waitForBoot({

	s.sync;

	//(a) Synthsizer Definitions
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

	//(b) Remaining Functions Registration
	ServerTree.add(~makeNodes);
	ServerTree.add(~makeEvents);
	s.freeAll;

	s.sync;

	"Now You Can Run!".postln;

	//(c) GUI
	Window.closeAll;
	w = Window("Sonification of Bleeding level",
		Rect(850, 400, 600,200)).front.alwaysOnTop_(true);

	~delta = 0;
	~volume = 0;

	~sliderDelta = Slider(w, Rect(30, 30, 250, 40)).background_(Color.rand).action_({
		arg obj;
		~delta = obj.value;
		~reverbSynth.set(\lpf, (~delta.linlin(0,1,1500,5000)));

	});
	~sliderVolume = Slider(w, Rect(30, 80, 250, 40)).background_(Color.rand).action_({
		arg obj;
		~volume = obj.value;
		~reverbSynth.set(\revtime, (~volume.linlin(0,1,1.8,0.5)));
		~reverbSynth.set(\mix, (~volume.linlin(0,1,0.5,0.1)));
		~reverbSynth.set(\predelay, (~volume.linlin(0,1,0.4,0.1)));
		~reverbSynth.set(\amp, (~volume.linexp(0,1,0.8,0.2)));
	});

	StaticText(w, Rect(300, 35, 300, 30))
	.string_("spontaneous blood values, 0-10 ml/s");
	StaticText(w, Rect(300, 85, 300, 30))
	.string_("total amount of bleeding, 0-2500 ml");
	Button(w, Rect(350, 120, 60, 60)).states_([["Play", Color.black,
		Color.gray]]).action_({e[\pad_sine_lf].value;~init.value;"\pad_sine_lf".postln;});
	Button(w, Rect(430, 120, 60, 60)).states_([["Stop", Color.black,
		Color.gray]]).action_({e[\event_stop].value;
		s.freeAll;~init.value;"\stop".postln;});
});
)

s.record;
s.stopRecording;

