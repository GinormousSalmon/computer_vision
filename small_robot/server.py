import zmq
import time
import json
import threading
import datetime

context2 = zmq.Context(1)
socket2 = context2.socket(zmq.REP)

socket2.bind("tcp://*:7777")


def __del__():
    # def cleanup():
    global socket2
    print("close socket")
    socket2.close()


# atexit.register(cleanup)


num_client = 0
clients_list = []  # id, name, type, timeout
message_list = []  # id_from, text, id_to, type, data


def load_list_clients():
    global num_client, clients_list
    with open('clients.txt', 'r') as content_file:
        clients = content_file.read()
    clients = clients.split('\n')

    for s in clients:
        s = s.split(",")
        if len(s) > 4:
            clients_list.append([int(s[0]), s[1], s[2], float(s[3])])
            num_client = int(s[0]) + 1
    print(clients_list)


def save_list_clients():
    global clients_list
    str_list = ""
    for s in clients_list:
        for i in s:
            str_list += str(i) + ","
        str_list += "\n"

    with open("clients.txt", "w") as text_file:
        text_file.write(str_list)


def take_message(id, type):
    # находим сообщение для клиента  id_from, text, id_to
    # print("take_message", id)
    # print(message_list)
    for i in range(len(message_list)):
        if message_list[i][1] == id and type == message_list[i][3]:
            mes = message_list.pop(i)
            return mes
    return []


def clear_paket(id):
    global message_list
    id = int(id)
    count = 0
    new_list = []
    for i in range(len(message_list)):
        if message_list[i][0] == id or message_list[i][2] == id:
            count += 1
            pass
        else:
            new_list.append(message_list[i])

    message_list = new_list.copy()
    return count


def find_duble(mes):
    for i in range(len(message_list)):
        # print( message_list[i], mes)
        if message_list[i][0] == int(mes[1]) and message_list[i][1] == int(mes[2]) and message_list[i][2] == mes[3]:
            # message_list.pop(i)
            # print("duble", mes)
            return True
    return False
    pass


def test_client():
    t = time.time()
    while 1:
        if t + 5 < time.time():
            print("----------------- message_list:" + str(len(message_list)))
            for m in message_list:
                print(m)
            print("----------------- message_list:" + str(len(message_list)))
            t = time.time()
            # print("clients_list ", len(clients_list), "message_list", len(message_list))
            for c in clients_list:
                #                    if c[3]<time.time()+10:
                if time.time() - c[3] < 5:
                    count_in = 0
                    count_out = 0
                    for p in message_list:
                        if p[1] == c[2]:
                            count_in += 1
                        if p[2] == c[0]:
                            count_out += 1

                    print("pause client ", c, round(time.time() - c[3], 2), "messages_in", count_in, "message_out",
                          count_out)
        # print(message_list)
        time.sleep(1)


my_thread = threading.Thread(target=test_client)
# my_thread.daemon = True
# my_thread.start()

load_list_clients()

while 1:

    message = socket2.recv_string()
    message = message.split("~")
    # print(message)

    # пересылка инфы
    if message[0] == "s":
        # чистим все запросы до этого
        # while 1:
        #     mes = take_message(int(message[1]), "s")
        #     if len(mes) == 0:
        #         break
        # print(message)
        if find_duble(message) == False:
            try:
                message_list.append([int(message[1]), int(message[2]), message[3], "s"])
            except:
                pass
        # print(message_list)
        socket2.send_string("1~")
        continue

    # запрос на получение ответа
    if message[0] == "t":
        # чистим все запросы до этого
        # while 1:
        #     mes = take_message(int(message[1]), "t")
        #     if len(mes) == 0:
        #         break
        mes = take_message(int(message[1]), "s")

        flag_reg = False
        # print(clients_list, message)
        for c in clients_list:
            if c[0] == int(message[1]):
                flag_reg = True
                c[3] = time.time()

        # print(message)
        resp = "0~"
        if flag_reg == False:
            print("nedd reg", message)
            resp = "-1~"

        if len(mes) > 0:
            if mes[3] == "s":
                resp = str(mes[0]) + "~" + (mes[2]) + "~"
            # print(resp)
        # print(resp)
        socket2.send_string(resp)
        continue

    # пересыл байтовой информации
    if message[0] == "b":
        # print(message)
        message_byte = socket2.recv(0)
        # print("take bytes", len(message_byte))

        # чистим все месаги байтовые впереди
        while 1:
            mes = take_message(int(message[1]), "b")
            if len(mes) == 0:
                break
        message_list.append([int(message[1]), int(message[2]), message[3], "b", message_byte])
        # print(message_list)
        socket2.send_string("1~")
        continue

    # запрос на получение ответа байтовой посылки
    if message[0] == "bt":
        # print(message)
        mes = take_message(int(message[1]), "b")
        # print("bt_mes", mes)
        frame_json = "-1"
        frame_bytes = b''
        resp = "-1~"
        if len(mes) > 0:
            if mes[3] == "b":
                # resp = str(mes[0]) + "~" + (mes[2]) + "~"
                # socket2.send_string(resp)
                # print("send,",mes[1] )
                frame_json = json.loads(mes[2])
                frame_bytes = mes[4]

            # print(resp)
        # пусто
        # socket2.send_string(frame_json, zmq.SNDMORE)

        socket2.send_json(frame_json, zmq.SNDMORE)
        socket2.send(frame_bytes)

        continue

    if message[0] == "clear":
        # print("take num ", num_client)
        # print("clear", message)
        count = clear_paket(message[1])
        socket2.send_string(str(count))
        continue

    if message[0] == "i":
        # print("take num ", num_client)
        num = num_client
        f = 1
        for l in clients_list:
            if l[1] == message[1]:
                # print("old client")
                f = 0
                num = l[0]
                print("login ", datetime.datetime.today(), message[1], message[2])
                continue
        if f == 1:
            print("login NEW", datetime.datetime.today(), message[1], message[2])
            clients_list.append([int(num_client), message[1], message[2], time.time()])
            save_list_clients()
            num_client += 1
        socket2.send_string(str(num))
        # clear_paket(num_client)
        continue

    if message[0] == "l":
        list_str = ""
        for i in clients_list:
            if i[2] == "robot" and time.time() - i[3] < 50:
                for j in i:
                    list_str += str(j) + ","
                list_str += "~"
        print(list_str)
        socket2.send_string(list_str)

        continue

    # print(message)
    socket2.send_string("error")

    # socket2.send_string(message)
