#Изменить размер матрицы
#frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)

# размеры матрицы
#y = frame.shape[0]
#x = frame.shape[1]
#x,y = frame.shape

# вырезать часть кадра(кроп)
# frame = frame[d.top(): d.bottom(), d.left():d.right()].copy()
# frame = frame[100: 300, 0:x].copy()

# вырезать часть изображение, снизу полоска 150 по Y, по X вся ширина
#frame = frame[frame.shape[0] - 150: frame.shape[0], 0: frame.shape[1]].copy()

#конвертировать в черно-белый формат
#gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# вывести на экран текст
#cv2.putText(frame, str("test"), (100, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)

# обьеденить две матрицы по горизонтале
#np.vstack([frame1, frame2])

# обьеденить две матрицы по вертикале
#np.hstack([frame1, frame2])

# отрисовать контуры
#cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

# создать контур и вычислить его площадь
#countur_rect = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])
#k = cv2.contourArea(countur_rect)

# найти rect вокруг контура
#x, y, w, h = cv2.boundingRect(contur)

# расстояние между двумя точками numpy
#def dist(xa,ya,xb,yb,za=0,zb=0):
#    return np.sqrt(np.sum((np.array((xa, ya, za))-np.array((xb, yb, zb)))**2))
# пример работы функции
#p1 = distance_between_points(pos[0][0], pos[0][1], pos[1][0], pos[1][1])

# HSV
# low = np.array([80, 0, 0])
# up = np.array([100, 255, 255])
# frame1 = frame[420: 480, 100:540]
# hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
# mask1 = cv2.inRange(hsv1, low, up)
# im2, contours1, hierarchy = cv2.findContours(mask1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)





