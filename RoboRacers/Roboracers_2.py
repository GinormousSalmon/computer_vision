# import RoboRacers.RobotAPI as RobotAPI
import RobotAPI
import time
import cv2
import numpy
import math

robot = RobotAPI.RobotAPI()
robot.set_camera(fps=30, width=640, height=480)
frame = robot.get_frame()
width = frame.shape[1]
height = frame.shape[0]

low = numpy.array([0, 0, 0])
high = numpy.array([255, 255, 255])
ksize = 6
rect = [170, 290]

robot.manual_regim = 1
print("Start")
robot.ready()
robot.move(0)
robot.servo(90)
e_old = 0
while 1:
    if robot.manual() == 1:
        continue
    frame = robot.get_frame()
    # cv2.rectangle(frame, (110, height - 250), (550, height - 230), (255, 0, 0), 2)
    # robot.set_frame(frame, 20)
    # continue

    crop = frame[50:100, int(rect[0]):int(rect[1])].copy()
    median_blur = cv2.medianBlur(crop, ksize - 1)
    grey = cv2.cvtColor(median_blur, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(grey, 70, 120)
    lines = cv2.HoughLines(canny, 1, numpy.pi / 180, 18, None, 0, 0)

    lines_convert = []
    if lines is not None:
        # print(lines)
        for line in lines:
            rho = line[0][0]
            theta = line[0][1]
            angle = theta * 180 / numpy.pi
            if angle < 80 or angle > 100:
                # print(theta * 180 / numpy.pi)
                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a * rho
                y0 = b * rho
                pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
                pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a)))
                cv2.line(crop, pt1, pt2, (0, 0, 255), 3, cv2.LINE_AA)

        crop_line = crop[10:11, 0:crop.shape[1]].copy()

        for i in range(crop_line.shape[1]):
            # print(list(crop_line1[0][i]), list([0, 0, 255]))
            if list(crop_line[0][i]) == list([0, 0, 255]):
                lines_convert.append(i)

        lines_convert.sort()

        x = 0
        while x < len(lines_convert) - 1:
            if abs(lines_convert[x] - lines_convert[x + 1]) < 20:
                lines_convert.remove(lines_convert[x + 1])
            else:
                x += 1

        coordinate_rel = 0
        if len(lines_convert) > 0:
            for l in lines_convert:
                pt1 = (l, 0)
                pt2 = (l, 15)
                cv2.line(crop, pt1, pt2, (0, 255, 0), 3, cv2.LINE_AA)
                coordinate_rel += l
            coordinate_rel /= len(lines_convert)

        pt1 = (int(coordinate_rel), 0)
        pt2 = (int(coordinate_rel), 15)
        cv2.line(crop, pt1, pt2, (255, 0, 0), 3, cv2.LINE_AA)
        # print(coordinate, crop_line.shape[1])

        cv2.rectangle(frame, (int(rect[0]), 250), (int(rect[1]), 270), (255, 0, 0), 2)
        coordinate_abs = rect[0] + coordinate_rel
        print(coordinate_rel, coordinate_abs)
        robot.set_frame(frame, 20)

        e = (rect[0] + rect[1]) / 2 - coordinate_rel
        d = (coordinate_rel - e_old) * 0.3
        e_old = coordinate_rel
        rect[0] = robot.constrain(coordinate_abs - 35 + d, 0, 630)
        rect[1] = robot.constrain(coordinate_abs + 35 + d, int(rect[0]) + 1, 640)

        if abs(e) < 10:
            # robot.move(40)
            robot.move(0)
        else:
            # robot.move(35)
            robot.move(0)
        u = e * 1 + 90
        u = 180 - u
        # print(coordinate_abs, u)
        robot.servo(u)
    else:
        robot.servo(90)
        robot.move(40)
        print("error")

# 150
# center 33
# max 62
# min 13
