
import zmq
import time
import threading



class InetConnect:
    def __init__(self, name, type):
        self.name = name
        self.type = type


        self.id="-1"
        self.time_count=time.time()

        #self.socket = self.context.socket(zmq.PAIR)

        #self.socket.connect("tcp://localhost:7777")

        self.list_wait=[]
        self.connected=False
        self.count_disconnected=0
        # self.my_thread = threading.Thread(target=self.sender)
        # self.my_thread.daemon = True
        #self.my_thread.start()

    def sender(self):
        while 1:
            if self.id=="-1":
                time.sleep(0.5)
                continue

            if time.time() - self.time_count>3:
                self.connected = False
                print("close socket")
                time.sleep(3)
                self.socket.close()
                self.context.term()
                print("close socket")
                self.id="-1"

                time.sleep(1)
                self.context = zmq.Context()
                self.socket = self.context.socket(zmq.REQ)
                self.socket.connect("tcp://95.154.96.240:7777")
                self.connected = True
                self.time_count = time.time()

                # self.wait_my_query()
            # try:
            #     self.socket.send_string("t~" + self.id + "~", zmq.NOBLOCK)
            #     self.socket.recv_string( zmq.NOBLOCK)
            # except:
            #     pass
            # self.exit_query()
            # time.sleep(0.5)

    # def send_non_block(self, message):
    #     while 1:
    #         f=0
    #         try:
    #             print("try send")
    #             self.socket.send_string(message,zmq.NOBLOCK)
    #             f=1
    #         except:
    #             pass
    #         if f==1:
    #             break

    def clear(self):
        if self.connected == False:
            return
        self.wait_my_query()
        m=""
        try:
            self.socket.send_string("clear~" + self.id + "~")
            #self.send_non_block("clear~" + self.id + "~")
            m = self.socket.recv_string()
        except:
            pass
        self.exit_query()
        #print("clear", m)
        return m

    def try_connect(self):
        #print("connect try..", self.name, self.type)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://95.154.96.240:7777")
        self.connected = True
        #print("connect OK!")
        self.clear()
        self.registration()

    def connect(self):
        if self.connected==False:
            self.my_thread = threading.Thread(target=self.try_connect)
            self.my_thread.daemon = True
            self.my_thread.start()


    def disconnect(self):
        if self.connected == True:
            self.socket.close()
            self.connected = False

    def wait_my_query(self):
        self.time_count = time.time()
        id = time.time()
        #print(id)
        self.list_wait.append(id)
        while 1:
            if self.list_wait[0]==id:
                time.sleep(0.01)
                return True
            #time.sleep(0.00)
        self.time_count = time.time()

    def exit_query(self):
        self.list_wait.pop(0)
        self.time_count = time.time()

    def registration(self):

        self.wait_my_query()
        try:
            self.socket.send_string("i~"+self.name+"~"+self.type+"~")
            self.id = str(self.socket.recv_string())
        except:
            pass
        self.exit_query()
        #print("registration id",self.id)


    def take_list(self):
        self.wait_my_query()
        try:
            self.socket.send_string("l~" + self.id)
            message = str(self.socket.recv_string())
        except:
            pass
        self.exit_query()
        list = []
        m = message.split("~")

        for s in m:
            data = s.split(",")
            if len(data)>1:
                data[3]="i"
                list.append(data)
        #print(list)
        return  list

    def send_to(self, to_id, text):

        self.wait_my_query()
        message=""
        try:
            self.socket.send_string("s~"+self.id +"~" +str(to_id)+"~"+text)
            message = str(self.socket.recv_string())
        except:
            pass
        self.exit_query()
        return  message


    def take_answer(self):
        if self.connected==False:
            time.sleep(0.1)
            return ["0"]

        if self.count_disconnected>50:
            self.count_disconnected=0
            print("try reconnect")
            self.disconnect()
            self.connect()


        self.wait_my_query()
        #print("send")
        try:
            self.socket.send_string("t~" + self.id + "~", zmq.NOBLOCK)  # zmq.NOBLOCK
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                #print("error", e)
                pass
        message=""
        t = time.time()
        while 1:
            try:
                message = self.socket.recv_string(zmq.NOBLOCK)
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    #print("error", e)
                    pass
            if len(message)>0:
                self.count_disconnected=0
                break
            if time.time()-t>0.1:
                self.count_disconnected+=1
                break


        self.exit_query()

        #print("message:", message)

        if  message != None:
            message = message.split("~")
            if message[0] == "":
                return []
            if message[0] != "-1":
       #         print("return", message)
                return message
            else:
                self.registration()

        # if message!="-1":
        return []

    def send_and_wait_answer(self, to_id, text):
        #print(len(self.list_wait))
        self.send_to(to_id, text)
        while 1:
            answer = self.take_answer()
            # пришел запрос, надо ответить
            if len(answer)==0:
                continue
            if answer[0] != "-1":
                break
        if len(answer)>1:
            return answer[1]
        return ""

    def take_frame(self, to_id):
        self.send_to(to_id, "p~"+self.id +"~")
        while 1:
            answer = self.take_answer_bytes()
            # пришел запрос, надо ответить
            if answer[0] != "-1":
                break
        return answer[1]

    def send_bytes_to(self, to_id, json_text, bytes):
        if self.connected==False:
            return

        self.wait_my_query()
        #print("send string")
        try:
            self.socket.send_string("b~"+self.id +"~" +str(to_id)+"~"+json_text, zmq.SNDMORE)
            #print("send bytes", len(bytes))
            self.socket.send(bytes)
            #print("send bytes ok")
            message = str(self.socket.recv_string())
        except:
            pass
        self.exit_query()

    def take_answer_bytes(self):
        if self.connected==False:
            return

        self.wait_my_query()
        try:
            self.socket.send_string("bt~"+self.id +"~")
            message_json = self.socket.recv_json()
            message = self.socket.recv(0)
        except:
            pass
        self.exit_query()
        return message_json, message

    def send_key(self, to_id, key):
        self.send_to( to_id, "k|"+str(key))











