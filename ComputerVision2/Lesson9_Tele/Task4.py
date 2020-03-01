from ComputerVision2.Examples import signs
import RobotAPI as rapi

robot = rapi.RobotAPI()
mode = 0


def manual(type):
    if type == 87:
        robot.move(150, 150, 10)
    if type == 83:
        robot.move(-150, -150, 10)
    if type == 68:
        robot.move(150, -150, 15)
    if type == 65:
        robot.move(-150, 150, 15)


def robotGo():
    robot.step(150, 150)
    frame = robot.get_frame()
    sign = signs.find_signs(frame)
    if sign is not None:
        return 0
    else:
        return 1


while True:
    key = robot.get_key()
    if key == 49:
        mode = 0
    if key == 50:
        mode = 1
    if mode == 0:
        manual(key)
    if mode == 1:
        mode = robotGo()
