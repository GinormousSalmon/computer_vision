import RobotAPI as rapi

robot = rapi.RobotAPI()

import numpy as np
import cv2
import threading

yellow_list = []
green_list = []
red_list = []


def findYellow():
    global yellow_list
    low_stop_yellow = np.array([20, 100, 0])
    up_stop_yellow = np.array([38, 252, 256])
    while True:
        hsv = cv2.cvtColor(robot.get_frame(), cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, low_stop_yellow, up_stop_yellow)
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        yellow_list = []
        for contur in contours:
            x, y, w, h = cv2.boundingRect(contur)
            if cv2.contourArea(contur) > 1500:
                yellow_list.append([x, y, w, h])


my_thread_yellow = threading.Thread(target=findYellow)
my_thread_yellow.daemon = True
my_thread_yellow.start()


def findGreen():
    global green_list
    low_stop_green = np.array([40, 100, 0])
    up_stop_green = np.array([71, 252, 256])
    while True:
        hsv = cv2.cvtColor(robot.get_frame(), cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, low_stop_green, up_stop_green)
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        green_list = []
        for contur in contours:
            x, y, w, h = cv2.boundingRect(contur)
            if cv2.contourArea(contur) > 1500:
                green_list.append([x, y, w, h])


my_thread_green = threading.Thread(target=findGreen)
my_thread_green.daemon = True
my_thread_green.start()


def findRed():
    global red_list
    low_stop_red = np.array([170, 100, 0])
    up_stop_red = np.array([256, 252, 256])
    while True:
        hsv = cv2.cvtColor(robot.get_frame(), cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, low_stop_red, up_stop_red)
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        red_list = []
        for contur in contours:
            x, y, w, h = cv2.boundingRect(contur)
            if cv2.contourArea(contur) > 1500:
                red_list.append([x, y, w, h])


my_thread_red = threading.Thread(target=findRed)
my_thread_red.daemon = True
my_thread_red.start()

while True:

    if robot.manual() == 1:
        continue

    frame = robot.get_frame().copy()

    for y in green_list:
        x, y, w, h = y
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
    for y in yellow_list:
        x, y, w, h = y
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 1)
    for y in red_list:
        x, y, w, h = y
        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
    robot.set_frame(frame)
