import cv2
import RobotAPI as rapi
import numpy

robot = rapi.RobotAPI()

low = numpy.array((0, 0, 0))
high = numpy.array((255, 70, 60))

frame = robot.get_frame()
x = frame.shape[1]
y = frame.shape[0]

robot.serv(5)
while True:
    if robot.manual(1) == 1:
        continue
    frame = robot.get_frame()
    crop = frame[y - 100:y - 0, 0:x].copy()
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    xNow = 0
    if len(contours) > 0:
        for contour in contours:
            pass
            x, y, w, h = cv2.boundingRect(contour)
            # xNow = x + w/2
            # cv2.rectangle(crop, (x, y), (x + w, y + h), (255, 0, 0), 1)
        # xNow /= len(contours)
    # U = frame.shape[1]/2 - xNow
    # U *= 0.7
    # robot.move(70 - U, 70 + U, 5)
    print(xNow)
    robot.set_frame(crop)
