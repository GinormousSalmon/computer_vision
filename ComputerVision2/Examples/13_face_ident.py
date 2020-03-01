import RobotAPI as rapi
import cv2
import time
import dlib

robot = rapi.RobotAPI()

print("Start load libs..")


# Orange
# sp = dlib.shape_predictor('/root/robot/shape_predictor_68_face_landmarks.dat')
# facerec = dlib.face_recognition_model_v1('/root/robot/dlib_face_recognition_resnet_model_v1.dat')
# face_cascade = cv2.CascadeClassifier('/root/robot/haarcascade_frontalface_default.xml')

# Raspberry
sp = dlib.shape_predictor('/home/pi/robot/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('/home/pi/robot/dlib_face_recognition_resnet_model_v1.dat')
face_cascade = cv2.CascadeClassifier('/home/pi/robot/haarcascade_frontalface_default.xml')

detector = dlib.get_frontal_face_detector()


print("Done.. Start work")

def take_priznak(frame):

    t = time.time()
    #находим лицо на изображении при помоши нейросети
    dets_webcam = detector(frame, 1)
    for k, d in enumerate(dets_webcam):
        #выделяем ключевые признаки лица(68 штук)
        shape = sp(frame, d)
        for i in range(0, 68):
            #рисуем точки на кадре
            frame = cv2.circle(frame, (shape.part(i).x, shape.part(i).y), 1, (255, 255, 255), 1)

        # на основе ключевых точек вычисляем признаки лица при помощи другой нейросети
        pr = facerec.compute_face_descriptor(frame, shape)

        # выводим информацию о времени выполнения функции
        robot.text_to_frame(frame, str(round(time.time() - t, 3)), 20, 20)

        return pr
    return []



def take_priznak_fast(frame):

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, 1.35, 5)

    t = time.time()
    for (x, y, w, h) in faces:
            frame1 = frame[y: y + h, x: x + w]
            dets_webcam = detector(frame1, 1)
            for k, d in enumerate(dets_webcam):
                #cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (0, 0, 255), 2)
                shape = sp(frame1, d)
                for i in range(0, 68):
                    frame = cv2.circle(frame, (x+shape.part(i).x, y+shape.part(i).y), 1, (255, 255, 255), 1)

                pr = facerec.compute_face_descriptor(frame1, shape)
                robot.text_to_frame(frame, str(round(time.time() - t, 3)), 20, 20)
                return pr


    return []


master =[]

while True:

    if robot.manual() == 1:
        continue
    frame = robot.get_frame().copy()

    #take_priznak(frame)
    take_priznak_fast(frame)

    robot.set_frame(frame)

