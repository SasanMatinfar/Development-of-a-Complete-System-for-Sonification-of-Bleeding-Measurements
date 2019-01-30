import serial
import threading

running = threading.Event()
running.set()

def thread_read(ser, callback=None):
    buf = b''
    while running.is_set():
        buf = read_data(ser, buf, callback)

def msg_parsed(msg_parts):
    # Do something with the parsed data
    print(msg_parsed)

ser = serial.Serial("COM3", 9600)
th = threading.Thread(target=thread_read, args=(ser, msg_parsed))
th.start()

def read_data(ser, buf=b'', callback=None):
    if callback is None:
        callback = print

    # Read enough data for a message
    buf += ser.read(ser.inwaiting()) # If you are using threading +10 or something so the thread has to wait for more data, this makes the thread sleep and allows the main thread to run.
    while b"[" not in buf or b"]" not in buf:
        buf += ser.read(ser.inwaiting())

    # There may be multiple messages received
    while b"[" in buf and b']' in buf:
        # Find the message
        start = buf.find(b'[')
        buf = buf[start+1:]
        end = buf.find(b']')
        msg_parts = buf[:end].split(",") # buf now has b"Hello, 1234"
        buf = buf[end+1:]

        # Check the checksum to make sure the data is valid
        if msg_parts[-1] == b"1234": # There are many different ways to make a good checksum
            callback(msg_parts[:-1])

   return buf

# Do other stuff while the thread is running in the background
start = time.clock()
duration = 5 # Run for 5 seconds
while running.is_set():
    time.sleep(1) # Do other processing instead of sleep
    if time.clock() - start > duration:
        running.clear()

th.join() # Wait for the thread to finish up and exit
ser.close() # Close the serial port
