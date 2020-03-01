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
        sum = 0
        for i in range (1, 100):
            sum += robot.vcc()
        sum /= 100
        v = sum
        delta = v - last_vcc
        print("delta", delta)
        #if v > 11.8:
           # print("HIGH VCC", v)
           # robot.green()
          #  status = 1

        if abs(delta) > 0.3:

            if delta > 0:
                robot.green()
                status = 1
                print("HIGH DELTA", delta)

            if delta < -0.3:
                robot.color_off()
                status = -1

        last_vcc = v
        timer_vcc = robot.millis()
    return status


count_dist = 0


def parking():
    global count_dist
    robot.step(110, 110)
    if vcc_test() == 1:
        return 1
    print(robot.dist())
    if robot.dist() < 270:
        count_dist += 1
        if count_dist > 100:
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
        countur_rect = np.array(result.position)
        name = result.data.decode("utf-8")
        area = cv2.contourArea(countur_rect)
        x, y, w, h = cv2.boundingRect(countur_rect)
        all_qr.append([name, area, x, y, w, h, result.position])
    return all_qr


def distance_between_points(xa, ya, xb, yb, za=0, zb=0):
    return np.sqrt(np.sum((np.array((xa, ya, za)) - np.array((xb, yb, zb))) ** 2))


# phase = "parking"
# phase = "chargeS"
# phase = "chargeB"
phase = "bigQR"
count_fail_chargeS = 0
robot.serv(0)
n = 0
while True:
    if robot.manual(show_code=True) == 1:
        phase = "bigQR"
        continue

    frame = robot.get_frame()

    qrs = []
    if phase != "parking" or phase == "bigQR":
        qrs = find_qr()

    if phase == "bigQR":
        found = 0
        for qr in qrs:
            # print(qr)
            name, area, x, y, h, w, pos = qr
            if name == "charge":
                found = 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 4)
                center = x + int(w / 2)
                e = (320 - center) * 4
                # robot.move(255 - e, 255 + e, 7)
                robot.step(180 - e, 180 + e, 80)
                if area > 45000:
                    print("area" + str(area))
                    phase = "smallQR"
        if found == 0:
            robot.step(180, 180, 80)
            n += 1
        else:
            n = 0
        if n == 15:
            n = 0
            print("not found")
            phase = "smallQR"
        #continue

    if phase == "smallQR":
        # выполняем движение робота ориентируясь по маленькому знаку
        found = 0
        for qr in qrs:
            # print(qr)
            name, area, x, y, h, w, pos = qr
            if name == "chargeS":
                found = 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 4)
                center = x + int(w / 2)
                e = (200 - center) * 4
                # robot.move(255 - e, 255 + e, 8)
                robot.step(170 - e, 170 + e, 80)
                if area > 20000:
                    phase = "parking"
        if found == 0:
            n += 1
        else:
            n = 0
        if n == 10:
            phase = "parking"
            n = 0
        # robot.move(180, 180, 20)
            #continue

    if phase == "parking":
        # print("parking")
        res = parking()
        # если функция парковки вернула успех, то завершаем парковку
        if res == 1:
            robot.sound1()
            robot.wait(500)
            phase = "charging"
        if res == -1:
            # функция парковки вернула результат сбоя парковки
            print("Fail parking")
            robot.step(-250, -250, 1000)
            phase = "bigQR"
            # возможно требуется перейти на стадию ориентации по QR коду
            #pass

    if phase == "charging":

        # следущий этап проверим, что зарядка действительно идет
        # если напряжение недостаточное, то перепарковываемся
        #vcc = robot.vcc()
        # print(vcc, "CHARGING")
        # robot.wait(2000)
        # key = robot.get_key()
        # if key == ord("p"):
            # print("p")
        if vcc_test() == -1:
            #print(vcc, "LOW VCC, reparking...")
            phase = "parking"

    robot.text_to_frame(frame, phase, 20, 20)
    robot.text_to_frame(frame, str(robot.vcc()), 180, 20)
    robot.text_to_frame(frame, str(robot.dist()), 270, 20)
    robot.set_frame(frame)
