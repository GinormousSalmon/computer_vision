import json
import os
import socket as sc
import threading
import time
import tkinter.filedialog as tkFileDialog
from tkinter import *

import cv2
import numpy as np
import zmq
import zlib
import base64

import InetConnection

MOUSE_FLAG = False
if MOUSE_FLAG:
    import mouse

ic = InetConnection.InetConnect(sc.gethostname(), "client")
# ic.take_list()
ic_key = InetConnection.InetConnect(sc.gethostname() + "_key", "client")

Reset = "\x1b[0m"
Bright = "\x1b[1m"
Dim = "\x1b[2m"
Underscore = "\x1b[4m"
Blink = "\x1b[5m"
Reverse = "\x1b[7m"
Hidden = "\x1b[8m"

FgBlack = "\x1b[30m"
FgRed = "\x1b[31m"
FgGreen = "\x1b[32m"
FgYellow = "\x1b[33m"
FgBlue = "\x1b[34m"
FgMagenta = "\x1b[35m"
FgCyan = "\x1b[36m"
FgWhite = "\x1b[37m"

BgBlack = "\x1b[40m"
BgRed = "\x1b[41m"
BgGreen = "\x1b[42m"
BgYellow = "\x1b[43m"
BgBlue = "\x1b[44m"
BgMagenta = "\x1b[45m"
BgCyan = "\x1b[46m"
BgWhite = "\x1b[47m"

flag_inet_work = False

port = "5557"

context = zmq.Context()
print(FgBlue + "Start robot API")

list_combobox = []
robot_adres = "-1"
robot_adres_inet = "-1"

# vd = vsc.VideoClient().inst()
# socket.connect ("tcp://192.168.88.19:%s" % port)


selected_file = ""
selected_file_no_dir = ""
video_show = 0
video_show2 = 3
video_show2_global = 0
video_show_work = False
started_flag = 0
recive_flag = 0
key_started = -1
key_pressed = 0
mouse_x = -1
mouse_y = -1


def camera_work():
    global root, video_show2, socket2, video_show2_global, image, started_flag, flag_inet_work
    ic_v = InetConnection.InetConnect(sc.gethostname() + "_v", "client")
    ic_v.connect()
    count_break = 0
    while 1:
        # try:
        # print("s",started_flag)
        if video_show2_global == 1:
            if video_show2 == 1:  # and started_flag == 1:
                # print("vid1", flag_inet_work)
                if flag_inet_work == True:
                    ic_v.send_and_wait_answer(robot_adres_inet, "p")
                    while 1:
                        j_mesg, jpg_bytes = ic_v.take_answer_bytes()
                        if len(jpg_bytes) > 1:
                            try:
                                A = np.frombuffer(jpg_bytes, dtype=j_mesg['dtype'])
                                # arrayname = md['arrayname']sccv2.waitKey(1)

                                # image = A.reshape(j_mesg['shape'])
                                image = A.reshape(j_mesg['shape'])
                                image = cv2.imdecode(image, 1)
                                # print("show window")
                                cv2.imshow("Robot frame", image)
                                cv2.waitKey(1)
                            except:
                                pass

                        else:
                            time.sleep(0.05)
                            break
                    continue
                else:
                    try:
                        socket2.send_string("1", zmq.NOBLOCK)  # zmq.NOBLOCK
                    except zmq.ZMQError as e:
                        if e.errno == zmq.ETERM:
                            # print("error", e)
                            pass
                    md = ""
                    t = time.time()
                    while 1:
                        b = 1
                        try:
                            md = socket2.recv_json(zmq.NOBLOCK)
                            b = 0
                        except zmq.ZMQError as e:
                            if e.errno == zmq.ETERM:
                                pass
                                # print("error", e)
                        count_break += b
                        if md != "":
                            count_break = 0
                            break
                        if time.time() - t > 0.1:
                            # print("break video")
                            break

                    if video_show2 != 1:
                        continue
                    if md == "":
                        continue

                    # if md != None:
                    try:
                        msg = socket2.recv(0)
                        A = np.frombuffer(msg, dtype=md['dtype'])
                        # arrayname = md['arrayname']sccv2.waitKey(1)
                        image = A.reshape(md['shape'])
                        image = cv2.imdecode(image, 1)
                        cv2.imshow("Robot frame", image)
                        cv2.waitKey(1)
                    except:
                        pass

                    if count_break > 1:
                        print("count_break", count_break)
                    continue

            if video_show2 == 0:

                # print("vid0")
                cv2.destroyAllWindows()

                if flag_inet_work == True:
                    video_show2 = 1
                    continue
                # print("Connecting to soft...", robot_adres)
                context = zmq.Context()
                socket2 = context.socket(zmq.REQ)
                socket2.connect("tcp://" + robot_adres + ":5555")

                ic_v.connect()
                video_show2 = 1
                # print("connected")

                continue
            if video_show2 == -1:
                # print("vid-1")
                # print("close socket2")
                cv2.destroyAllWindows()
                if flag_inet_work:
                    video_show2 = 3
                    continue
                socket2.close()
                time.sleep(0.1)
                video_show2 = 3
                ic_v.disconnect()
                time.sleep(0.05)
                # print("video_show2", video_show2 )

                continue
            if video_show2 == 3:
                # print("vid3")
                time.sleep(0.05)
                continue
            # print("vid??", video_show2, "started_flag==", started_flag)
            time.sleep(0.1)
        else:
            cv2.destroyAllWindows()
            video_show2 = 3
            time.sleep(0.1)
            # except:
            #     print("error video")
            #     pass


my_thread = threading.Thread(target=camera_work)
my_thread.daemon = True
my_thread.start()


def robot_receive_work():
    global socket, video_show2, recive_flag, started_flag, flag_inet_work, ic
    color_log = FgBlack
    ic = InetConnection.InetConnect(sc.gethostname() + "_r", "client")
    ic.connect()
    while 1:
        if recive_flag == 1:
            # print("reciv1")
            message_s = ""
            if flag_inet_work == True:
                message_s = ic.send_and_wait_answer(robot_adres_inet, "d")
                pass
            else:
                try:
                    socket.send_string("data")
                    message_s = str(socket.recv_string())
                except:
                    pass
                # while 1:
                #     f=0
                #     try:
                #         socket.send_string("data", zmq.NOBLOCK)  # zmq.NOBLOCK
                #         f=1
                #     except zmq.ZMQError as e:
                #         if e.errno == zmq.ETERM:
                #             #print("error", e)
                #             pass
                #     if f==0:
                #         break
                # message_s = ""
                # t = time.time()
                # while 1:
                #     try:
                #         message_s = socket.recv_string(zmq.NOBLOCK)
                #
                #     except zmq.ZMQError as e:
                #         if e.errno == zmq.ETERM:
                #             pass
                #             #print("error", e)
                #     if message_s != "":
                #         break
                #     if time.time() - t > 0.1:
                #         break
            # print(message_s.encode('utf-8'))
            # message_s=message_s.replace("/n", "")

            if message_s == None:
                time.sleep(0.01)
                continue

            if message_s != "" and len(message_s) > 0:
                # обрезаем конец сообщения, спец символ
                if message_s.find("Traceback") >= 0 or message_s.find("Error:") >= 0:
                    color_log = FgRed

                message_s = message_s.replace("STOPED", FgRed + "STOPED" + Reset)
                print(color_log + message_s.rstrip())

            if message_s.find("STOPE") >= 0 or message_s.find("stoping") >= 0:
                # print("reciv1_stope")
                # message_s = ""
                # video_show2 = -1
                color_log = FgBlack

                # if video_show2 != 3:
                #     video_show2 = -1
                video_show2 = -1
                time.sleep(0.3)
                while video_show2 != 3:
                    print("stop_wideo", video_show2)
                    time.sleep(0.3)
                cv2.destroyAllWindows()

                recive_flag = 0
                time.sleep(0.01)

            time.sleep(0.1)
        if recive_flag == -1:
            # print("reciv-1")
            color_log = FgBlack
            ret = ""
            if flag_inet_work == True:
                ret = ic.send_and_wait_answer(robot_adres_inet, "stop")
                pass
            else:
                try:
                    socket.send_string("stop")
                    ret = socket.recv_string()
                except:
                    pass
            if started_flag == 1:
                print(ret.replace("STOPED", FgRed + "STOPED" + Reset))
            recive_flag = 0
            time.sleep(0.1)

        if recive_flag == 0:
            time.sleep(0.1)


my_thread_print = threading.Thread(target=robot_receive_work)
my_thread_print.daemon = True
my_thread_print.start()


def Video(ev):
    global recive_flag, root, video_show, robot_adres, started_flag, selected_file_no_dir, selected_file, video_show2, video_show2_global
    # video_show2 = 1
    if robot_adres == "-1":
        print(FgRed + "select robot")

        return
    # if selected_file_no_dir == "":
    #     print("select file!")
    #     return
    selected_file_no_dir = "raw.py"
    dir = os.path.abspath(os.curdir).replace("starter", '')
    selected_file = dir + selected_file_no_dir
    # print(dir)

    # send_selected_file()

    Start(ev)

    # socket.send_string("start|" + selected_file_no_dir)
    # res = socket.recv_string()

    started_flag = 1

    video_show2_global = 1
    video_show2 = 0
    recive_flag = 1

    print(BgGreen + "RAW ON" + Reset)


def Video2(ev):
    global root, video_show2, robot_adres, socket2, video_show2_global, video_show_work
    if robot_adres == "-1":
        print(FgRed + "select robot")
        return

    if video_show2_global == 0:
        video_show2_global = 1
        video_show2 = 0

        print(FgYellow + "Video ON")
        # root.after(100, ShowVideo2)
    else:
        video_show2_global = 0
        video_show2 = 0
        # print(video_show_work)
        # while video_show_work == True:
        #     print("wait...")
        #     pass

        print(FgYellow + "Video2 OFF")
        # cv2.destroyAllWindows()
        # socket2.close()


def Quit(ev):
    global root
    root.destroy()


def send_selected_file(show_text=False):
    global selected_file, robot_adres, selected_file_no_dir, socket

    if flag_inet_work == True:
        with open(selected_file, 'rb') as myfile:
            data = myfile.read()
        # print(ic.send_and_wait_answer(robot_adres_inet, "file|" + selected_file_no_dir + "|" + data.decode("utf-8")))
        #        z = zlib.compress(data, 1).decode("utf-8")

        print(ic.send_and_wait_answer(robot_adres_inet, "file|" + selected_file_no_dir + "|" + str(
            base64.b64encode(zlib.compress(data, 1)).decode("utf-8"))))

        return
    # print("sending...", video_show2, recive_flag)
    socket.send_string("file|" + selected_file_no_dir)
    m = socket.recv_string()
    # print()

    with open(selected_file, 'rb') as myfile:
        data = myfile.read()
    # print(data)
    # s1 = fastlz.compress(data)
    # s2 = fastlz.decompress(s1)
    # print(len(data), len(s1), len(s2))

    # data = zlib.compress(data, 1)
    socket.send(data)
    r = socket.recv_string()
    if show_text:
        print(FgBlue + "sended ", selected_file_no_dir)

    pass


def Start(ev):
    global root, robot_adres, video_show2, video_show2_global, started_flag, recive_flag, socket, flag_inet_work

    # video_show2 = 1
    if robot_adres == "-1":
        print(FgRed + "select robot")
        return
    if selected_file_no_dir == "":
        print(FgRed + "select file!" + Reset)
        return

    # print("stop")
    Stop(ev)
    # print("Send script")
    # print("send")
    send_selected_file()

    # textbox.delete('1.0', 'end')

    if flag_inet_work:
        time.sleep(0.5)
        ic.send_and_wait_answer(robot_adres_inet, "start|" + selected_file_no_dir)
        time.sleep(0.5)
        ic.send_and_wait_answer(robot_adres_inet, "startvideo")
        # ic.clear()
    else:
        socket.send_string("start|" + selected_file_no_dir)
        res = socket.recv_string()

    print(FgBlue + "starting..." + FgBlue + selected_file_no_dir)
    # time.sleep(2.5)
    started_flag = 1

    if video_show2_global == 1:
        # print("restart video")
        video_show2 = 0
    recive_flag = 1

    # root.after(10, recive_from_robot)


def Stop(ev):
    global root, video_show2, video_show2_global, started_flag, recive_flag, robot_adres, socket2

    if robot_adres == "-1":
        print(FgRed + "select robot")
        return

    if video_show2 != 3:
        video_show2 = -1

    if flag_inet_work:
        ic.send_and_wait_answer(robot_adres_inet, "stopvideo")
        # print("stop")
        ic.send_and_wait_answer(robot_adres_inet, "stop")
        time.sleep(0.1)
        # while 1:
        #     message_s = ic.take_answer()
        #     print(message_s)
        #     if message_s[2]=='':
        #         break

        ic.clear()

        cv2.destroyAllWindows()

        started_flag = 0
        recive_flag = -1
        time.sleep(0.05)
        cv2.destroyAllWindows()
        return

    # if video_show2_global == 1:
    count = 0
    while video_show2 != 3:
        if count > 20:
            print(BgRed + "break Video Stop" + Reset)
            break
        count += 1
        # print("wait stoped video", video_show2)
        time.sleep(0.05)

    recive_flag = -1
    count = 0
    while recive_flag != 0:
        if count > 100:
            print(BgRed + "break Stop" + Reset)
            break
        count += 1
        time.sleep(0.05)

    # print("stoped, ", video_show2, recive_flag)

    # socket.send_string("stop")
    # # socket2.disable_monitor()
    # print(socket.recv_string())
    started_flag = 0
    time.sleep(0.1)
    cv2.destroyAllWindows()


def LoadFile(ev):
    global selected_file, robot_adres, selected_file_no_dir

    if robot_adres == "-1":
        print(FgRed + "select robot!")
        return
    #
    # my_thread_stop = threading.Thread(target=Stop, args=[(ev,)])
    # my_thread_stop.daemon = True
    # my_thread_stop.start()
    Stop(ev)

    # fn = tkFileDialog.Open(root, filetypes=[('*.py files', '.py')]).show()
    fn = tkFileDialog.askopenfilename(filetypes=[('*.py files', '.py')])
    if fn == '':
        return
    # print("load2")

    selected_file = fn

    s = fn.split("/")
    selected_file_no_dir = s[len(s) - 1]
    # print(s[len(s) - 1])

    # print(selected_file)
    root.title(selected_file)

    Start(ev)
    # send_selected_file(True)

    # textbox.delete('1.0', 'end')
    # textbox.insert('1.0', open(fn, 'rt').read())


# def OptionMenu_SelectionEvent(event):  # I'm not sure on the arguments here, it works though
#     ## do something
#     global robot_adres, socket, recive_flag
#     print(FgBlue,event)
#
#     if event == "none" or robot_adres != "-1":
#         print("return")
#         return
#
#     if event[0] == "scan":
#         ScanRobots(event)
#         return
#     robot_adres = event[1]
#     # socket = context.socket(zmq.REP)
#     socket = context.socket(zmq.REQ)
#     socket.connect("tcp://" + robot_adres + ":%s" % port)
#
#     ip_adress = sc.gethostbyname(sc.gethostname())
#
#     # s = socket.recv_string(zmq.NOBLOCK)
#
#     print("Taking robot..", robot_adres)
#     socket.send_string("take|" + ip_adress)
#     print("Connected to robot: "+BgGreen+socket.recv_string()+Reset)
#     # recive_flag = 1
#
#     connect_keyboard(robot_adres)
#     flag_inet_work = False
#     pass


def OptionMenu_SelectionEvent(event):  # I'm not sure on the arguments here, it works though
    ## do something
    global robot_adres, socket, recive_flag, flag_inet_work, robot_adres_inet
    print(FgBlue, event)

    # if event == "none" or robot_adres != "-1":
    #     print("return")
    #     return

    if event[0] == "scan":
        ScanRobots(event)
        return

    if event[0] == "scan_inet":
        ip_adress_s = sc.gethostbyname(sc.gethostname())
        print(ip_adress_s)
        print("connect to server...")
        ic.connect()
        print("take list")
        list = ic.take_list()
        # print(list)
        # print(ic.take_list())
        # list_combobox_inet = []
        # list_combobox_inet.append(["scan_inet", " "])
        for r in list:
            print(r)
            if r[2] == "robot":
                list_combobox.append(r)

        dropVar = StringVar()
        dropVar.set(list_combobox_inet[0])

        combobox_inet = OptionMenu(panelFrame, dropVar, *(list_combobox), command=OptionMenu_SelectionEvent)
        combobox_inet.place(x=260, y=10, width=150, height=40)  # Позиционируем Combobox на форме
        return

    if event[3] == "l":
        robot_adres = event[1]
        robot_adres_inet = event[0]
        # socket = context.socket(zmq.REP)
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://" + robot_adres + ":%s" % port)

        ip_adress = sc.gethostbyname(sc.gethostname())

        # s = socket.recv_string(zmq.NOBLOCK)

        print("Taking robot..", robot_adres)
        socket.send_string("take|" + ip_adress)
        print("Connected to robot: " + BgGreen + socket.recv_string() + Reset)
        # recive_flag = 1
        flag_inet_work = False

    if event[3] == "i":
        robot_adres_inet = event[0]
        robot_adres = event[0]
        print(robot_adres_inet)
        flag_inet_work = True
        print("Connected to robot: " + BgGreen + event[1] + Reset)
        pass
    connect_keyboard(robot_adres)
    pass


def test(ev):
    # print(ic.send_and_wait_answer(robot_adres_inet,"d"))
    # ic.send_and_wait_answer(robot_adres_inet, "stopvideo|")

    m = ic.send_and_wait_answer(robot_adres_inet, "p")
    print(m)
    time.sleep(0.5)
    j_mesg, jpg_bytes = ic.take_answer_bytes()
    if j_mesg == "-1":
        print("error json")
        return
    print(j_mesg, len(jpg_bytes))
    md = json.loads(j_mesg)
    A = np.frombuffer(jpg_bytes, dtype=md['dtype'])
    # arrayname = md['arrayname']sccv2.waitKey(1)

    image = A.reshape(md['shape'])
    image = cv2.imdecode(image, 1)
    cv2.imshow("Robot frame", image)
    cv2.waitKey(1)
    time.sleep(1)


def ScanRobots(ev):
    global panelFrame, socket, robot_adres, video_show

    ip_adress_s = sc.gethostbyname(sc.gethostname())
    print(ip_adress_s)
    ip_adress = ip_adress_s.split(".")
    ip_adress[0] = "192"
    ip_adress[1] = "168"
    ip_adress[2] = "88"
    if robot_adres != "-1":
        Stop(ev)
        print("drop robot")
        socket = context.socket(zmq.REQ)
        print(robot_adres)
        socket.connect("tcp://" + robot_adres + ":%s" % port)
        print("send", "tcp://" + robot_adres + ":%s" % port)
        socket.send_string("drop")
        print(socket.recv_string())
        robot_adres = "0"
        video_show = 0

    list_combobox = ["none"]
    dropVar = StringVar()
    dropVar.set(list_combobox[0])

    for i in range(20, 30):

        socket = context.socket(zmq.REQ)
        ip_adress_ping = str(ip_adress[0] + "." + ip_adress[1] + "." + ip_adress[2] + "." + str(i))
        # socket.connect("tcp://"+ip_adress[0]+"."+ip_adress[1]+"."+ip_adress[2]+"."+str(i)+":%s" % port)
        socket.connect("tcp://" + ip_adress_ping + ":%s" % port)
        print("ping", ip_adress_ping)
        # print("send")
        socket.send_string("ping")
        time.sleep(0.7)

        s = ""
        try:
            # print("recv...")
            s = socket.recv_string(zmq.NOBLOCK)
            # print("....ok")
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                return  # shutting down, quit
                print("no server")

        data = s.split("|")
        if len(data) > 1:
            s = data[0] + " " + data[1] + " " + str(ip_adress_ping) + "\n"
            if len(s) > 2:
                print(FgMagenta + s + Reset)

            if data[1] == ip_adress_s:
                dropVar.set(ip_adress_ping)
                robot_adres = ip_adress_ping
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://" + robot_adres + ":%s" % port)
                # data[1] = "Connected"
                list_combobox.append(data[1])
                connect_keyboard(robot_adres)
                print(FgBlue + "Connected to robot: " + BgGreen + data[0] + Reset)
                # дальше не ищем
                break

            if data[1] == "0":
                data[1] = ip_adress_ping
                list_combobox.append(data)

    # combobox = OptionMenu(panelFrame, dropVar, *list)
    # combobox.place(x=250, y=10, width=250, height=40)  # Позиционируем Combobox на форме

    # var = StringVar()
    # combobox = OptionMenu(panelFrame, dropVar, *(list), command=OptionMenu_SelectionEvent)
    combobox = OptionMenu(panelFrame, dropVar, *(list_combobox), command=OptionMenu_SelectionEvent)
    combobox.place(x=260, y=10, width=150, height=40)  # Позиционируем Combobox на форме

    # fn = tkFileDialog.SaveAs(root, filetypes=[('*.py files', '.py')]).show()
    # if fn == '':
    #     return
    # if not fn.endswith(".txt"):
    #     fn += ".txt"
    # open(fn, 'wt').write(textbox.get('1.0', 'end'))
    pass


def mouse_move():
    global mouse_x, mouse_y
    x1 = 0
    y1 = 0
    while 1:
        x, y = mouse.get_position()

        if x1 != x or y1 != y:
            # send_event(data)
            x1 = x
            y1 = y
            mouse_x = x
            mouse_y = y
            # print("mouse", x,y)


if MOUSE_FLAG:
    my_thread_mouse = threading.Thread(target=mouse_move)
    my_thread_mouse.daemon = True
    my_thread_mouse.start()


def send_event():
    global socket3, started_flag, ic_key, recive_flag, key_started, key_pressed, mouse_x, mouse_y

    socket3 = context.socket(zmq.REQ)
    while 1:
        if key_started == -1:
            continue

        if key_started == 0:
            if flag_inet_work:
                ic_key.connect()
                # print("start key client")
            else:
                socket3.connect("tcp://" + robot_adres + ":5559")
            key_started = 1
            break

    while 1:
        data = ""
        if key_pressed != 0:
            data = key_pressed
            key_pressed = 0
        else:
            if mouse_x != -1 and mouse_y != -1:
                data = "m," + str(mouse_x) + "," + str(mouse_y)
                mouse_x = -1
                mouse_y = -1

        # print(key_pressed)

        if data != "" and recive_flag == 1:
            if flag_inet_work == True:
                ic_key.send_key(robot_adres_inet, str(data))
            else:

                # socket3.send_string(str(data))

                try:
                    socket3.send_string(str(data), zmq.NOBLOCK)  # zmq.NOBLOCK
                except zmq.ZMQError as e:
                    if e.errno == zmq.ETERM:
                        print("error", e)
                        continue

                message = ""
                count = 0
                while 1:
                    count += 1
                    try:
                        # print("s1")
                        # socket2.send_string("p", zmq.NOBLOCK)
                        message = socket3.recv_string(zmq.NOBLOCK)
                        # print("....ok")
                    except zmq.ZMQError as e:
                        if e.errno == zmq.ETERM:
                            print("error", e)
                    if len(message) > 0:
                        break
                    if count > 50:
                        # print(BgRed + "reconnect key" + Reset)
                        socket3.close()
                        socket3 = context.socket(zmq.REQ)
                        socket3.connect("tcp://" + robot_adres + ":5559")

                        break
                    time.sleep(0.01)
                    # if recive_flag != 1:
                    #     break


my_thread_key = threading.Thread(target=send_event)
my_thread_key.daemon = True
my_thread_key.start()


def connect_keyboard(robot_adres):
    global socket3, flag_inet_work, ic_key, key_started
    key_started = 0
    pass


def keydown(e):
    global socket3, started_flag, ic_key, recive_flag, key_pressed
    # if started_flag == 0:
    #     if e.keycode == 13:
    #         Start(e)
    #     return
    key_pressed = e.keycode

    # if flag_inet_work == True:
    #     ic_key.send_key(robot_adres_inet, str(e.keycode))
    # else:
    #     #socket3.send_string(str(e.keycode), zmq.NOBLOCK)
    #     socket3.send_string(str(e.keycode))
    #
    #     #s = socket3.recv_string()
    #     message=""
    #     while 1:
    #         try:
    #             # print("s1")
    #             # socket2.send_string("p", zmq.NOBLOCK)
    #             message = socket3.recv_string(zmq.NOBLOCK)
    #             # print("....ok")
    #         except zmq.ZMQError as e:
    #             if e.errno == zmq.ETERM:
    #                 print("error", e)
    #         if len(message) > 0:
    #             break
    #         if recive_flag != 1:
    #             break


root = Tk()
root.title('RoboStarter')
root.geometry('420x100+900+10')  # ширина=500, высота=400, x=300, y=200
root.resizable(True, True)  # размер окна может быть изменён только по горизонтали

root.bind("<KeyPress>", keydown)

panelFrame = Frame(root, height=260, bg='gray')
textFrame = Frame(root, height=200, width=500)

panelFrame.pack(side='top', fill='x')
textFrame.pack(side='bottom', fill='both', expand=1)

textbox = Text(textFrame, font='Arial 10', wrap='word')
scrollbar = Scrollbar(textFrame)

scrollbar['command'] = textbox.yview
textbox['yscrollcommand'] = scrollbar.set

textbox.pack(side='left', fill='both', expand=1)
scrollbar.pack(side='right', fill='y')

loadBtn = Button(panelFrame, text='Load\nStart')
# saveBtn = Button(panelFrame, text='Scan')
startBtn = Button(panelFrame, text='Start')
stopBtn = Button(panelFrame, text='Stop')
videoBtn = Button(panelFrame, text='Raw')
videoBtn2 = Button(panelFrame, text='Video')
# testBtn = Button(panelFrame, text='test')

loadBtn.bind("<Button-1>", LoadFile)
# saveBtn.bind("<Button-1>", ScanRobots)
startBtn.bind("<Button-1>", Start)
stopBtn.bind("<Button-1>", Stop)
videoBtn.bind("<Button-1>", Video)
videoBtn2.bind("<Button-1>", Video2)
# testBtn.bind("<Button-1>", test)

loadBtn.place(x=10, y=10, width=40, height=40)
# saveBtn.place(x=10, y=10, width=40, height=40)
startBtn.place(x=60, y=10, width=40, height=40)
stopBtn.place(x=110, y=10, width=40, height=40)
videoBtn.place(x=160, y=10, width=40, height=40)
videoBtn2.place(x=210, y=10, width=40, height=40)

# testBtn.place(x=10, y=60, width=40, height=40)
# root.after(10, recive_from_robot)
#
list_combobox = []

list_combobox_inet = []
dropVar = StringVar()
dropVar.set("Connect to robot")
dropVar_inet = StringVar()
dropVar_inet.set("Connect to robot")
list_combobox.append(["0", "192.168.88.20", "robot", "l"])
list_combobox.append(["1", "192.168.88.21", "robot", "l"])
list_combobox.append(["2", "192.168.88.22", "robot", "l"])
list_combobox.append(["3", "192.168.88.23", "robot", "l"])
list_combobox.append(["4", "192.168.88.24", "robot", "l"])
list_combobox.append(["5", "192.168.88.25", "robot", "l"])
list_combobox.append(["6", "192.168.88.26", "robot", "l"])
list_combobox.append(["7", "192.168.88.27", "robot", "l"])
list_combobox.append(["8", "192.168.88.28", "robot", "l"])
list_combobox.append(["9", "192.168.88.29", "robot", "l"])
# list_combobox.append(["0_eth","192.168.88.30", "robot", "l"])
# list_combobox.append(["1_eth","192.168.88.31", "robot", "l"])
# list_combobox.append(["2_eth","192.168.88.32", "robot", "l"])
list_combobox.append(["3_eth", "192.168.88.33", "robot", "l"])
# list_combobox.append(["4_eth","192.168.88.34", "robot", "l"])
# list_combobox.append(["5_eth","192.168.88.35", "robot", "l"])
# list_combobox.append(["6_eth","192.168.88.36", "robot", "l"])
list_combobox.append(["scan", " "])
list_combobox.append(["scan_inet", " "])
list_combobox_inet.append(["scan_inet", " "])

combobox = OptionMenu(panelFrame, dropVar, *(list_combobox), command=OptionMenu_SelectionEvent)
combobox.place(x=260, y=10, width=150, height=40)  # Позиционируем Combobox на форме

# combobox_inet = OptionMenu(panelFrame, dropVar_inet, *(list_combobox_inet), command=OptionMenu_SelectionEvent_inet)
# combobox_inet.place(x=260, y=60, width=150, height=40)  # Позиционируем Combobox на форме


root.mainloop()
