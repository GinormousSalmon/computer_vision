import RobotAPI as rapi

robot = rapi.RobotAPI()


def manual(show_code=False):
    m = robot.get_key()

    if 'regim' not in manual.__dict__:
        manual.regim = 0

    if m == 49:  # клавиша1
        if manual.regim == 0:
            print("manual on")
            manual.regim = 1
            robot.red()
        else:
            print("manual off")
            manual.regim = 0
            robot.color_off()

    if manual.regim==0:
        return manual.regim

    if m > -1 and manual.regim==1:
        if 'angle' not in manual.__dict__:
            manual.angle = 0
        if 'speed' not in manual.__dict__:
            manual.speed = 200
        if 'video' not in manual.__dict__:
            manual.video = 0

        if m == 38:
            robot.move(manual.speed, manual.speed, 50, True)
        if m == 40:
            robot.move(-manual.speed, -manual.speed, 50, True)
        if m == 39:
            robot.move(manual.speed, -manual.speed, 50, True)
        if m == 37:
            robot.move(-manual.speed, manual.speed, 50, True)
        if m == 105:
            robot.move(manual.speed, manual.speed/3, 50, True)
        if m == 188:
            manual.angle -= 1
            robot.serv(manual.angle)
        if m == 190:
            manual.angle += 1
            robot.serv(manual.angle)
        if m == 32:
            angle = 0
            robot.serv(angle)
        if m == 66:
            robot.tone(1000, 50)
        if m ==189:
            manual.speed-=20
            if manual.speed <100:
                manual.speed=100

        if m ==187:
            manual.speed+=20
            if manual.speed > 250:
                manual.speed = 250

        if m == 86:
            if manual.video == 0:
                manual.video = 1
            else:
                manual.video = 0
        if show_code:
            print(m)

        robot.set_frame(robot.get_frame())

    if manual.regim==1 and manual.video==1:
        robot.set_frame(robot.get_frame())

    return manual.regim

while True:
    if robot.button() == 1:
        break

    if manual()==1:
        continue

    robot.color_off()


    robot.set_frame(robot.get_frame(), 50)

        # robot.wait(200)
