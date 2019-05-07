(
var window, slider1, slider2, slider3;

window = Window.new("Sonification of Bleeding Measurements-Algorithmic Music", Rect(50, 50, 915, 400), resizable: false);

slider1 = EZSlider(window,Rect(10, 10, 60, 180));
slider2 = Slider(window,Rect(100, 10, 40, 180));
slider3 = Slider(window,Rect(200, 10, 40, 180));

slider1.action_({slider1.value.postln;});
slider2.action_({slider2.value.postln;});
slider3.action_({slider3.value.postln;});


window.front;
)