# import RoboRacers.RobotAPI as RobotAPI
import RobotAPI
import time
import cv2
import numpy
import math

robot = RobotAPI.RobotAPI(0)
# robot.set_camera(fps=30, width=640, height=480)
frame = robot.get_frame()
width = frame.shape[1]
height = frame.shape[0]

low = numpy.array([0, 0, 0])
high = numpy.array([255, 255, 255])
ksize = 4

robot.manual_regim = 1
print("Start")
robot.ready()
# robot.move(45)
robot.servo(90)
turns = 0
e_old = 0
while 1:
    if robot.manual() == 1:
        continue
    frame = robot.get_frame()
    # cv2.rectangle(frame, (140, height - 250), (width - 350, height - 230), (255, 0, 0), 2)
    # median_blur = cv2.medianBlur(frame, ksize - 1)
    # grey = cv2.cvtColor(median_blur, cv2.COLOR_BGR2GRAY)
    # canny = cv2.Canny(grey, 150, 200)
    # robot.set_frame(canny, 20)
    # continue

    crop = frame[height - 250:height - 230, 135:width - 350].copy()
    median_blur = cv2.medianBlur(crop, ksize - 1)
    grey = cv2.cvtColor(median_blur, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(grey, 150, 200)
    lines = cv2.HoughLines(canny, 1, numpy.pi / 180, 20, None, 0, 0)

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
            if abs(lines_convert[x] - lines_convert[x + 1]) < 10:
                lines_convert.remove(lines_convert[x + 1])
            else:
                x += 1

        coordinate = 0
        if len(lines_convert) > 0:
            for l in lines_convert:
                pt1 = (l, 0)
                pt2 = (l, 15)
                cv2.line(crop, pt1, pt2, (0, 255, 0), 3, cv2.LINE_AA)
                coordinate += l
            coordinate /= len(lines_convert)

        pt1 = (int(coordinate), 0)
        pt2 = (int(coordinate), 15)
        cv2.line(crop, pt1, pt2, (255, 0, 0), 3, cv2.LINE_AA)
        # print(coordinate, crop_line.shape[1])
        robot.set_frame(crop, 20)

        e = 50 - coordinate
        if abs(e) > 56:
            turns += 1
            print(coordinate, e)
            # if turns != 6:
            robot.servo(60)
            # else:
            #     robot.servo(140)
            robot.move(-40)
            time.sleep(0.4)
            #if turns != 6:
            robot.servo(140)
            # else:
            #     robot.servo(60)
            # robot.move(45)
            robot.move(40)
            time.sleep(0.7)
        else:
            if abs(e) < 14:
                robot.move(45)
            else:
                robot.move(49)
        u = e * 0.75 + (e - e_old) * 1.5 + 90
        u = robot.constrain(180 - u, 67, 200)
        e_old = e
        robot.servo(u)
        print(u, e)
    else:
        robot.move(42)
        print("error")
        # robot.servo(90)

# 150
# center 33
# max 62
# min 13
