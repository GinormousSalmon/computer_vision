import time
# import VideoServiceClient as vsc
import zmq
import cv2
import threading
import numpy as np
import atexit
import socket


class RobotAPI:
    port = None
    server_flag = False
    last_key = -1
    last_frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
    quality = 50
    manual_regim = 0
    manual_video = 1
    manual_speed = 150
    manual_angle = 0
    frame = []
    mouse_x = -1
    mouse_y = -1
    joy_x = 0
    joy_y = 0
    joy_data = []
    small_frame = 0
    motor_left = 0
    motor_rigth = 0
    flag_serial = False
    flag_pyboard = False
    __time_old_frame = time.time()

    def __init__(self, flag_video=True, flag_keyboard=True, flag_serial=True, flag_pyboard=False):
        # print("\x1b[42m" + "Start script" + "\x1b[0m")
        self.flag_serial = flag_serial
        self.flag_pyboard = flag_pyboard

        print("Start script")
        atexit.register(self.cleanup)
        # print("open robot port")
        if flag_serial:
            import serial
            if socket.gethostname().find("ras") == 0:
                self.comp_name = "raspberry"
                if flag_pyboard:
                    self.port = serial.Serial("/dev/ttyS0", baudrate=1000000)
                    # self.port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=0.01)
                else:
                    self.port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=0.001)
                    # self.port = serial.Serial("/dev/ttyS0", baudrate=115200)

            else:
                self.comp_name = "orange"
                self.port = serial.Serial("/dev/ttyS3", baudrate=115200, timeout=0.01)
        # vsc.VideoClient.inst().subscribe("ipc")
        # vsc.VideoClient.inst().subscribe("tcp://127.0.0.1")
        # vsc.VideoClient.inst().subscribe("udp://127.0.0.1")

        # while True:
        #     frame = vsc.VideoClient.inst().get_frame()
        #     if frame.size != 4:
        #         break
        self.init_cam(0)
        # self.cap.set(cv2.CAP_PROP_FPS, 30)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.cap.open(0)
        # if camera_high_res:
        #     self.set_camera_high_res()
        r, self.frame = self.cap.read()
        self.time_frame = time.time()

        if flag_video:
            self.context = zmq.Context(1)
            self.socket = self.context.socket(zmq.REP)

            self.socket.bind("tcp://*:5555")
            # print("start video server")
            self.server_flag = True
            self.my_thread_video = threading.Thread(target=self.__send_frame)
            self.my_thread_video.daemon = True

            self.my_thread_video.start()

        if flag_keyboard:
            self.context2 = zmq.Context(1)
            self.socket2 = self.context2.socket(zmq.REP)

            self.socket2.bind("tcp://*:5559")
            # print("start video server")
            self.server_keyboard = True
            self.my_thread = threading.Thread(target=self.__recive_key)
            self.my_thread.daemon = True
            self.my_thread.start()

        # серву выставляем в нуль

        if self.flag_serial:
            self.serv(0)
            # очищаем буфер кнопки( если была нажата, то сбрасываем)
            self.button()
            # выключаем все светодиоды
            self.color_off()
        self.stop_frames = False
        self.my_thread_f = threading.Thread(target=self.__work_f)
        self.my_thread_f.daemon = True
        self.my_thread_f.start()

        self.manual_video = 1
        pass
    def init_cam(self, num=0):
        self.cap = cv2.VideoCapture(num)

    def end_work(self):
        # self.cap.release()
        if self.flag_serial:
            self.color_off()
            self.serv(0)
        self.stop_frames = True
        self.wait(300)
        self.frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
        self.wait(1000)
        print("STOPED ")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_work()

    def cleanup(self):
        self.end_work()

        # self.cap.release()

    def set_camera(self, fps=60, width=640, height=480):
        self.stop_frames = True
        self.wait(500)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.wait(500)
        self.stop_frames = False

    def set_camera_high_res(self):
        self.set_camera(30, 1024, 720)

    def set_camera_low_res(self):
        self.set_camera(60, 320, 240)

    def __recive_key(self):
        while True:
            try:
                message = ""
                try:

                    message = self.socket2.recv_string()
                except:
                    pass
                # print(message)
                if message.find("m") > -1:
                    message = message.split(",")
                    self.mouse_x = int(message[1])
                    self.mouse_y = int(message[2])
                    # print(message)
                if message.find("j") > -1:
                    # message = message.split(",")
                    self.joy_data = message.split(",")[1:]
                    # print("recive joy", self.joy_data)
                # self.joy_x = float(message[1])
                # self.joy_y = float(message[2])
                else:
                    self.last_key = int(message.lstrip())
                try:
                    self.socket2.send_string("1")
                except:
                    pass
            except:
                pass
            # print(self.last_key)
            # self.wait(10)
        pass

    def __work_f(self):
        self.stop_frames = False
        while True:
            if self.stop_frames == False:
                ret, frame = self.cap.read()
                if ret:
                    self.frame = frame
                    self.time_frame = time.time()
            else:
                time.sleep(0.001)
        pass

    def get_key(self, clear=True):
        l = self.last_key
        self.last_key = -1
        return l

    def get_frame(self, wait_new_frame=False):
        if wait_new_frame:
            while self.time_frame <= self.__time_old_frame:
                time.sleep(0.001)
                pass
            self.__time_old_frame = self.time_frame
        return self.frame

    def __send_frame(self):

        while True:
            if self.last_frame is not None:
                if self.server_flag == True and self.last_frame.shape[0] > 2:

                    try:
                        message = self.socket.recv_string()
                    except:
                        pass

                    if message == "1":
                        try:
                            # encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
                            self.encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
                            result, frame = cv2.imencode('.jpg', self.last_frame, self.encode_param)

                            md = dict(
                                # arrayname="jpg",
                                dtype=str(frame.dtype),
                                shape=frame.shape,
                            )

                            self.socket.send_json(md, zmq.SNDMORE)
                            self.socket.send(frame, 0)


                        except:
                            pass
                else:
                    try:
                        self.socket.send_string("0")
                    except:
                        pass

                # self.wait(10)
                continue

    def set_frame(self, frame, quality=30):
        self.quality = quality
        self.last_frame = frame
        return

    def wait(self, t):
        # print(t/1000)
        time.sleep(t / 1000)

    def __send(self, message):
        if self.flag_serial:
            # print(message)
            # t = time.time()
            # while self.port.in_waiting == True:
            #     if time.time()-t>1:
            #         print("wait serial")
            #
            #     pass
            # while self.port.in_waiting:
            #     s = self.port.read(1)
            self.port.flushInput()
            self.port.write(message.encode("utf-8"))
            # time.sleep(0.01)
            # print("send ok")
            answer = ""

            while self.port.in_waiting == False:
                pass

            if self.flag_pyboard:
                # while 1:
                answer = b''
                while self.port.in_waiting:
                    s = self.port.read(1)
                    # print(s)

                    if s == b'|':
                        break
                    answer += s

                return str(answer, "utf-8")
            else:
                while self.port.in_waiting:
                    answer = answer + str(self.port.readline())
                # print(answer.rstrip())
                return answer.rstrip()  # удаляем \r\n
            # print(answer)
            #

            # return answer[:len(answer) - 5]  # удаляем \r\n
        return "0,0"

    def rgb(self, r, g, b):
        if self.flag_pyboard:
            return self.__send("C," + str(r) + "," + str(g) + "," + str(b) + "|")
        else:
            # return self.__send("RGB," + str(r) + "," + str(g) + "," + str(b) + "|")
            return self.__send("C," + str(r) + "," + str(g) + "," + str(b) + "|")

    def move(self, m1, m2, timer=10, wait=True):

        # if timer < 50:
        #     wait = True
        m1 = self.constrain(m1, -255, 255)
        m2 = self.constrain(m2, -255, 255)

        self.motor_left = m1
        self.motor_rigth = m2
        # f'http://{domain}/{lang}/{path}'

        if self.flag_pyboard:
            m = self.__send(''.join(["M,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))
        else:
            # m = self.__send(''.join(["MOVE,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))
            # print(''.join(["M,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))
            m = self.__send(''.join(["M,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))

        if wait:
            self.wait(timer)

        return m

    def move_fix_speed(self, m1, timer=10, p=1, i=0.001, d=0.1, wait=False):

        # дл роборэйсера
        # if timer < 50:
        #     wait = True
        m1 = self.constrain(m1, -255, 255)
        # m2 = self.constrain(m2, -255, 255)

        self.motor_left = m1
        # self.motor_rigth = m2
        # f'http://{domain}/{lang}/{path}'

        m = self.__send(
            ''.join(["F,", str(int(m1)), ",", str(0), ",", str(timer), ",", str(p), ",", str(i), ",", str(d), "|"]))
        # m = self.__send(''.join(["M,", str(int(m1)), ",", str(int(m2)), ",", str(timer), "|"]))
        # m = self.__send("MOVE," + str(int(m1)) + "," + str(int(m2)) + "," + str(timer) + "|")

        if wait:
            self.wait(timer)

        return m

    def accel(self):
        if self.flag_pyboard:
            m = self.__send("A|")
        else:
            m = self.__send("ACCEL|")
        s = str(m).split(",")
        x = 0
        y = 0
        z = 0
        try:
            x = float(s[1])
            y = float(s[2])
            z = float(s[3])
        except:
            pass
        return [x, y, z]

    def tone(self, fr, timer, wait=False):
        if self.flag_pyboard:
            mes = self.__send("T," + str(fr) + "," + str(timer) + "|")
        else:
            mes = self.__send("T," + str(fr) + "," + str(timer) + "|")
        if wait:
            self.wait(timer)
        return mes

    def light(self, l, wait=False):
        if self.flag_pyboard:
            mes = self.__send("L," + str(l) + "|")
        else:
            mes = self.__send("L," + str(l) + "|")
        return mes

    def sirena(self, timer, tone=100, wait=False):
        if self.flag_pyboard:
            mes = self.__send("Q," + str(timer) +","+ str(tone)+"|")
        else:
            mes = self.__send("Q," + str(timer) +","+ str(tone)+"|")
        return mes
    def serv(self, angle, num=0, min=-60, max=60):
        if angle > max:
            angle = max
        if angle < min:
            angle = min
        if self.flag_pyboard:
            return self.__send("S," + str(angle) + "|")
        else:
            # return self.__send("SERV," + str(angle) + "|")
            return self.__send(''.join(["S,", str(int(num)), ",", str(int(angle)), "|"]))

    def dist(self):
        if self.flag_pyboard:
            s = self.__send("D|")
        else:
            s = self.__send("D|")
        s = s.split(",")
        d = -1
        try:
            d = float(s[1])
        except:
            pass
        return d

    def rc(self):
        # print(s)
        d = []
        try:
            if self.flag_pyboard:
                s = self.__send("R|")
            else:
                s = self.__send("RC,|")
            s = s.split(",")
            if s[0] != 'RC':
                return d
            kol = int(s[1])
            s = s[2:]
            # print(len(s),kol)
            if len(s) != kol:
                return d

            for i in s:
                d.append(float(i))
        except:
            return []

        return d

    def compas(self):
        d = [0, 0, 0, 0]
        try:
            s = self.__send("COMPAS,|")
            s = s.split(",")

            d = [float(s[1]), float(s[2]), float(s[3]), float(s[4])]
        except:
            pass
        return d

    def gps(self):
        d = [0, 0, 0, 0, 0, 0]
        try:
            s = self.__send("GPS,|")
            s = s.split(",")

            d = [float(s[1]), float(s[2]), float(s[3]), float(s[4]), float(s[5]), float(s[5])]
        except:
            pass
        return d

    def vcc(self):
        if self.flag_pyboard:
            s = self.__send("V|")
        else:
            # s = self.__send("VCC,|")
            s = self.__send("V,|")
        # pos = s.find("VCC")

        # s = s[pos:]
        s = s.split(",")

        v = -1
        try:
            v = float(s[1])
        except:
            pass
        return v

    def speed(self):
        if self.flag_pyboard:
            s = self.__send("P|")
        else:
            s = self.__send("SPEED,|")
        # pos = s.find("VCC")
        # s = s[pos:]
        s = s.split(",")
        v = -1
        try:
            v = float(s[1])
        except:
            pass
        return v

    def vcst(self, k):
        s = self.__send("E," + str(k) + "|")
        s = s.split(",")
        v = 0
        try:
            v = float(s[1])
        except:
            pass
        return v

    def button(self):
        if self.flag_pyboard:
            s = self.__send("B|")
        else:
            # s = self.__send("BUTT,|")
            s = self.__send("B,|")
        s = s.split(",")
        v = 0
        try:
            v = int(float(s[1]))
        except:
            pass
        return v

    def start(self):
        self.button()
        self.rgb(0, 255, 0)
        self.tone(10000, 50)
        while (self.button() == 0):
            pass
        for i in range(10000, 15000, 500):
            self.tone(i, 50)
        self.wait(100)
        self.button()
        self.rgb(0, 0, 0)

    def beep(self):
        self.tone(10000, 50)
        self.wait(50)

    def green(self):
        self.rgb(0, 255, 0)

    def red(self):
        self.rgb(255, 0, 0)

    def blue(self):
        self.rgb(0, 0, 255)

    def color_off(self):
        self.rgb(0, 0, 0)

    def sound1(self):
        # for i in range (1000,10000,500):
        for i in range(15000, 1000, -500):
            self.tone(i, 50)

    def sound2(self):
        # for i in range (1000,10000,500):
        for i in range(1000, 15000, 500):
            self.tone(i, 50)

    # функция движения короткими импульсами
    def step(self, motorL, motorR, time_step=20, pulse_go=10, pause_go=20, pulse_stop=5, pause_stop=3, wait=True):
        motorL = self.constrain(motorL, -255, 255)
        motorR = self.constrain(motorR, -255, 255)
        self.motor_left = motorL
        self.motor_rigth = motorR

        m = self.__send(
            "STEP," + str(int(motorL)) + "," + str(int(motorR)) + "," + str(pulse_go) + "," + str(pause_go) + "," + str(
                pulse_stop) + "," + str(pause_stop) + "," + str(time_step) + "|")
        # print(m)
        if wait:
            self.wait(time_step)
        return m

    def millis(self):
        return int(round(time.time() * 1000))

    def text_to_frame(self, frame, text, x, y, font_color=(255, 255, 255), font_size=2):
        cv2.putText(frame, str(text), (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, font_color, font_size)
        return frame

    def vcc_to_frame(self, frame):
        return self.text_to_frame(frame, str(self.vcc()), 10, 20)

    def dist_to_frame(self, frame):
        return self.text_to_frame(frame, str(self.dist()), 550, 20)

    def distance_between_points(self, xa, ya, xb, yb, za=0, zb=0):
        return np.sqrt(np.sum((np.array((xa, ya, za)) - np.array((xb, yb, zb))) ** 2))

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def median(self, lst):
        if len(lst)>0:
            quotient, remainder = divmod(len(lst), 2)
            if remainder:
                return sorted(lst)[quotient]
            return sum(sorted(lst)[quotient - 1:quotient + 1]) / 2.

    def constrain(self, x, out_min, out_max):
        if x < out_min:
            return out_min
        elif out_max < x:
            return out_max
        else:
            return x

    def manual(self, c=-1, show_code=False):
        m = c
        if c == -1:
            m = self.get_key()
        frame = self.get_frame()

        if m == 49:  # клавиша1
            if self.manual_regim == 0:
                print("manual on")
                self.manual_regim = 1
                self.red()
            else:
                print("manual off")
                self.manual_regim = 0
                self.color_off()
        if m == 8:
            if self.small_frame == 1:
                self.small_frame = 0
            else:
                self.small_frame = 1

        if self.manual_regim == 0:
            return self.manual_regim

        if m > -1 and self.manual_regim == 1:

            if m == 38:
                self.move(self.manual_speed, self.manual_speed, 50, True)
            if m == 40:
                self.move(-self.manual_speed, -self.manual_speed, 50, True)
            if m == 39:
                self.move(self.manual_speed, -self.manual_speed, 50, True)
            if m == 37:
                self.move(-self.manual_speed, self.manual_speed, 50, True)
            if m == 188:
                self.manual_angle -= 30
                self.serv(self.manual_angle)
            if m == 190:
                self.manual_angle += 30
                self.serv(self.manual_angle)
            if m == 32:
                self.manual_angle = 0
                self.serv(self.manual_angle)
            if m == 66:
                self.tone(1000, 50)
            if m == 189:
                self.manual_speed -= 20
                if self.manual_speed < 100:
                    self.manual_speed = 100

            if m == 187:
                self.manual_speed += 20
                if self.manual_speed > 250:
                    self.manual_speed = 250

            if m == 86:
                if self.manual_video == 0:
                    self.manual_video = 1
                else:
                    self.manual_video = 0
            if show_code:
                print(m)

                #     self.set_frame(
                # self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(frame, "manual", 280, 20))))

        if self.manual_regim == 1 and self.manual_video == 1:

            if self.small_frame == 1:
                frame = cv2.resize(frame, None, fx=0.25, fy=0.25)
                self.set_frame(frame, 10)
                return self.manual_regim

            frame = self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(frame, "manual", 280, 20)))
            # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.set_frame(frame)

        return self.manual_regim
