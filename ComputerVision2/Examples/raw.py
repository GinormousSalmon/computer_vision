import RobotAPI as rapi

robot = rapi.RobotAPI()

print("Start RAW")
while 1:
    frame = robot.get_frame()
    robot.manual()
    robot.wait(10)
    robot.set_frame(frame)
