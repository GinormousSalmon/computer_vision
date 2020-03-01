import RobotAPI as rapi
import cv2
import numpy

robot = rapi.RobotAPI()

robot.start()


def findStop(frame):
    result = []
    low = numpy.array([120, 50, 50])
    high = numpy.array([250, 170, 180])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if contours is not None:
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if cv2.contourArea(contour) > 6000 and abs(w - h) < 20:
                result.append([x, y, w, h])
    return result
    # robot.set_frame(numpy.hstack([cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), frame]))


robot.serv(-10)
while True:
    robot.move(170, 180, 6)
    frame = robot.get_frame()
    zn = findStop(frame)
    if zn is not None:
        for z in zn:
            cv2.rectangle(frame, (z[0], z[1]), (z[0] + z[2], z[1] + z[3]), (255, 0, 0), 2)
            if z[2] * z[3] > 20000:
                print("detected")
                robot.wait(2000)
                robot.move(60, 60, 800)
                robot.wait(800)
    robot.set_frame(frame)
