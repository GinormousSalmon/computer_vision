import RobotAPI as rapi
import cv2
import zbar
import numpy

robot = rapi.RobotAPI()
vcc_old = robot.vcc()
timer = robot.millis()
timerDist = robot.millis()
scanner = zbar.Scanner()


def vccTest():
    global vcc_old
    global timer
    if robot.millis() > timer + 200:
        timer = robot.millis()
        vcc = robot.vcc()
        if vcc - vcc_old > 0.9:
            vcc_old = vcc
            return 1
        else:
            if vcc - vcc_old < -0.9:
                vcc_old = vcc
                return -1
            else:
                vcc_old = vcc
                return 0


def parking():
    global timerDist
    if robot.dist() < 24:
        if robot.millis() > timerDist + 1500:
            robot.move(-150, -150, 250)
            robot.wait(400)
            timerDist = robot.millis()
    else:
        timerDist = robot.millis()
    if vccTest() == 1:
        return 1
    else:
        return 0


robot.start()
while parking() != 1:
    frame = robot.get_frame()
    results = scanner.scan(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    e = 0
    for result in results:
        data = result.data.decode("utf-8")
        cv2.line(frame, result.position[0], result.position[1], (255, 0, 0), 4)
        cv2.line(frame, result.position[1], result.position[2], (255, 0, 0), 4)
        cv2.line(frame, result.position[2], result.position[3], (255, 0, 0), 4)
        cv2.line(frame, result.position[3], result.position[0], (255, 0, 0), 4)

        center = (result.position[0][0] + result.position[1][0] + result.position[2][0] + result.position[3][0]) / 4
        e = (320 - center) * 4
        area = cv2.contourArea(numpy.array(result.position))
        print(data, result.position, area, e)
    robot.move(150 - e, 150 + e, 10)
