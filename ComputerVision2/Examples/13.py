import RobotAPI as rapi
import cv2

robot = rapi.RobotAPI()

face_cascade = cv2.CascadeClassifier('/home/pi/robot/haarcascade_frontalface_default.xml')
#face_cascade = cv2.CascadeClassifier('/root/haarcascade_frontalface_default.xml')

while True:
        frame = robot.get_frame()
#        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_image, 1.35, 5)

        for (x, y, w, h) in faces:
            center_face =x+w/2
            frame = robot.text_to_frame(frame,"center_face="+str(center_face), 20,20)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        robot.set_frame(frame)
