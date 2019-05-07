//musical patterns for pad:
    //pad
~prog1 = Pseq([[0, 4, 6],[0, 3, 5],[-1, 3, 5],[-1, 2, 4]], inf);
~prog2 = Pseq([[0, 4, 6],[0, 5, 8],[-1, 5, 7],[-1, 2, 5]], inf);
~prog3 = Pseq([[0, 3, 5],[0, 2, 5],[-1, 2, 4],[-1, 1, 1]], inf);



d =Pbind(*[
	instrument: \pad,
	amp: Pexprand(-40, -25, inf).dbamp,
	octave: 4,
	dur: 4,
	legato: 1,
	ffreq: Pseq([1000, 500], inf),
	degree: Prand([~prog1, ~prog2, ~prog3], inf)
]);

d.play;
e = Pbind(*[
	instrument: \organ,
	amp: Pexprand(-60, -35, inf).dbamp,
	octave: Pwhite(4, 5, inf),
	dur: Pexprand(0.5, 4, inf),
	legato: Pwhite(0.8, 1, inf),
	degree: Pwhite(-3, 4, inf)
]).trace.play;


(
~pad=Pbind(*[
	instrument: \pad,
	amp: -25.dbamp,
	octave: 4,
	dur: 4,
	legato: 1,
	ffreq: Pseq([1000, 500], inf),
	degree: Pseq([
		[0, 4],
		[0, 3, 5],
		[-1, 3, 5],
		[-1, 2, 4],
	], inf)
]).play;
)

(
Pfx(
	Pbind(*[
		scale: Scale.dorian,
		root: 5,
	]) <> Ppar([
		Pbind(*[
			instrument: \mypad,
			amp: -30.dbamp,
			octave: 3,
			dur: 5,
			legato: 1,
			ffreq: Pseq([1500, 1000], inf),
			degree: Pseq([
				[0, 4, 6],
				[0, 3, 5],
				[-1, 3, 5],
				[-1, 2, 4],
			], inf)
		]).play;,
		Pbind(*[
			instrument: \organ,
			amp: -35.dbamp,
			octave: 4,
			dur: 5,
			legato: 0.9,
			degree: Pseq([0, 0, -1, -1], inf)
		]),
		Pbind(*[
			instrument: \wave,
			amp: -35.dbamp,
			dur: 5
		]),
		Pbind(*[
			instrument: \freq_mod,
			amp: -20.dbamp,

		])
	])
).play;
)

