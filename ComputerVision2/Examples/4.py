import RobotAPI as rapi
import cv2
import zbar

robot = rapi.RobotAPI()

robot.button()
robot.tone(10000,100)
scanner = zbar.Scanner()

def draw_qr(frame, p):
    cv2.line(frame, (p[0][0], p[0][1]), (p[1][0], p[1][1]), (255, 0, 0), 5)
    cv2.line(frame, (p[2][0], p[2][1]), (p[1][0], p[1][1]), (255, 0, 0), 5)
    cv2.line(frame, (p[2][0], p[2][1]), (p[3][0], p[3][1]), (255, 0, 0), 5)
    cv2.line(frame, (p[0][0], p[0][1]), (p[3][0], p[3][1]), (255, 0, 0), 5)
    cv2.putText(frame, data, (p[0][0], p[0][1]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
    return frame


while True:
    if robot.button() == 1:
        robot.tone(7000, 100)
        break
    frame = robot.get_frame()

    results = scanner.scan(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    robot.rgb(0, 0, 0)
    for result in results:
        data = result.data.decode("utf-8")
        if data == "green":
            robot.rgb(0, 255, 0)
        if data == "red":
            robot.rgb(255, 0, 0)
        if data == "blue":
            robot.rgb(0, 0, 255)
        frame = draw_qr(frame, result.position)
        print(data, result.position)

    robot.set_frame(frame)
