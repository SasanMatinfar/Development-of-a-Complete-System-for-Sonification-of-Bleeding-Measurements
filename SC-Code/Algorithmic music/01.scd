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

//Fourth: ServerBoot/Quit Functions Registrations
ServerBoot.add(~createBuffs);
ServerBoot.add(~mkBusses);
ServerQuit.add(~cleaningUp);

//Fifth: Server Boot
s.waitForBoot({

	s.sync;

	//Sixth_one: SynthDefs
	SynthDef(

	).add;

	SynthDef().add;

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