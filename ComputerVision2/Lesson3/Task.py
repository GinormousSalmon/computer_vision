import RobotAPI as rapi
import cv2

robot = rapi.RobotAPI()

robot.button()
robot.rgb(255, 0, 0)
while not robot.button():
    pass
robot.rgb(0, 255, 0)
ser = 0
while True:
    frame = robot.get_frame()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 400, 200, 100, 30, 60)
    minimum = 1000000
    i1 = 0
    i2 = 0
    i3 = 0
    if circles is not None:
        for i in circles[0, :]:
            if i[2] < minimum:
                i1 = i[0]
                i2 = i[1]
                i3 = i[2]
                minimum = i[2]
        cv2.circle(frame, (i1, i2), i3, (255, 0, 0), 2)
    robot.set_frame(frame)
    e = 320 - i1
    ser+=int(e*(-0.02))
    robot.serv(ser)
