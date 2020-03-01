import RobotAPI as rapi

robot = rapi.RobotAPI()


def manual(type):
    if type == 87:
        robot.move(150, 150, 10)
    if type == 83:
        robot.move(-150, -150, 10)
    if type == 68:
        robot.move(150, -150, 15)
    if type == 65:
        robot.move(-150, 150, 15)


#robot.start()
mode = 0

while True:
    key = robot.get_key()
    if key == 49:
        mode = 0
    if key == 50:
        mode = 1
    if mode == 0:
        manual(key)
    if mode == 1:
        robot.step(150, 150)
