import onnxruntime as ort
import numpy as np
import cv2
import time
from utils import time_it

# Class for working with an ONNX model
class CnnOnnx:
    def __init__(self, weights_path, size=640, cuda=True):
        """
        Initialize the class.

        :param weights_path: Path to the model weights.
        :param size: Size of the input image for the model.
        :param cuda: Whether to use GPU (CUDA).
        """
        self.size = size
        self.weights_path = weights_path
        # Choose providers for execution (CUDA for GPU or CPU)
        self.providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']
        print("Used providers: ", self.providers)
        # Create a session for model execution
        self.session = ort.InferenceSession(self.weights_path, providers=self.providers)
        # Get the names of model inputs and outputs
        self.outname = [i.name for i in self.session.get_outputs()]
        self.inname = [i.name for i in self.session.get_inputs()]

    @time_it
    def detect_image(self, image, conf_threshold=0.1, nms_threshold=0.8):
        """
        Detect objects in an image.

        :param image: Input image.
        :param conf_threshold: Confidence threshold for detection.
        :param nms_threshold: Threshold for non-maximum suppression (NMS).
        :return: Boxes, probabilities, and object classes.
        """
        # Convert the image to RGB format
        processed_img = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2RGB)
        # Resize the image and add padding
        processed_img, ratio, dwdh = letterbox(processed_img, auto=False, new_shape=(self.size, self.size))
        # Transpose the image axes to match the ONNX format
        processed_img = processed_img.transpose((2, 0, 1))
        # Add a batch dimension
        processed_img = np.expand_dims(processed_img, 0)
        # Convert the array to contiguous memory layout
        processed_img = np.ascontiguousarray(processed_img)
        # Normalize the image
        im = processed_img.astype(np.float32)
        im /= 255

        # Pass the image to the model input and perform inference
        inp = {self.inname[0]: im}
        start = time.time()
        outputs = self.session.run(self.outname, inp)[0]
        end = time.time()
        # Inference execution time
        res = end - start
        h, w, _ = image.shape
        boxes = []
        scores = []
        classes = []
        # Process the inference results
        for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
            if cls_id == 0:
                box = np.array([x0, y0, x1, y1])
                box -= np.array(dwdh * 2)
                box /= ratio
                box = box.round().astype(np.int32).tolist()
                boxes.append(box)
                scores.append(score)
                classes.append(cls_id)

        return boxes, scores, classes

    def draw_boxes(self, boxes, image):
        """
        Draw detected objects on an image.

        :param boxes: Boxes of detected objects.
        :param image: Input image.
        :return: Image with drawn objects.
        """
        h, w, _ = image.shape

        # Display detected objects on the image
        for box in boxes:
            color = (128, 128, 0)
            cv2.rectangle(image, box[:2], box[2:], color, 2)
            cv2.putText(image, 'Person', (box[0], box[1] - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.75, [225, 255, 255],
                        thickness=2)
        return image


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
    """
    Resize and add padding to an image.

    :param im: Input image.
    :param new_shape: Desired image size.
    :param color: Color of the padding.
    :param auto: Automatic mode for padding.
    :param scaleup: Scale up the image size.
    :param stride: Stride for padding.
    :return: Resized and padded image.
    """
    # Current image size
    shape = im.shape[:2]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    # Scale factor (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:
        r = min(r, 1.0)

    # Calculate padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]

    if auto:
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)

    dw /= 2
    dh /= 2

    # Resize the image
    if shape[::-1] != new_unpad:
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    # Add padding to the image
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

    return im, r, (dw, dh)
