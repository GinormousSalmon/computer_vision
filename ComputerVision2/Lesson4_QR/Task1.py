import RobotAPI as rapi
import cv2
import zbar
import numpy


def right():
    robot.move(120, -120, 410)
    robot.wait(430)


def left():
    robot.move(-120, 120, 410)
    robot.wait(430)


robot = rapi.RobotAPI()
scanner = zbar.Scanner()

robot.button()
robot.rgb(255, 0, 0)
while (robot.button() == 0):
    pass

robot.rgb(0, 0, 255)
while True:
    frame = robot.get_frame()
    results = scanner.scan(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

    for result in results:
        data = result.data.decode("utf-8")
        cv2.line(frame, result.position[0], result.position[1], (255, 0, 0), 4)
        cv2.line(frame, result.position[1], result.position[2], (255, 0, 0), 4)
        cv2.line(frame, result.position[2], result.position[3], (255, 0, 0), 4)
        cv2.line(frame, result.position[3], result.position[0], (255, 0, 0), 4)

        center = (result.position[0][0] + result.position[1][0] + result.position[2][0] + result.position[3][0]) / 4
        e = (320 - center)
        area = cv2.contourArea(numpy.array(result.position))
        print(data, result.position, area, e)
        if area > 17000:
            right()
        else:
            robot.move(220 - e, 220 + e, 10)
    #robot.set_frame(frame)
