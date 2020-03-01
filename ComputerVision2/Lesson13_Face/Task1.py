import RobotAPI as rapi
import cv2

robot = rapi.RobotAPI()

face_cascade = cv2.CascadeClassifier('/home/pi/robot/haarcascade_frontalface_default.xml')
# face_cascade = cv2.CascadeClassifier('/root/haarcascade_frontalface_default.xml')


def constrain(a, min, max):
    if a < min:
        return min
    else:
        if a > max:
            return max
        else:
            return a


yaw = 0
kp = 0.05
kd = 0.1
e_old = 0
robot.serv(0)
while True:
        frame = robot.get_frame()
#        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_image, 1.35, 5)
        e = 0
        for (x, y, w, h) in faces:
            center_face = x+w/2
            frame = robot.text_to_frame(frame,"center_face="+str(center_face), 20,20)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            e = (x + w/2) - 320
        u = e * kp + (e_old - e) * kd
        e_old = e
        yaw += u
        yaw = constrain(yaw, -160, 160)
        robot.serv(yaw)
        robot.set_frame(frame)
