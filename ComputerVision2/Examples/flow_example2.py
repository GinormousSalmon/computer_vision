import numpy as np
import cv2
import RobotAPI as rapi

robot = rapi.RobotAPI()

#cap = cv2.VideoCapture("vtest.avi")
frame1 = robot.get_frame()
frame1 = cv2.resize(frame1, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
prvs = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
hsv = np.zeros_like(frame1)
hsv[...,1] = 255
while(1):
    frame2 = robot.get_frame()
    frame2 = cv2.resize(frame2, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    next = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prvs,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
    bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
    robot.set_frame(bgr)
    prvs = next

cv2.destroyAllWindows()