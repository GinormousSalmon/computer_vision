import RobotAPI
import cv2

robot = RobotAPI.RobotAPI()
robot.start()
robot.serv(5)

while True:
    frame = robot.get_frame()
    x = frame.shape[1]
    y = frame.shape[0]
    crop = frame[y - 100:y - 0, 70:x - 70].copy()
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, 20, 70, apertureSize=3)
    im2, contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cannyColor = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)
    xNow = frame.shape[1] / 2
    if len(contours) > 0:
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            xNow += x + w / 2
            cv2.rectangle(cannyColor, (x, y), (x + w, y + h), (255, 0, 0), 1)
        xNow /= len(contours)
    U = frame.shape[1] / 2 - xNow
    U *= 0.7
    # print(U)
    robot.move(70 - U, 70 + U, 5)
    # frame = numpy.vstack([crop, cannyColor])
    # robot.set_frame(cannyColor)
