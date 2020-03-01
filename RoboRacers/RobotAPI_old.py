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
    manual_speed = 20
    manual_angle = 90
    frame = []
    mouse_x = -1
    mouse_y = -1
    joy_x = 0
    joy_y = 0
    small_frame = 0

    def __init__(self, flag_video=True, flag_keyboard=True):
        # print("\x1b[42m" + "Start script" + "\x1b[0m")
        print("Start script")
        atexit.register(self.cleanup)
        # print("open robot port")
        self.port = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=0.1)
        # vsc.VideoClient.inst().subscribe("ipc")
        # vsc.VideoClient.inst().subscribe("tcp://127.0.0.1")
        # vsc.VideoClient.inst().subscribe("udp://127.0.0.1")

        # while True:
        #     frame = vsc.VideoClient.inst().get_frame()
        #     if frame.size != 4:
        #         break
        self.cap = cv2.VideoCapture()
        self.cap.open(0)
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
            self.my_thread = threading.Thread(target=self.receive_key)
            self.my_thread.daemon = True
            self.my_thread.start()

        # self.servo(0)
        # self.button()
        self.stop_frames = False
        self.my_thread_f = threading.Thread(target=self.work_f)
        self.my_thread_f.daemon = True
        self.my_thread_f.start()

        self.manual_video = 1
        pass

    def ready(self):
        time.sleep(1)
        self.send("READY", flag_wait=True)

    def cleanup(self):
        # self.cap.release()
        self.stop_frames = True
        self.wait(300)
        self.frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
        self.wait(1000)
        print("STOPED ")

        # self.cap.release()

    def set_camera(self, fps=60, width=640, height=480):
        self.stop_frames = True
        self.wait(500)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.wait(500)
        self.stop_frames = False

    def receive_key(self):
        while True:
            message = ""
            try:

                message = self.socket2.recv_string()
            except:
                pass
            if message.find("m") > -1:
                message = message.split(",")
                self.mouse_x = int(message[1])
                self.mouse_y = int(message[2])
                # print(message)
            elif message.find("j") > -1:
                message = message.split(",")
                self.joy_x = float(message[1])
                self.joy_y = float(message[2])

            else:
                self.last_key = int(message.lstrip())
            try:
                self.socket2.send_string("1")
            except:
                pass
            # print(self.last_key)
            # self.wait(10)
        pass

    def set_camera_high_res(self):
        self.set_camera(30, 1024, 720)

    def set_camera_low_res(self):
        self.set_camera(60, 320, 240)

    def work_f(self):
        self.stop_frames = False
        while True:
            if self.stop_frames == False:
                ret, frame = self.cap.read()
                if ret:
                    self.frame = frame
                    self.time_frame = time.time()
                    # time.sleep(0.001)

                    # self.wait(1)
            else:
                time.sleep(0.01)
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
                    message = None
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

    def send(self, message, flag_wait=False):
        # print("send message")
        message += '\n'
        self.port.write(str(message).encode("utf-8"))
        if flag_wait:
            time.sleep(0.01)
            answer = ""
            while not self.port.in_waiting:
                time.sleep(0.01)
            while self.port.in_waiting:
                answer = answer + str(self.port.readline())
            return answer[:len(answer) - 5]  # remove \r\n

    def move(self, speed, timer=0, wait=False):
        self.send("SPD" + str(speed))
        if wait:
            self.wait(timer)
            self.move(0)

    def servo(self, angle):
        angle = self.constrain(angle, 0, 180)
        return self.send("SER" + str(angle))

    def button(self):
        s = self.send("BUT")
        # print(s)
        return int(s)

    @staticmethod
    def millis():
        return int(round(time.time() * 1000))

    @staticmethod
    def text_to_frame(frame, text, x, y, font_color=(255, 255, 255), font_size=2):
        cv2.putText(frame, str(text), (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, font_color, font_size)
        return frame

    @staticmethod
    def distance_between_points(xa, ya, xb, yb, za=0, zb=0):
        return np.sqrt(np.sum((np.array((xa, ya, za)) - np.array((xb, yb, zb))) ** 2))

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    @staticmethod
    def constrain(a, min, max):
        if a < min:
            return min
        if a > max:
            return max
        return a

    def manual(self, c=-1, show_code=False):
        m = c
        if c == -1:
            m = self.get_key()
        frame = self.get_frame()
        if m != -1:
            print(m)
        if m == 77:  # button1
            if self.manual_regim == 0:
                print("manual on")
                self.manual_regim = 1
            else:
                print("manual off")
                self.manual_regim = 0
        if m == 8:
            if self.small_frame == 1:
                self.small_frame = 0
            else:
                self.small_frame = 1

        if self.manual_regim == 0:
            return self.manual_regim

        if m > -1 and self.manual_regim == 1:

            if m == 87:
                self.move(self.manual_speed, 150, True)
            if m == 83:
                self.move(-self.manual_speed, 150, True)
            if m == 65:
                self.manual_angle -= 10
                self.manual_angle = self.constrain(self.manual_angle, 60, 130)
                print(self.manual_angle)
                self.servo(self.manual_angle)
            if m == 68:
                self.manual_angle += 10
                self.manual_angle = self.constrain(self.manual_angle, 60, 130)
                print(self.manual_angle)
                self.servo(self.manual_angle)
            if m == 32:
                self.manual_angle = 90
                self.servo(self.manual_angle)
            if m == 109:
                self.manual_speed -= 20
                self.manual_speed = self.constrain(self.manual_speed, 0, 255)
                print(self.manual_speed)

            if m == 107:
                self.manual_speed += 20
                self.manual_speed = self.constrain(self.manual_speed, 0, 255)
                print(self.manual_speed)

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

            frame = self.text_to_frame(frame, "manual", 280, 20)
            # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.set_frame(frame)

        return self.manual_regim
