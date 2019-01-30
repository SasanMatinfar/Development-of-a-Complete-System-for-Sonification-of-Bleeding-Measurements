# import packages
import serial
import time

# initialization
timestr = time.strftime("%Y%m%d-%H%M%S")
output_file = open("C:/Users/MITI-Sono/Google Drive/Master Maschinenwesen/Masterarbeit/Python/" + timestr + "_data.csv", "w+");
sobj = serial.Serial('COM3', 9600)
running_pre = 0;

# run data acquisition loop
while True:
 
    # read serial message until \n 
    line = sobj.readline();
    # convert to string
    line = line.decode("utf-8")

    # read identifier
    running = float(line[0]);
    print(line);

    # start writing data to file when switch is activated
    if running == 1:
        output_file.write(line);

    # stop writing data when switch is deactivated 
    elif (running_pre - running) == 1:
        output_file.close();
        break

    # write variable for next iteration
    running_pre = running;
	
	
	
