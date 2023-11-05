import onnxruntime as ort
import numpy as np
import cv2
import time

class CnnOnnx:
    def __init__(self, weights_path, size=640, cuda=True):
        self.size = size
        self.weights_path = weights_path
        self.providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']
        print("Using providers: ", self.providers)
        self.session = ort.InferenceSession(self.weights_path, providers=self.providers)
        self.outname = [i.name for i in self.session.get_outputs()]
        self.inname = [i.name for i in self.session.get_inputs()]

    def detect_image(self, image, cl_id = 0):
        processed_img = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)

        processed_img, ratio, dwdh = letterbox(processed_img, auto=False, new_shape=(self.size, self.size))
        processed_img = processed_img.transpose((2, 0, 1))
        processed_img = np.expand_dims(processed_img, 0)
        processed_img = np.ascontiguousarray(processed_img)
        im = processed_img.astype(np.float32)
        im /= 255

        inp = {self.inname[0]: im}
        start = time.time()
        outputs = self.session.run(self.outname, inp)[0]
        end = time.time()
        res = end - start
        # print("Inference time: ", res)
        h, w, _ = image.shape
        boxes = []
        scores = []
        classes = []
        for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
            if cls_id != cl_id:
                continue
            box = np.array([x0, y0, x1, y1])
            box -= np.array(dwdh * 2)
            box /= ratio
            box = box.round().astype(np.int32).tolist()
            box = [box[0], box[1], box[2]-box[0], box[3]-box[1]]
            boxes.append(box)
            scores.append(score)
            classes.append(cls_id)

        return boxes, scores, classes

    def draw_boxes(self, boxes, image):
        h, w, _ = image.shape

        for box in boxes:
            color = (128, 128, 0)
            cv2.rectangle(image, box[:2], box[2:], color, 2)
            cv2.putText(image, "Bottle", (box[0], box[1] - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.75, [225, 255, 255],
                        thickness=2)
        return image


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border

    return im, r, (dw, dh)
