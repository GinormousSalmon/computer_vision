import cv2
import numpy


def nothing(x):
    pass


cv2.namedWindow("frame")
capture = cv2.VideoCapture()
capture.open(0)
cv2.createTrackbar('param1', 'frame', 10, 300, nothing)
cv2.createTrackbar('param2', 'frame', 10, 300, nothing)
while True:
    s, frame = capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, cv2.getTrackbarPos("param1", "frame"), cv2.getTrackbarPos("param2", "frame"),
                      apertureSize=3)
    contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(len(contours))
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)
    cv2.imshow("frame", numpy.hstack([frame, cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)]))
    k = cv2.waitKey(10)
    if k == ord('s') or k == ord('ы'):
        cv2.destroyAllWindows()
        capture.release()
        break
