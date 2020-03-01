import zmq
import cv2 as cv
import numpy as np
import threading
import socket
import sys
import os
import errno
import time

class VideoClient:
    __streams = []
    __frames = []
    __context = zmq.Context(1)
    __instance = None
    __udp = []
    __server_address = ('0.0.0.0', 5100)

    def __init__(self):
        th = self.updater(self.update)
        th.daemon = True
        th.start()

    @staticmethod
    def inst():
        if VideoClient.__instance == None:
            VideoClient.__instance = VideoClient()
        return VideoClient.__instance

    def subscribe(self, ipaddress, stream_idx=0):

        addr = ''
        if ipaddress[0] == 't':
            self.__streams.append(self.__context.socket(zmq.SUB))
            addr =  ipaddress + ":500" + str(stream_idx)
        elif ipaddress[0] == 'i':
            self.__streams.append(self.__context.socket(zmq.SUB))
            addr = "ipc:///tmp/zmqfeed/" + str(stream_idx)
        elif ipaddress[0] == 'u':

            addr = ipaddress[6:] + ":510" + str(stream_idx + 1)
            self.__udp.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
            #fcntl.fcntl(self.__udp[-1], fcntl.F_SETFL, os.O_NONBLOCK)
            self.__udp[-1].setblocking(0)
            self_address = ('0.0.0.0', 3101)
            self.__server_address = (ipaddress[6:], 5100)
            self.__udp[-1].bind(self_address)
            self.__frames.append(np.array([[10, 10], [10, 10]], dtype=np.uint8))
            return

        self.__streams[-1].connect(addr)
        self.__streams[-1].subscribe('')
        self.__frames.append(np.array([[10, 10], [10, 10]], dtype=np.uint8))

    def update(self):
        while True:
            time.sleep(.010)
            for i in range(len(self.__streams)):
                msg = None
                try:
                    msg = self.__streams[i].recv(zmq.NOBLOCK, copy=True)
                except (zmq.ZMQError, ) as e:
                    if e.errno == zmq.EAGAIN:
                        pass
                    else:
                        raise e

                if msg is not None:
                    msg = np.frombuffer(msg, dtype=np.uint8)
                    self.__frames[i] = cv.imdecode(msg, flags=1)

            for i in range(len(self.__udp)):
                #server_address = ('0.0.0.0', 5100)
                sent = self.__udp[-1].sendto(bytes(1), self.__server_address)
                data = None
                try:
                    data, addres = self.__udp[-1].recvfrom(500000)
                except (socket.error,) as e:
                    err = e.args[0]
                    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                        continue

                if data:
                    msg = np.frombuffer(data, dtype=np.uint8)
                    self.__frames[i] = cv.imdecode(msg, flags=1)


    class updater(threading.Thread):
        def __init__(self, function):
            threading.Thread.__init__(self)
            self.functor = function

        def run(self):
            self.functor()

    def get_frame(self, stream_idx = 0):
        return self.__frames[stream_idx]

