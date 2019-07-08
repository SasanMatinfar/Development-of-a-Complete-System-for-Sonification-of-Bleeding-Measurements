(

//First: Server Configuration
s = Server.local;
s.options.outDevice_(
	"Built-in Output"
	//or any other desired output device available ...
);
s.options.numOutputBusChannels_(2);
s.options.sampleRate_(44100);
s.options.memSize_(2.pow(32));
s.newBusAllocators;
ServerBoot.removeAll;
ServerTree.removeAll;
ServerQuit.removeAll;

//Second: Global Variables Initialization
~out = 0;
~path = PathName(thisProcess.nowExecutingPath).parentPath++"samples/";

//Third: Musical Function Definitions
~mkBusses = {
	~bus = Dictionary.new;
	~bus.add(\reverb -> Bus.audio(s,2));
};
//Fourth: ServerBoot/Quit Functions Registrations
ServerBoot.add(~createBuffs);
ServerBoot.add(~mkBusses);
ServerQuit.add(~cleaningUp);

//Fifth: Server Boot
s.waitForBoot({

	s.sync;

	//Sixth_one: SynthDefs
	SynthDef(\pad_one, {
		arg freq=500, detune=0.2,
		co_min = 1000, co_max = 2000, cohz_min = 0.1, cohz_max = 0.3,
		rq_min = 0.1, rq_max = 0.2, rqhz_min = 0.1, rqhz_max = 0.1,
		atk=2, sus=0, rel=3, crv1 = 1, crv2 = -1,
		pan=0, amp=1, out=0, lsfreq = 200, lsdb = 0;

		var signal, envelop;

		signal = Saw.ar(freq * {LFNoise2.kr(0.5, detune).midiratio}!2);
		//signal = SinOsc.ar(freq * {LFNoise2.kr(0.5, detune).midiratio}!2);
		//signal = Pulse.ar(freq * {LFNoise2.kr(0.5, detune).midiratio}!2);

		signal = BPF.ar(signal,
			LFNoise2.kr(LFNoise2.kr(4).exprange(cohz_min,cohz_max)).exprange(co_min, co_max)!2,
			LFNoise2.kr(LFNoise2.kr(4).exprange(rqhz_min, rqhz_max)).exprange(rq_min, rq_max)!2);

		envelop = EnvGen.kr(Env([0,1,1,0],[atk,sus,rel],[crv1, 0, crv2]),doneAction:2);

		signal = BLowShelf.ar(signal, lsfreq, 0.5, lsdb);
		signal = Balance2.ar(signal[0], signal[1], pan);
		Out.ar(out, (signal * envelop * amp));
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

	SynthDef().add;

	//more SynthDefs here ...

	s.sync;

	//Sixth_two: Remaining Functions Registration
	ServerTree.add(~mkNodes);
	ServerTree.add(~mkEvents);
	s.freeAll;
	s.sync;

	"Ready to Run!".postln;
});
)


///Temporary Section for Pbinds:

//1. pad one

(
~chords = Pbind(
	\instrument, \pad_one,
	\dur, Pwhite(4.5, 7, inf),
	\midinote, Pxrand([
		[23,35,54,63,64],
		[45,52,54,59,61,64],
		[28,40,47,56,59,63],
		[42,52,57,61,63]
	], inf), //here need to be ellaborate with interesting chord progressions
	\detune, Pexprand(0.05, 0.2, inf),
	\cfmin, 100,
	\cfmax, 1500,
	\rqmin, Pexprand(0.01, 0.15, inf),
	\atk, Pwhite(2.0, 2.5, inf),
	\rel, Pwhite(6.5, 10.0, inf),
	\ldb, 6,
	\amp, 0.2,
	\out, 0,
).play;
)



~chords = Pbind(
			\instrument, \bpfsaw,
			\dur, Pwhite(4.5,7.0),
			\midinote, Pxrand([
				[23,35,54,63,64],
				[45,52,54,59,61,64],
				[28,40,47,56,59,63],
				[42,52,57,61,63]
			], inf),
			\detune, Pexprand(0.05,0.2),
			\cfmin, 100,
			\cfmax, 1500,
			\rqmin, Pexprand(0.01,0.15),
			\atk, Pwhite(2.0,2.5),
			\rel, Pwhite(6.5,10.0),
			\ldb, 6,
			\amp, 0.2,
			\group, ~mainGrp,
			\out, ~bus[\reverb],
		).play;

~drone = Pbind(
			\instrument, \bpfsaw,
			\dur, 1,
			\freq, 26.midicps,
			\detune, Pwhite(0.03,0.2),
			\rqmin, 0.08,
			\rqmax, 0.12,
			\cfmin, 50,
			\cfmax, 400,
			\atk, 2,
			\sus, 0.1,
			\rel, 2,
			\amp, 0.5,
			\group, ~mainGrp,
			\out, ~bus[\reverb],
		).play;

(
~marimba = Pbind(
	\instrument, \pad_one,
	\dur, Pexprand(0.1,1,inf),
	\freq, Pexprand(0.25,9,inf),
	\detune, 0,
	\rqmin, 0.005,
	\rqmax, 0.008,
	\cfmin, 150,
	\cfmax, 1500,
	\amp, 1,
	\out, 0,
).play
)




(
~marimba = Pbind(
	\instrument, \bpfsaw,
	\dur, Pexprand(0.1, 1, inf),
	\freq, Pexprand(0.25, 9, inf),
	\detune, 0,
	\rqmin, 0.005,
	\rqmax, 0.008,
	\cfmin, Prand((Scale.major.degrees+64).midicps, inf) * Prand([0.5,1,2,4],inf),
	\cfmax, Pkey(\cfmin),
	\amp, 1,
	\out, 0,
).play
)