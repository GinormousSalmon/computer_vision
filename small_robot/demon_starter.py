import asyncio
import json
import os
import pty
import socket
import time
from threading import Thread
import fcntl
import numpy as np
import zmq
import zlib
import base64

import InetConnection

# 18.05.2018
myhost = os.uname()[1]

master_ip = "0"
OFLAGS = None

os.system('sudo modprobe bcm2835-v4l2')


def set_nonblocking(file_handle):
    """Make a file_handle non-blocking."""
    global OFLAGS
    OFLAGS = fcntl.fcntl(file_handle, fcntl.F_GETFL)
    nflags = OFLAGS | os.O_NONBLOCK
    fcntl.fcntl(file_handle, fcntl.F_SETFL, nflags)


master, slave = pty.openpty()
set_nonblocking(master)

port = "5557"

context = zmq.Context(1)
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % port)
flag_stop = False
console_out = ""
proc = False
filename = ""
# raspberry
dir = "/home/pi/robot/"
# orange
# dir = "/root/robot/"

if myhost.find("ras") == 0:
    dir = "/home/pi/robot/"
else:
    dir = "/root/robot/"

frame_byte = np.array([[10, 10], [10, 10]], dtype=np.uint8)
frame_json = ""
flag_stopt_video = False
keypress = ""
flag_video_demon_work = False

pass_hash = ""
try:
    file = open(dir+"password", "r+")
    pass_hash = file.readline()
    file.close()
except:
    pass
print("pass hash (", pass_hash, ")")


def key_to_robot():
    global keypress, flag_stopt_key
    # видео клиент. берет кадры с запущенного робота

    # while 1:
    #     if proc:
    #         break

    context_key = zmq.Context(1)
    socket_key = context_key.socket(zmq.REQ)
    socket_key.connect("tcp://127.0.0.1:5559")
    flag_stopt_key = False
    print("START KEY DEMON")
    while 1:
        try:

            if flag_stopt_key == True:
                flag_stopt_video = False
                print("STOP KEY DEMON")
                break
            if keypress != "":
                try:
                    socket_key.send_string(keypress)
                    m = socket_key.recv_string(0)
                    keypress = ""
                except:
                    pass
            else:
                time.sleep(0.07)
        except:
            pass


def video_from_robot():
    global frame_byte, frame_json, flag_stopt_video, flag_video_demon_work
    # видео клиент. берет кадры с запущенного робота

    # while 1:
    #     if proc:
    #         break

    context_video = zmq.Context(1)
    socket_video = context_video.socket(zmq.REQ)
    socket_video.connect("tcp://127.0.0.1:5555")
    flag_stopt_video = False
    flag_video_demon_work = True
    print("START VIDEO DEMON")
    while 1:

        try:
            if flag_stopt_video == True:
                flag_stopt_video = False
                print("STOP VIDEO DEMON")
                break

            try:
                socket_video.send_string("1", zmq.NOBLOCK)
                frame_json = socket_video.recv_json(0)
                if frame_json != None:
                    frame_byte = socket_video.recv(0)
            except:
                pass
            time.sleep(0.001)
        except:
            pass


def inet_work():
    global socket, filename, proc, myhost, frame_byte, frame_json, flag_stopt_video, keypress, flag_video_demon_work
    print("Start Inet Work")
    ic = InetConnection.InetConnect(myhost, "robot")
    ic.connect()

    # клиент к демону
    context_inet = zmq.Context(1)
    socket_inet = context_inet.socket(zmq.REQ)
    socket_inet.connect("tcp://127.0.0.1:%s" % port)

    pause = 0.01
    while 1:
        answer = ic.take_answer()
        # print("in", answer, time.time())
        # time.sleep(0.1)
        if len(answer) == 0:
            time.sleep(0.01)
            continue

        if int(answer[0]) > -1:
            # print("Start file from inet", answer)
            # пришел запрос, надо ответить
            if len(answer) < 2:
                time.sleep(0.01)
                continue

            message = answer[1].split("|")
            if message[0]=="":
                continue
            if pass_hash != "":
                if pass_hash != message[-1]:
                    print("wrong pass", answer)
                    ic.send_to(answer[0], "WRONG PASSWORD")
                    #time.sleep(1)
                    continue

            print("inet_message", message)

            if message[0] == "start":
                print("Start", message[1])
                # посылаем данные консоли
                filename = message[1]
                try:
                    socket_inet.send_string("start|" + filename)
                    answ = socket_inet.recv_string()
                    ic.send_to(answer[0], answ)
                except:
                    pass
                continue

            if message[0] == "stop":
                print("Stop")
                # посылаем данные консоли
                try:
                    socket_inet.send_string("stop")
                    answ = socket_inet.recv_string()
                    print(answ)
                    ic.send_to(answer[0], answ)
                except:
                    pass
                continue

            if message[0] == "d":
                # print("Data inet")
                # посылаем данные консоли

                socket_inet.send_string("data")
                answ = socket_inet.recv_string()
                # print(answ)
                if answ != "":
                    ic.send_to(answer[0], answ)
                continue

            if message[0] == "file":
                print("File inet size", len(message[2]))
                # посылаем данные консоли
                try:
                    socket_inet.send_string("file|" + message[1])
                    answ = socket_inet.recv_string()
                    # socket_inet.send(message[2].encode('utf-8'))
                    try:
                        socket_inet.send(zlib.compress(zlib.decompress(base64.b64decode(message[2]))), 1)
                    except:
                        print("error compress inet")
                        pass

                    answ = socket_inet.recv_string()
                    print("anser inet file", answ)
                    print(answ)
                    ic.send_to(answer[0], message[1])
                except:
                    pass
                continue

            if message[0] == "p":
                if flag_video_demon_work == False:
                    my_thread_video = Thread(target=video_from_robot)
                    my_thread_video.daemon = True
                    my_thread_video.start()

                print("frame inet")
                # забираем кадр
                print(frame_json)
                # convert to string
                frame_json_str = json.dumps(frame_json)
                # load to dict
                # my_dict = json.loads(input)
                # ic.send_to(answer[0], "1")
                print("send bytes")
                ic.send_bytes_to(answer[0], frame_json_str, frame_byte)
                continue
            if message[0] == "startvideo":
                print("Start video")
                # посылаем данные консоли
                my_thread_video = Thread(target=video_from_robot)
                my_thread_video.daemon = True
                my_thread_video.start()

                ic.send_to(answer[0], "1")
                continue
            if message[0] == "stopvideo":
                print("Stop video")
                # посылаем данные консоли
                flag_stopt_video = True
                ic.send_to(answer[0], "1")
                continue

            if message[0] == "k":
                print("Send keqy")
                try:
                    keypress = message[1]
                except:
                    pass
                # посылаем данные консоли
                # ic.send_to(answer[0], "1")
                continue
            if message[0] == "pause":
                print("Send keqy")
                pause = float(message[1])
                # посылаем данные консоли
                # ic.send_to(answer[0], "1")
                continue

            if message[0] == "0" or message[0] == 0:
                time.sleep(0.01)

                continue

            # ic.send_to(answer[0], "wrong_packet")

        if int(answer[0]) == -1:
            print("registration")
            ic.registration()

        time.sleep(pause)
        pass


def test_wifi():
    import subprocess

    count_fail = 0
    time.sleep(180)
    while 1:

        try:
            subprocess.call(['/home/pi/robot/wifi_reconnect.sh'])
        except:
            pass

        # test connection and reset
        wifi_ip = subprocess.check_output(['hostname', '-I'])
        if wifi_ip is not None:
            # print(wifi_ip)
            count_fail = 0
        else:
            count_fail += 1

        if count_fail > 10:
            os.system('sudo shutdown -r now')
        time.sleep(30)



async def main():
    global console_out, proc, master_ip, filename
    my_thread_inet = Thread(target=inet_work)
    my_thread_inet.daemon = True
    my_thread_inet.start()

    my_thread_video = Thread(target=key_to_robot)
    my_thread_video.daemon = True
    my_thread_video.start()

    my_thread_video = Thread(target=test_wifi)
    my_thread_video.daemon = True
    my_thread_video.start()

    filename = "/autostart.py"
    print("Autostart file", filename)
    asyncio.ensure_future(run_subprocess())
    await asyncio.sleep(0.001)

    # process = asyncio.create_subprocess_exec(*["python3", "print1.py"], stdout=slave)
    #            print("start", process.returncode)

    flag_file = False
    # filename = ""
    print("Start demon")
    while True:
        #  Wait for next request from client
        if flag_file:
            # print("wait file data")
            t = time.time()
            message = ""
            while 1:
                try:
                    message = socket.recv()
                except:
                    pass
                if message != "":
                    break
                if time.time() - t > 5:
                    break

            # message = message.decode("utf-8")

            print("filename", filename)
            # print("file", message)
            # message = zlib.decompress(message)

            flag_file = False
            if message == "":
                print("bad file")
                continue

            text_file = open(dir + filename, "wb")
            try:
                text_file.write(zlib.decompress(message))
            except:
                print("error compress")
                pass
            text_file.close()
            try:
                socket.send_string("ok")
            except:
                pass
            continue

        message = ""
        try:
            message = socket.recv_string(zmq.NOBLOCK)
        except:
            pass

        # if len(message)>0:
        #    print("Received request: %s" % message)
        await asyncio.sleep(0.001)
        if message == "":
            time.sleep(0.01)
            # print("message empty")
            continue
        # time.sleep(0.001)
        print("message", message)
        message = message.split("|")

        if message[0].find("data") >= 0:
            snd = "STOPED "
            if proc:
                if len(console_out) == 0:
                    if proc.returncode == None:
                        # print(console_out)
                        asyncio.ensure_future(run_subprocess_read())
                        # print(console_out)
                        snd = console_out

            if len(console_out) > 0:
                snd = console_out
                # print(len(console_out))
                # if len(console_out) < 1024:
                #    await asyncio.sleep(0.1)
            # print("send: "+snd)
            try:
                socket.send_string(snd)
            except:
                pass
            console_out = ""
            continue

        if message[0].find("stop") >= 0:
            # print("stop")

            if proc:
                if proc.returncode == None:
                    # print("k1", proc.returncode)
                    asyncio.ensure_future(run_subprocess_read())
                    proc.kill()
                    # await asyncio.sleep(2)
                    while proc:
                        await asyncio.sleep(0.01)
                    # print("k2",proc.returncode)

            console_out_summ = ""

            # while len(console_out)>0:
            #     print("len", len(console_out))
            #     console_out_summ+=console_out
            #     print(console_out)
            #     console_out=""
            #     time.sleep(0.001)
            #
            try:
                socket.send_string(console_out + "STOPED ")
            except:
                pass
            console_out = ""

            proc = False
            print("stoping", console_out)
            continue
            # break
        if message[0].find("ping") >= 0:
            try:
                socket.send_string(myhost + "|" + master_ip)
            except:
                pass
            continue

        if message[0].find("take") >= 0:
            # назначаем хозяина
            master_ip = message[1]
            print("take", master_ip)
            try:
                socket.send_string(myhost + "|" + master_ip)
            except:
                pass
            continue

        if message[0].find("drop") >= 0:
            # скидываем хозяина]
            master_ip = "0"
            print("drop", master_ip)
            try:
                socket.send_string(myhost + "|" + master_ip)
            except:
                pass
            continue

        if message[0].find("file") >= 0:
            # принимаем файл
            print("filename", filename)

            filename = message[1]

            try:
                socket.send_string("ok")
            except:
                pass
            # await asyncio.sleep(0.01)
            flag_file = True
            # print("zagolovok prinat")
            continue

        if message[0].find("start") >= 0:
            #            flag_stop = False

            filename = message[1]
            print("start file", filename)
            if proc == False:
                asyncio.ensure_future(run_subprocess())
                print("start ok")
                try:
                    socket.send_string("start ok")
                except:
                    pass
            else:
                print("already run")
                try:
                    socket.send_string("already run")
                except:
                    pass
            #            process = asyncio.create_subprocess_exec(*["python3", "print1.py"], stdout=slave)
            #            print("start", process.returncode)
            continue

        if message[0].find("exit") >= 0:
            print("exit")
            break


async def run_subprocess_read():
    global proc, console_out
    if proc:
        if proc.returncode == None:
            # s = stdout.readline()
            # print("read..")
            s = ""
            try:
                # return 1-n bytes or exception if no bytes
                # s = str(os.read(master, 1024))
                # s = str(os.read(master, 1024).decode("utf-8"))
                s = str(os.read(master, 4096).decode("utf-8"))

            except BlockingIOError:
                # sys.stdout.write('no data read\r')
                #   print("block")
                pass

            # print("..ok")
            # if s.find("EXIT")>=0:
            #     print("end of programm")
            #     proc=False
            console_out += s
            return s


async def run_subprocess():
    global proc, slave, console_out, filename
    print('Starting subprocess', dir + filename)
    proc = await asyncio.create_subprocess_exec(
        # 'python3', 'print1.py', stdout=slave, stderr=slave)
        'python3', dir + filename, stdout=slave, stderr=slave)
    # 'python3', 'robot_keras2.py', stdout = slave, stderr = slave)
    # 'python3', 'manual_client.py', stdout = slave, stderr = slave)
    # 'python3', 'robot_keras.py', stdout=slave, stderr=slave)

    # 'python3', 'print1.py', stdout=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    try:
        console_out += str(os.read(master, 4096).decode("utf-8"))
    except BlockingIOError:
        pass

    proc = False
    print("END proc")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()  # prevents annoying signal handler error
