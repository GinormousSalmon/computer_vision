
import cv2
import numpy as np



low = np.array([101, 130, 0])
up = np.array([121, 256, 256])

def find_signs(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, up)
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    list = []
    for contur in contours:
        x, y, w, h = cv2.boundingRect(contur)
        (x_r, y_r), radius = cv2.minEnclosingCircle(contur)
        radius = int(radius)
        area = radius * radius * 3.14  #площадь найденого круга
        if cv2.contourArea(contur) > 0 and area > 200:
            k = area / cv2.contourArea(contur)
            if k < 1.4:
                frame1 = frame[y: y + h, x: x + h]
                mask1 = mask[y: y + h, x: x + h].copy()

                x1 = int(frame1.shape[1] / 4)
                y1 = int(frame1.shape[0] / 2)

                x2 = int(frame1.shape[1] / 2)
                y2 = int(frame1.shape[0] / 4)

                x3 =int(frame1.shape[1] - frame1.shape[1] / 4)
                y3 =int(frame1.shape[0] / 2)

                #print(mask1[y1,x1] , mask1[y2,x2] , mask1[y3,x3])
                type_sign = 0

                if mask1[y1,x1] ==0 and mask1[y2,x2] >0 and mask1[y3,x3] >0 :
                    print("left")
                    type_sign = 1

                if mask1[y1,x1] >0 and mask1[y2,x2] >0 and mask1[y3,x3] ==0 :
                    print("rigth")
                    type_sign = 2

                if mask1[y1,x1] >0 and mask1[y2,x2] ==0 and mask1[y3,x3] >0 :
                    print("forward")
                    type_sign = 3

                list.append([x, y, w, h, radius, type_sign])
    return list

# пример исполнения функции в программе
# while True:
#     if robot.button() == 1:
#         break
#     frame = robot.get_frame()
#
#     signs = find_sign(frame)
#
#     for sign in signs:
#         x, y, w, h, radius, type = sign
#         print(x, y, w, h, radius, type)
#         if type == 1:
#             cv2.putText(frame, "Left", (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
#         if type == 2:
#             cv2.putText(frame, "Right", (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
#         if type == 3:
#             cv2.putText(frame, "Forward", (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
#
#         cv2.circle(frame, (int(x+w/2), int(y+h/2)), radius, (255, 0, 0), 2)
#
#     robot.set_frame(frame)
#
