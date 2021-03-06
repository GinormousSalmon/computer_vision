import RobotAPI as rapi
import numpy as np
import cv2
import zbar

scanner = zbar.Scanner()

robot = rapi.RobotAPI()

timer_vcc = robot.millis()
last_vcc = robot.vcc()


def vcc_test():
    global timer_vcc, last_vcc
    status = 0
    if timer_vcc + 1000 < robot.millis():
        v = robot.vcc()
        delta = v - last_vcc
        print("v", v)
        if v > 11.8:
            print("HIGH VCC", v)
            robot.green()
            status = 1

        if abs(delta) > 0.6:

            if delta > 0:
                robot.green()
                status = 1
                print("HIGH DELTA", delta)

            if delta < 0:
                robot.color_off()
                status = 0

        last_vcc = v
        timer_vcc = robot.millis()
    return status


count_dist = 0


def parking():
    global count_dist
    robot.step(150, 150)
    if vcc_test() == 1:
        return 1
    print(robot.dist())
    if robot.dist() < 15:
        count_dist += 1
        if count_dist > 15:
            print("small dist")
            robot.step(-200, -200, time_step=1500)
            robot.wait(500)
            count_dist = 0
            return -1
    return 0


def find_qr():
    all_qr = []
    results = scanner.scan(cv2.cvtColor(robot.get_frame(), cv2.COLOR_BGR2GRAY))
    for result in results:
        contour_rect = np.array(result.position)
        name = result.data.decode("utf-8")
        area = cv2.contourArea(contour_rect)
        x, y, w, h = cv2.boundingRect(contour_rect)
        all_qr.append([name, area, x, y, w, h, result.position])
    return all_qr


def distance_between_points(xa, ya, xb, yb, za=0, zb=0):
    return np.sqrt(np.sum((np.array((xa, ya, za)) - np.array((xb, yb, zb))) ** 2))


# faza = "parking"
faza = "chargeS"
# faza = "chargeB"
# faza = "charge"
count_fail_chargeS = 0
robot.serv(0)

while True:
    if robot.button() == 1:
        break
    if robot.manual(1) == 1:
        continue

    frame = robot.get_frame()

    qrs = []
    if faza != "parking" or faza == "charge":
        qrs = find_qr()

    if faza == "chargeS":
        # выполняем движение робота ориентируясь по маленькому знаку
        for qr in qrs:
            print(qr)
            name, area, x, y, h, w, pos = qr
            continue

    if faza == "parking":
        print("parking")
        res = parking()
        # если функция парковки вернула успех, то завершаем парковку
        if res == 1:
            robot.sound1()
            robot.wait(1000)
            faza = "charging"
        if res == -1:
            # функция парковки вернула результат сбоя парковки
            print("Fail parking")
            robot.step(-250, -250, 1000)
            faza = "chargeS"
            # возможно требуется перейти на стадию ориентации по QR коду
            pass

    if faza == "charging":

        # следущий этап проверим, что зарядка действительно идет
        # если напряжение недостаточное, то перепарковываемся
        vcc = robot.vcc()
        print(vcc, "CHARGING")
        robot.wait(5000)
        if vcc < 11.0:
            print(vcc, "LOW VCC, reparking...")
            faza = "parking"

    robot.set_frame(frame)
