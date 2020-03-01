import RobotAPI as rapi

robot = rapi.RobotAPI()

#robot.start()
while True:
    key = robot.get_key()
    if key == 87:
        robot.move(100, 100, 2)
        while key == 87:
            key = robot.get_key()
    if key == 83:
        robot.move(-100, -100, 2)
        while key == 83:
            key = robot.get_key()
    if key == 68:
        robot.move(100, -100, 2)
        while key == 68:
            key = robot.get_key()
    if key == 65:
        robot.move(100, -100, 2)
        while key == 65:
            key = robot.get_key()
