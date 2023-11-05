import cv2
import numpy as np
from classes.utils import time_it


class Cnn:
    net: cv2.dnn_Net
    confidence_idx: float
    threshold_idx: float

    def __init__(self, weights_path: str, config_path: str, confidence_idx, threshold_idx, size):
        """

        :param weights_path: Path of the weights file
        :param config_path: Path of the config file
        :param confidence_idx: Threshold percentage for detection
        :param threshold_idx: Threshold for deleting the overlapping boxes
        """

        # Creating net object from OpenCv for inference
        self.net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
        self.confidence_idx = confidence_idx
        self.threshold_idx = threshold_idx
        ln = self.net.getLayerNames()
        self.ln = [ln[i - 1] for i in self.net.getUnconnectedOutLayers()]
        self.size = size

    @time_it
    def get_bboxes(self, image, rel=True) -> (list[list[float]], list[float]):
        """

        :param rel: relative coordinates
        :param image: image for detection
        :return: coordinate boxes, confidence levels, class ids
        """

        # Creating blob from input image
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (self.size, self.size), swapRB=True, crop=False)

        # Setting the blob as an input and forwarding through the net
        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.ln)

        # Creating empty lists for data collection
        boxes = []
        initial_boxes = []
        final_boxes = []

        confidences = []
        final_confidences = []

        class_ids = []
        final_class_ids = []

        # Iterating other the results
        for output in layer_outputs:
            for detection in output:
                # Separating id class info
                scores = detection[5:]
                # Getting the class id by max confidence value
                class_id = np.argmax(scores)
                # Writing the confidence value of the class
                confidence = scores[class_id]
                # Confidence threshold
                if confidence > self.confidence_idx and class_id == 0:
                    # Computing the coordinates for the box
                    box = np.around(detection[0:4], 2)
                    initial_boxes.append(box)
                    (centerX, centerY, width, height) = box
                    x = centerX - (width / 2)
                    y = centerY - (height / 2)
                    # Writing the data into appropriate lists
                    boxes.append([x, y, width, height])
                    confidences.append(confidence)
                    class_ids.append(class_id)
        # Deleting the overlapping boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_idx, self.threshold_idx)

        # Adding rest into the final result
        if len(idxs) > 0:
            H, W = image.shape[:2]
            for i in idxs:
                if not rel:
                    (centerX, centerY, width, height) = initial_boxes[i] * np.array([W, H, W, H])
                    x1 = int(centerX - (width / 2))
                    y1 = int(centerY - (height / 2))
                    # x2 = int(centerX + (width / 2))
                    # y2 = int(centerY + (height / 2))
                    box = [x1, y1, int(width), int(height)]
                    final_boxes.append(box)
                else:
                    final_boxes.append(initial_boxes[i])
                final_confidences.append(confidences[i])
                final_class_ids.append(class_ids[i])
            return final_boxes, final_confidences, final_class_ids
        else:
            return None, None, None

    def draw_boxes(self, boxes, image, color=(0, 255, 0), thickness=3, confidences=None, classes=None, labels=None):
        """

        :param boxes: coordinates for rendering
        :param image: image for rendering
        :param color: color
        :param thickness: thickness of the text and boxes
        :param confidences: list of class confidences(for rendering the text on top of the boxes)
        :param classes: list of class ids(for rendering the text on top of the boxes)
        :param labels: list of class names(for rendering the text on top of the boxes)
        :return: image with rendered detection results
        """
        (H, W) = image.shape[:2]
        copy = image.copy()
        # If there are no results then simply return the original image
        if boxes is None:
            return copy
        # Case when optional confidences, classes, labels are given
        if confidences is not None:
            # Rounding until two digits after dot
            confidences = np.around(confidences, 2)
            # For each element
            for bb, conf, class_id in zip(boxes, confidences, classes):
                if class_id != 0:
                    continue
                # Computing the coordinates on image
                (centerX, centerY, width, height) = bb * np.array([W, H, W, H])
                x1 = int(centerX - (width / 2))
                y1 = int(centerY - (height / 2))
                x2 = int(centerX + (width / 2))
                y2 = int(centerY + (height / 2))
                # Drawing the box
                cv2.rectangle(copy, (x1, y1), (x2, y2), color, thickness)
                # Drawing the text
                cv2.putText(copy, '{}: {:.2f}'.format(labels[class_id], conf), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, color,
                            thickness)
                # Adding dot in the center of the box
                cv2.circle(copy, (int(centerX), int(centerY)), 1, color, -1)
        # Only drawing the boxes
        else:
            for bb in boxes:
                (centerX, centerY, width, height) = bb * np.array([W, H, W, H])
                x1 = int(centerX - (width / 2))
                y1 = int(centerY - (height / 2))
                x2 = int(centerX + (width / 2))
                y2 = int(centerY + (height / 2))
                cv2.rectangle(copy, (x1, y1), (x2, y2), color, thickness)
        return copy
