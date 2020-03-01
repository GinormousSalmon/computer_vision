import RobotAPI as rapi

robot = rapi.RobotAPI()
vcc_old = robot.vcc()
timer = robot.millis()
timerDist = robot.millis()


def vccTest():
    global vcc_old
    global timer
    if robot.millis() > timer + 200:
        timer = robot.millis()
        vcc = robot.vcc()
        if vcc - vcc_old > 0.7:
            vcc_old = vcc
            return 1
        else:
            if vcc - vcc_old < -0.7:
                vcc_old = vcc
                return -1
            else:
                vcc_old = vcc
                return 0


while True:
    robot.start()
    robot.red()

    while vccTest() != 1:
        if robot.dist() < 24:
            if robot.millis() > timerDist + 1500:
                robot.move(-100, -100, 250)
                robot.wait(400)
                timerDist = robot.millis()
        else:
            timerDist = robot.millis()
        robot.step(230, 230, 12)
    robot.red()
    robot.start()
    robot.move(-100, -100, 250)
    robot.wait(250)
