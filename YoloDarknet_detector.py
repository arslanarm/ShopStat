import cv2

from classes.cnn_class import Cnn
cnn = Cnn('yolov7-tiny.weights', 'yolov7-tiny.cfg', 0.3, 0.5, 512)

cap = cv2.VideoCapture('videos_for_test/tester.mp4')

while True:
    ret, frame = cap.read()
    final_boxes, final_confidences, final_class_ids = cnn.get_bboxes(frame)
    res = cnn.draw_boxes(final_boxes, frame)
    cv2.imshow('Res', res)
    cv2.waitKey(1)