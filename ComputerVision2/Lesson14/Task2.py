import numpy as np
import cv2
import time
import threading
import RobotAPI as rapi

robot = rapi.RobotAPI()

yaw = 0
e_old = 0
x0 = 0
install = False
servo = 0


def flow_work(show=False):
    global yaw, time_work, p0, color, lk_params, feature_params, old_gray, install

    if not install:
        feature_params = dict(maxCorners=50, qualityLevel=0.003, minDistance=70, blockSize=70)
        lk_params = dict(winSize=(25, 25), maxLevel=2,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        color = np.random.randint(0, 255, (1000, 3))
        old_frame = robot.get_frame()
        old_frame = old_frame[0: 200, 0: 640]
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
        install = True
        print("install")

    frame = robot.get_frame()
    frame = frame[0: 200, 0: 640]
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if len(p0) < 30 or (p0 is None):
        p0 = np.vstack((p0, cv2.goodFeaturesToTrack(frame_gray, mask=None, **feature_params)))
        return frame
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    if p1 is not None:
        good_new = p1[st == 1]
        good_old = p0[st == 1]
        m = np.array([])
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a, b = new.ravel()
            c, d = old.ravel()
            m = np.append(m, (a - c))
            if show:
                frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
        if len(m) > 0:
            yaw += np.median(m)
        old_gray = frame_gray
        p0 = good_new.reshape(-1, 1, 2)
    # return frame


def flowing():
    while True:
        flow_work(False)


def constrain(a, min, max):
    if a < min:
        return min
    else:
        if a > max:
            return max
        else:
            return a


thread = threading.Thread(target=flowing)
thread.daemon = True
thread.start()
while True:
    if robot.manual():
        yaw = 0
        x0 = 0
        continue
    t = time.time()

    frame = robot.get_frame()

    robot.text_to_frame(frame, str(round(yaw / 10, 2)), 20, 20)
    time_work = time.time() - t
    robot.text_to_frame(frame, str(round(time_work, 3)), 20, 40, font_color=(0, 0, 255))
    robot.set_frame(frame)
    e = x0 - yaw
    u = e * 0.2 + (e - e_old) * 2
    s1 = constrain(100 - u, -20, 90)
    s2 = constrain(100 + u, -20, 90)
    robot.move(s1, s2, 20)
    if robot.button():
        x0 = yaw
cv2.destroyAllWindows()
robot.cap.release()
