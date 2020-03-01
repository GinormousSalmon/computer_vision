import threading
import time

coins = 0
count = 0
threads = []
# append


def mining():
    global coins
    time.sleep(1)
    coins += 1


start_time = time.time()

for i in range(0, 249):
    threads.append(threading.Thread(target=mining))
    threads[i].daemon = True
    threads[i].start()

while coins < 9:
    pass

end_time = time.time() - start_time
print(end_time)
