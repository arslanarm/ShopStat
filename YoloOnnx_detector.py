from Onnx_Class import CnnOnnx
import cv2
cnn = CnnOnnx('yolov7_dynamic.onnx')

cap = cv2.VideoCapture('videos/tester.mp4')

while True:
    ret, frame = cap.read()
    boxes, scores, classes = cnn.detect_image(frame)
    res = cnn.draw_boxes(boxes, frame)
    cv2.imshow('Res', res)
    cv2.waitKey(1)