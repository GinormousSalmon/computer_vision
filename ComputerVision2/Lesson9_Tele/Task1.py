import RobotAPI as rapi

robot = rapi.RobotAPI()

#robot.start()
while True:
    m = robot.get_key()
    if m!=-1:
        print(m)
