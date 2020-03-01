import RobotAPI as rapi

robot = rapi.RobotAPI()
vcc_old = robot.vcc()
robot.start()
robot.rgb(255, 0, 0)
while True:
    vcc = robot.vcc()
    if vcc - vcc_old > 0.3:
        robot.beep()
        robot.rgb(0, 255, 0)
    if vcc - vcc_old < -0.3:
        robot.beep()
        robot.rgb(255, 0, 0)
    vcc_old = vcc
    robot.wait(0.1)
