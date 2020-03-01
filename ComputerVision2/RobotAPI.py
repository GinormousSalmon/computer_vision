import serial
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
    manual_speed = 200
    manual_angle = 0
    frame = []
    mouse_x = -1
    mouse_y = -1

    def __init__(self, flag_video=True, flag_keyboard=True):
        print("\x1b[42m" + "Start script" + "\x1b[0m")
        atexit.register(self.cleanup)
        # print("open robot port")
        if socket.gethostname().find("ras") == 0:
            self.comp_name = "raspberry"
            self.port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
        else:
            self.comp_name = "orange"
            self.port = serial.Serial("/dev/ttyS3", baudrate=115200, timeout=3.0)
        # vsc.VideoClient.inst().subscribe("ipc")
        # vsc.VideoClient.inst().subscribe("tcp://127.0.0.1")
        # vsc.VideoClient.inst().subscribe("udp://127.0.0.1")

        # while True:
        #     frame = vsc.VideoClient.inst().get_frame()
        #     if frame.size != 4:
        #         break
        self.cap = cv2.VideoCapture(0)
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
            self.my_thread_video = threading.Thread(target=self.send_frame)
            self.my_thread_video.daemon = True

            self.my_thread_video.start()

        if flag_keyboard:
            self.context2 = zmq.Context(1)
            self.socket2 = self.context2.socket(zmq.REP)

            self.socket2.bind("tcp://*:5559")
            # print("start video server")
            self.server_keyboard = True
            self.my_thread = threading.Thread(target=self.recive_key)
            self.my_thread.daemon = True
            self.my_thread.start()

        # серву выставляем в нуль

        self.serv(0)
        # очищаем буфер кнопки( если была нажата, то сбрасываем)
        self.button()
        # выключаем все светодиоды
        self.color_off()
        self.stop_frames = False
        self.my_thread_f = threading.Thread(target=self.work_f)
        self.my_thread_f.daemon = True
        self.my_thread_f.start()

        self.manual_video = 1

        pass

    def cleanup(self):
        print("stoping")
        self.cap.release()
        self.color_off()
        self.serv(0)
        self.stop_frames = True
        self.wait(300)
        self.frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
        self.wait(1000)

        # self.cap.release()

    def set_camera(self, fps=30, width=640, height=480):
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

    def recive_key(self):
        while True:
            message = self.socket2.recv_string()
            if message.find("m") > -1:
                message = message.split(",")
                self.mouse_x = int(message[1])
                self.mouse_y = int(message[2])
                # print(message)
            else:
                self.last_key = int(message.lstrip())
            self.socket2.send_string("1")
            # print(self.last_key)
            # self.wait(10)
        pass

    def work_f(self):
        self.stop_frames = False
        while True:
            if self.stop_frames == False:
                ret, frame = self.cap.read()
                if ret:
                    self.frame = frame
                    self.time_frame = time.time()

            # self.wait(1)
        pass

    def get_key(self, clear=True):
        l = self.last_key
        self.last_key = -1
        return l

    def get_frame(self):

        return self.frame

    def send_frame(self):
        while True:
            if self.last_frame is not None:
                if self.server_flag == True and self.last_frame.shape[0] > 2:

                    # print("robot api video" +str(time.time()))
                    message = self.socket.recv_string()
                    # print("send")
                    # self.socket.send_string(str(time.time()))

                    if message == "1":
                        # self.socket.send_string(str(time.time()),zmq.SNDMORE)
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                        result, frame = cv2.imencode('.jpg', self.last_frame, encode_param)

                        md = dict(
                            arrayname="jpg",
                            dtype=str(frame.dtype),
                            shape=frame.shape,
                        )

                        self.socket.send_json(md, zmq.SNDMORE)
                        self.socket.send(frame, 0)
                    else:
                        self.socket.send_string("0")

                self.wait(10)
                continue

    def set_frame(self, frame, quality=50):
        self.quality = quality
        self.last_frame = frame
        return

    def wait(self, t):
        # print(t/1000)
        time.sleep(t / 1000)

    def send(self, message, flag_wait=True):
        # print("send message")
        self.port.write(str(message).encode("utf-8"))
        # time.sleep(0.01)
        answer = ""
        if flag_wait:
            while self.port.in_waiting == False:
                pass
        while self.port.in_waiting:
            answer = answer + str(self.port.readline())
        return answer[:len(answer) - 5]  # удаляем \r\n

    def rgb(self, r, g, b):
        return self.send("RGB," + str(r) + "," + str(g) + "," + str(b) + "|")

    def move(self, m1, m2, timer=10, wait=False):
        if timer < 50:
            wait = True
        if m1 > 255:
            m1 = 255
        if m2 > 255:
            m2 = 255
        if m1 < -255:
            m1 = -255
        if m2 < -255:
            m2 = -255
        m = self.send("MOVE," + str(m1) + "," + str(m2) + "," + str(timer) + "|")
        if wait:
            self.wait(timer)

        return m

    def tone(self, fr, timer, wait=False):
        mes = self.send("TONE," + str(fr) + "," + str(timer) + "|")
        if wait:
            self.wait(timer)
        return mes

    def serv(self, angle):
        if angle > 60:
            angle = 60
        if angle < -60:
            angle = -60

        return self.send("SERV," + str(angle) + "|")

    def dist(self):
        s = self.send("DIST,|")
        s = s.split(",")
        d = -1
        try:
            d = float(s[1])
        except:
            pass
        return d

    def vcc(self):
        s = self.send("VCC,|")
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
        s = self.send("VCST," + str(k) + "|")
        s = s.split(",")
        return float(s[1])

    def button(self):
        s = self.send("BUTT,|")
        s = s.split(",")
        # print(s)
        return int(float(s[1]))

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
        if motorL > 255:
            motorL = 255
        if motorR > 255:
            motorR = 255
        if motorL < -255:
            motorL = -255
        if motorR < -255:
            motorR = -255
        m = self.send("STEP," + str(motorL) + "," + str(motorR) + "," + str(pulse_go) + "," + str(pause_go) + "," + str(
            pulse_stop) + "," + str(pause_stop) + "," + str(time_step) + "|")
        # print(m)
        if wait:
            self.wait(time_step)
        # self.move(motorL, motorR, pulse_go)
        # self.wait(pause_go)
        # self.move(-motorL, -motorR, pulse_stop)
        # self.wait(pause_stop)
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
            self.set_frame(self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(frame, "manual", 280, 20))))

        return self.manual_regim
