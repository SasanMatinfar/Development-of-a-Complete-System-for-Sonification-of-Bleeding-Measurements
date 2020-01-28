from time import sleep
import matlab.engine

eng = matlab.engine.start_matlab()
start = 150.0
i = 0

while True:
    i += 1
    print("loop iteration: " + str(i))
    if i%2 == 1:
        stop = start + 500.0
        eng.plot_anim(start, stop)
        print("start: " + str(start))
        start = start + 500.0
        print("stop: " + str(start))
        sleep(1)
    else:
        stop = start - 500.0
        eng.plot_anim(start, stop)
        print("start: " + str(start))
        start = start - 500.0
        print("stop: " + str(start))
        sleep(1)
