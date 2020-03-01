import serial
import time
port = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=0.1)
while True:
    message = "SER70"
    port.write(str(message).encode("utf-8"))
    time.sleep(0.5)

    message = "SER90"
    port.write(str(message).encode("utf-8"))
    time.sleep(0.5)

    message = "SER110"
    port.write(str(message).encode("utf-8"))
    time.sleep(0.5)
