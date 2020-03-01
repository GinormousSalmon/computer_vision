import cv2
import random
import numpy as np

# Create windows to show the captured images
cv2.namedWindow("window_a", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("window_b", cv2.WINDOW_AUTOSIZE)

# Structuring element
es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
# Webcam Settings
capture = cv2.VideoCapture()
capture.open(0)


_, frame = capture.read()
previous = frame.copy()
frameWidth = frame.shape[1]
frameHeight = frame.shape[0]
while True:
    # Capture a frame
    flag, frame = capture.read()

    current = cv2.blur(frame, (5, 5))
    difference = cv2.absdiff(current, previous)  # difference is taken of the current frame and the previous frame

    frame2 = cv2.cvtColor(difference, cv2.COLOR_RGB2GRAY)
    # retval, thresh = cv2.threshold(frame2, 10, 0xff, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
    # retval, thresh = cv2.threshold(frame2, 10, 0xff, cv2.THRESH_TOZERO)
    # retval, thresh = cv2.threshold(frame2, 10, 0xff, cv2.CALIB_CB_ADAPTIVE_THRESH)
    retval, thresh = cv2.threshold(frame2, 10, 0xff, cv2.THRESH_BINARY)
    # dilated1 = cv2.dilate(thresh, es)
    # dilated2 = cv2.dilate(dilated1, es)
    # dilated3 = cv2.dilate(dilated2, es)
    # dilated4 = cv2.dilate(dilated3, es)

    cv2.imshow('window_a', thresh)
    cv2.imshow('window_b', frame)

    previous = current.copy()

    key = cv2.waitKey(10)  # 20
    if key == 27:  # exit on ESC
        cv2.destroyAllWindows()
        break
