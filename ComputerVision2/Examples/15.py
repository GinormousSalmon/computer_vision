import RobotAPI as rapi

robot = rapi.RobotAPI()

import numpy as np
from keras import backend as K
from keras.models import load_model
from PIL import Image
from yad2k.models.keras_yolo import yolo_eval, yolo_head
import cv2

net_res =[]
temp=0
install_net = False

open_cv_image = robot.get_frame()

def yolo_find():
    global open_cv_image, model_image_size, net_res,temp, install_net, sess, is_fixed_size, anchors,class_names, boxes, scores, classes, yolo_model
    global num_classes, num_anchors, input_image_shape, colors

    if install_net==False:
        install_net=True
        sess = K.get_session()

        model_path = '/home/pi/robot/model_data/tiny-yolo-voc.h5'
        anchors_path = '/home/pi/robot/model_data/tiny-yolo-voc_anchors.txt'
        classes_path = '/home/pi/robot/model_data/pascal_classes.txt'
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]

        with open(anchors_path) as f:
            anchors = f.readline()
            anchors = [float(x) for x in anchors.split(',')]
            anchors = np.array(anchors).reshape(-1, 2)

        yolo_model = load_model(model_path)
        num_classes = len(class_names)
        num_anchors = len(anchors)

        model_output_channels = yolo_model.layers[-1].output_shape[-1]
        assert model_output_channels == num_anchors * (num_classes + 5), \
            'Mismatch between model and given anchor and class sizes. ' \
            'Specify matching anchors and classes with --anchors_path and ' \
            '--classes_path flags.'
        print('{} model, anchors, and classes loaded.'.format(model_path))

        model_image_size = yolo_model.layers[0].input_shape[1:3]
        is_fixed_size = model_image_size != (None, None)

        yolo_outputs = yolo_head(yolo_model.output, anchors, len(class_names))
        input_image_shape = K.placeholder(shape=(2,))
        boxes, scores, classes = yolo_eval(
            yolo_outputs,
            input_image_shape,
            score_threshold=.3,
            iou_threshold=.5)

        print("Load net done")

    # защита от перегрева компьютера
    f = open("/sys/class/thermal/thermal_zone0/temp", "r")
    temp = int(f.readline())/1000
    if temp>55:
        robot.wait(100)
        return

    image = robot.get_frame()
    cv2_im = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(cv2_im)
    if is_fixed_size:
        resized_image = image.resize(
            tuple(reversed(model_image_size)), Image.BICUBIC)
        image_data = np.array(resized_image, dtype='float32')
    else:
        new_image_size = (image.width - (image.width % 32),
                          image.height - (image.height % 32))
        resized_image = image.resize(new_image_size, Image.BICUBIC)
        image_data = np.array(resized_image, dtype='float32')

    image_data /= 255.
    image_data = np.expand_dims(image_data, 0)
    out_boxes, out_scores, out_classes = sess.run(
        [boxes, scores, classes],
        feed_dict={
            yolo_model.input: image_data,
            input_image_shape: [image.size[1], image.size[0]],
            K.learning_phase(): 0
        })
    net_res=[]

    for i, c in reversed(list(enumerate(out_classes))):
        predicted_class = class_names[c]
        box = out_boxes[i]
        score = out_scores[i]

        label = '{} {:.2f}'.format(predicted_class, score)
        top, left, bottom, right = box
        top = max(0, np.floor(top + 0.5).astype('int32'))
        left = max(0, np.floor(left + 0.5).astype('int32'))
        bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
        right = min(image.size[0], np.floor(right + 0.5).astype('int32'))

        net_res.append([predicted_class, (left, top), (right, bottom), score])
        print(label, (left, top), (right, bottom))


while True:
    if robot.manual()==1:
        continue
    frame = robot.get_frame().copy()
    yolo_find()


    for item in net_res:
        predicted_class, (left, top), (right, bottom), score = item
        frame = cv2.rectangle(frame, (left,top), (right, bottom), (0, 255, 0), 1)
        frame = robot.text_to_frame(frame, predicted_class + " "+str(round(score,2)), left, top)

    robot.set_frame(frame)



