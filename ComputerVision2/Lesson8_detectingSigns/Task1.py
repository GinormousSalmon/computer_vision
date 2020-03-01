import RobotAPI as rapi
import cv2
import numpy


def findSign(frame):
    result = []
    type = ""
    low = numpy.array([92, 84, 42])
    high = numpy.array([145, 255, 255])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if contours is not None:
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if cv2.contourArea(contour) > 4000 and min(h, w) / max(h, w) > 0.9:
                cut = mask[y:y + h, x:x + w]
                if cut[int(h / 4), int(w / 2)] == 0:
                    type = "forward"
                else:
                    if cut[int(h / 2), int(w / 4 * 3)] == 0:
                        type = "right"
                    else:
                        if cut[int(h / 2), int(w / 4)] == 0:
                            type = "left"
            result.append([x, y, w, h, type])
    return result


robot = rapi.RobotAPI()

robot.start()

while True:
    frame = robot.get_frame()
    low = numpy.array([92, 84, 42])
    high = numpy.array([145, 255, 255])
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if contours is not None:
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if cv2.contourArea(contour) > 4000 and min(h, w)/max(h, w) > 0.9:
                cut = mask[y:y + h, x:x + w]
                if cut[int(h / 4), int(w / 2)] == 0:
                    cv2.putText(cut, "forward", (0, 13), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1)
                else:
                    if cut[int(h / 2), int(w / 4 * 3)] == 0:
                        cv2.putText(cut, "right", (0, 13), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1)
                    else:
                        if cut[int(h / 2), int(w / 4)] == 0:
                            cv2.putText(cut, "left", (0, 13), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1)
                robot.set_frame(cut)
