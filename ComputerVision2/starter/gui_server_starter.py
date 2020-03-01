from tkinter import *
import tkinter.filedialog as tkFileDialog

import zmq
import time
import cv2
import numpy as np

import socket as sc

from ComputerVision2.Examples import VideoServiceClient as vsc

# import fastlz

port = "5557"

context = zmq.Context()
print("Start robot API")
list_combobox = []
robot_adres = "0"

# vd = vsc.VideoClient().inst()
# socket.connect ("tcp://192.168.88.19:%s" % port)


selected_file = ""
selected_file_no_dir = ""
video_show = 0
video_show2 = 0
video_show2_global = 0
video_show_work = False
started = 0


def Video(ev):
    global root, video_show, robot_adres
    if robot_adres == "0":
        print("select robot")
        return

    print(video_show)
    if video_show == 0:
        print("connect to video demon", robot_adres)
        # vsc.VideoClient.inst().subscribe("udp://"+robot_adres, 0)

        vsc.VideoClient.inst().subscribe("tcp://" + robot_adres, 0)
        # vd = vsc.VideoClient.inst()
        # vd.subscribe("tcp://" + robot_adres, 0)
        root.after(10, ShowVideo)
        video_show = 1
    else:
        if video_show == -1:
            video_show = 1
            root.after(10, ShowVideo)
        else:
            video_show = -1

    pass


def ShowVideo():
    global root, video_show
    if video_show == 1:
        frame = vsc.VideoClient.inst().get_frame()
        # frame = vd.get_frame()
        # frame = cv2.flip(frame, -1)
        cv2.imshow("robot", frame)
        if cv2.waitKey(1) == 32:
            print("svreenshot")
            cv2.imwrite("screen.jpg", frame)

        # image = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_CUBIC)
        root.after(1, ShowVideo)
    pass


def Video2(ev):
    global root, video_show2, robot_adres, socket2, video_show2_global, video_show_work
    if robot_adres == "0":
        print("select robot")
        return

    if video_show2_global == 0:
        video_show2_global = 1
        video_show2 = 0

        print("Video2 ON")
        root.after(100, ShowVideo2)
    else:
        video_show2_global = 0
        video_show2 = 0
        print(video_show_work)
        while video_show_work == True:
            print("wait...")
            pass

        print("Video2 OFF")

        socket2.close()


def ShowVideo2():
    global root, video_show2, socket2, video_show2_global
    if video_show2_global == 1:

        if video_show2 == 1:
            # print("try take frame")
            message = ""
            # socket2.send_string("p")
            # message = socket2.recv_string()
            try:
                # print("s1")
                socket2.send_string("p", zmq.NOBLOCK)
                # print("....ok")
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    print("no server1")
                    video_show_work = False
                    return  # shutting down, quit
            # print("recev")
            # time.sleep(0.03)
            try:
                # print("recv...")
                message = socket2.recv_string(zmq.NOBLOCK)
                # print("....ok")
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    print("no server2")
                    video_show_work = False
                    return  # shutting down, quit
            # print("s",message)
            # time.sleep(0.01)
            # print("recev ok")
            if message != None:
                if message == "ok":
                    try:
                        socket2.send_string("1")
                        md = socket2.recv_json(0)
                        msg = socket2.recv(0)

                        A = np.frombuffer(msg, dtype=md['dtype'])

                        arrayname = md['arrayname']
                        image = A.reshape(md['shape'])
                        # print "Received Array Named: ", arrayname
                        # print "Array size: ", image.shape
                        # image = cv2.flip(image, 0)
                        image = cv2.imdecode(image, 1)

                        # image = cv2.flip(image, -1)

                        # image = cv2.resize(image, (640, 480), interpolation=cv2.INTER_CUBIC)
                        # print("show frame")
                        # cv2.imshow(arrayname, image)
                        cv2.imshow("Robot frame", image)
                        # time.sleep(0.01)
                    except:
                        print("error take image")
                        pass

            # image = cv2.resize(frame, (320, 240), interpolation=cv2.INTER_CUBIC)

        if video_show2 == 0:
            print("Connecting to soft...", robot_adres)
            socket2 = context.socket(zmq.REQ)
            # socket.connect ("tcp://localhost:%s" % port)
            socket2.connect("tcp://" + robot_adres + ":5555")

            video_show2 = 1
            print("connected")

        root.after(10, ShowVideo2)


def recive_from_robot():
    global socket, video_show2
    socket.send_string("data")
    message_s = str(socket.recv_string())
    if message_s != "" or len(message_s) != 0:
        # обрезаем конец сообщения, спец символ
        print(str(message_s[:len(message_s) - 1]))
    if message_s.find("STOPED") < 0:
        root.after(100, recive_from_robot)
    else:
        message_s = ""
        video_show2 = -1
        textbox.insert(END, message_s)


def Quit(ev):
    global root
    root.destroy()


def send_selected_file():
    global selected_file, robot_adres, selected_file_no_dir

    socket.send_string("file|" + selected_file_no_dir)
    m = socket.recv_string()
    # print()
    # print("sending...")
    with open(selected_file, 'rb') as myfile:
        data = myfile.read()
    # print(data)
    # s1 = fastlz.compress(data)
    # s2 = fastlz.decompress(s1)
    # print(len(data), len(s1), len(s2))
    socket.send(data)
    r = socket.recv_string()
    # print()

    pass


def Start(ev):
    global root, robot_adres, video_show2, video_show2_global, started
    # video_show2 = 1
    if robot_adres == "0":
        print("select robot")
        return
    if selected_file_no_dir == "":
        print("select file!")
        return

    Stop(ev)
    # print("Send script")
    send_selected_file()

    textbox.delete('1.0', 'end')
    print("Start script")
    socket.send_string("start|" + selected_file_no_dir)
    res = socket.recv_string()

    started = 1

    if video_show2_global == 1:
        print("restart video")
        video_show2 = 0

        root.after(1000, ShowVideo2)

    root.after(10, recive_from_robot)


def Stop(ev):
    global root, video_show2, video_show2_global, started

    if video_show2_global == 1:
        video_show2 = -1
        # socket2.close()
    socket.send_string("stop")
    # socket2.disable_monitor()
    print(socket.recv_string())
    started = 0


def LoadFile(ev):
    global selected_file, robot_adres, selected_file_no_dir

    if robot_adres == "0":
        print("select robot!")
        return

    fn = tkFileDialog.Open(root, filetypes=[('*.py files', '.py')]).show()
    if fn == '':
        return
    selected_file = fn

    s = fn.split("/")
    selected_file_no_dir = s[len(s) - 1]
    print(s[len(s) - 1])

    print(selected_file)
    root.title(selected_file)

    Stop(ev)
    send_selected_file()

    # textbox.delete('1.0', 'end')
    # textbox.insert('1.0', open(fn, 'rt').read())


def connect_keyboard(robot_adres):
    global socket3
    socket3 = context.socket(zmq.REQ)
    socket3.connect("tcp://" + robot_adres + ":5559")
    # print("connect keyboard server")

    pass


def OptionMenu_SelectionEvent(event):  # I'm not sure on the arguments here, it works though
    ## do something
    global robot_adres, socket
    print(event)

    if event == "none" or robot_adres != "0":
        print("return")
        return
    robot_adres = event[1]
    # socket = context.socket(zmq.REP)
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://" + robot_adres + ":%s" % port)
    ip_adress = sc.gethostbyname(sc.gethostname())

    # s = socket.recv_string(zmq.NOBLOCK)

    print("Take robot..", robot_adres)
    socket.send_string("take|" + ip_adress)
    print(socket.recv_string())

    connect_keyboard(robot_adres)
    pass


def ScanRobots(ev):
    global panelFrame, socket, robot_adres, video_show

    ip_adress_s = sc.gethostbyname(sc.gethostname())
    print(ip_adress_s)
    ip_adress = ip_adress_s.split(".")
    ip_adress[0] = "192"
    ip_adress[1] = "168"
    ip_adress[2] = "88"
    if robot_adres != "0":
        Stop(ev)
        print("drop robot")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://" + robot_adres + ":%s" % port)
        print("send", "tcp://" + robot_adres + ":%s" % port)
        socket.send_string("drop")
        print(socket.recv_string())
        robot_adres = "0"
        video_show = 0

    list_combobox = ["none"]
    dropVar = StringVar()
    dropVar.set(list_combobox[0])

    for i in range(20, 27):

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
            print(s)
            print(data[0])

            if data[1] == ip_adress_s:
                dropVar.set(data[0] + " " + ip_adress_ping + " Connected")
                robot_adres = ip_adress_ping
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://" + robot_adres + ":%s" % port)
                data[1] = "Connected"
                list_combobox.append(data)
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
    combobox.place(x=310, y=10, width=250, height=40)  # Позиционируем Combobox на форме

    # fn = tkFileDialog.SaveAs(root, filetypes=[('*.py files', '.py')]).show()
    # if fn == '':
    #     return
    # if not fn.endswith(".txt"):
    #     fn += ".txt"
    # open(fn, 'wt').write(textbox.get('1.0', 'end'))
    pass


def keydown(e):
    global socket3, started
    if started == 0:
        return
    socket3.send_string(str(e.keycode))
    # print("send")
    s = socket3.recv_string()


root = Tk()
root.title('RoboStarter')
root.geometry('500x500+900+10')  # ширина=500, высота=400, x=300, y=200
root.resizable(True, True)  # размер окна может быть изменён только по горизонтали

root.bind("<KeyPress>", keydown)

panelFrame = Frame(root, height=60, bg='gray')
textFrame = Frame(root, height=340, width=600)

panelFrame.pack(side='top', fill='x')
textFrame.pack(side='bottom', fill='both', expand=1)

textbox = Text(textFrame, font='Arial 10', wrap='word')
scrollbar = Scrollbar(textFrame)

scrollbar['command'] = textbox.yview
textbox['yscrollcommand'] = scrollbar.set

textbox.pack(side='left', fill='both', expand=1)
scrollbar.pack(side='right', fill='y')

loadBtn = Button(panelFrame, text='File')
saveBtn = Button(panelFrame, text='Scan')
startBtn = Button(panelFrame, text='Start')
stopBtn = Button(panelFrame, text='Stop')
videoBtn = Button(panelFrame, text='Video\nraw')
videoBtn2 = Button(panelFrame, text='Video2')

loadBtn.bind("<Button-1>", LoadFile)
saveBtn.bind("<Button-1>", ScanRobots)
startBtn.bind("<Button-1>", Start)
stopBtn.bind("<Button-1>", Stop)
videoBtn.bind("<Button-1>", Video)
videoBtn2.bind("<Button-1>", Video2)

loadBtn.place(x=60, y=10, width=40, height=40)
saveBtn.place(x=10, y=10, width=40, height=40)
startBtn.place(x=110, y=10, width=40, height=40)
stopBtn.place(x=160, y=10, width=40, height=40)
videoBtn.place(x=210, y=10, width=40, height=40)
videoBtn2.place(x=260, y=10, width=40, height=40)

# root.after(10, recive_from_robot)
#
list_combobox = ["none"]
dropVar = StringVar()
dropVar.set("---")
list_combobox.append(["0", "192.168.88.20"])
list_combobox.append(["1", "192.168.88.21"])
list_combobox.append(["2", "192.168.88.22"])
list_combobox.append(["3", "192.168.88.23"])
list_combobox.append(["4", "192.168.88.24"])
list_combobox.append(["5", "192.168.88.25"])
list_combobox.append(["6", "192.168.88.26"])
list_combobox.append(["0_eth", "192.168.88.30"])
list_combobox.append(["1_eth", "192.168.88.31"])
list_combobox.append(["2_eth", "192.168.88.32"])
list_combobox.append(["3_eth", "192.168.88.33"])
list_combobox.append(["4_eth", "192.168.88.34"])
list_combobox.append(["5_eth", "192.168.88.35"])
list_combobox.append(["6_eth", "192.168.88.36"])
combobox = OptionMenu(panelFrame, dropVar, *(list_combobox), command=OptionMenu_SelectionEvent)
combobox.place(x=310, y=10, width=250, height=40)  # Позиционируем Combobox на форме

root.mainloop()
