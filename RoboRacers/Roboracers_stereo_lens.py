# import RoboRacers.RobotAPI as RobotAPI
import RobotAPI
import time
import cv2
import numpy
import math

robot = RobotAPI.RobotAPI(1)
# robot.set_camera(fps=30, width=640, height=480)
frame = robot.get_frame()
width = frame.shape[1]
height = frame.shape[0]
print(width, height)

low = numpy.array([0, 0, 0])
high = numpy.array([255, 255, 255])
ksize = 6

robot.manual_regim = 1
print("Start")
robot.ready()
# robot.move(45)
robot.servo(90)

while 1:
    if robot.manual() == 1:
        continue
    frame = robot.get_frame()
    # cv2.rectangle(frame, (170, 60), (width - 350, 80), (255, 0, 0), 2)
    # robot.set_frame(frame, 20)
    # continue

    # crop1 = frame[230:240, 0:320].copy()
    # crop2 = frame[230:240, 320:640].copy()
    crop1 = frame[70:80, 0:320].copy()
    crop2 = frame[70:80, 320:640].copy()

    median_blur1 = cv2.medianBlur(crop1, ksize - 1)
    median_blur2 = cv2.medianBlur(crop2, ksize - 1)
    grey1 = cv2.cvtColor(median_blur1, cv2.COLOR_BGR2GRAY)
    grey2 = cv2.cvtColor(median_blur2, cv2.COLOR_BGR2GRAY)
    canny1 = cv2.Canny(grey1, 100, 150)
    canny2 = cv2.Canny(grey2, 100, 150)
    # lines = cv2.HoughLines(canny, 1, numpy.pi / 180, 18, None, 0, 0)
    #
    # lines_convert = []
    # if lines is not None:
    #     # print(lines)
    #     for line in lines:
    #         rho = line[0][0]
    #         theta = line[0][1]
    #         angle = theta * 180 / numpy.pi
    #         if angle < 80 or angle > 100:
    #             # print(theta * 180 / numpy.pi)
    #             a = math.cos(theta)
    #             b = math.sin(theta)
    #             x0 = a * rho
    #             y0 = b * rho
    #             pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
    #             pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a)))
    #             cv2.line(crop, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)
    #
    #     crop_line = crop[10:11, 0:crop.shape[1]].copy()
    x1 = 0
    for i in range(320):
        # print(list(crop_line1[0][i]), list([0, 0, 255]))
        if canny1[5][i] > 0:
            x1 = i
            break

    x2 = 0
    for i in range(320):
        # print(list(crop_line1[0][i]), list([0, 0, 255]))
        if canny2[5][319 - i] > 0:
            x2 = i
            break

    # pt1 = (int(coordinate), 0)
    # pt2 = (int(coordinate), 15)
    # cv2.line(crop, pt1, pt2, (255, 0, 0), 3, cv2.LINE_AA)
    # print(coordinate, crop_line.shape[1])
    x = x1 - x2
    e = 60 - x
    if abs(e) < 8:
        # robot.move(45)
        robot.move(50)
    else:
        # robot.move(35)
        robot.move(35)
    if abs(e) > 200:
        robot.move(35)
        time.sleep(2)
    u = e * 0.1 + 90
    print(x1, x2, x, u, e)
    robot.servo(u)
    robot.set_frame(frame, 20)

# 150
# center 33
# max 62
# min 13
