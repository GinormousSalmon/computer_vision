import serial
import RobotAPI
import time
import datetime

robot = RobotAPI.RobotAPI()
robot.ready()

print("Start")
t = time.time()
c = 0
robot.manual_regim = 1
angle = 0
while 1:
    if time.time() - t > 1:
        t = time.time()
        print(datetime.datetime.now())
        c += 1
    if robot.manual() == 1:
        continue
    frame = robot.get_frame()
    robot.set_frame(frame, 20)
