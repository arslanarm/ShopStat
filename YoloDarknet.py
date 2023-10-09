import cv2
import numpy as np
from utils import time_it


class Cnn:
    net: cv2.dnn_Net
    confidence_idx: float
    threshold_idx: float

    def init(self, weights_path: str, config_path: str, confidence_idx, threshold_idx, size):
        """
        :param weights_path: Path to the weights file
        :param config_path: Path to the configuration file
        :param confidence_idx: Confidence percentage threshold for detection
        :param threshold_idx: Threshold for removing overlapping detections
        """

        # Create an OpenCv net object for inference
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
        :param image: Image for recognition
        :return: box coordinates as a list, confidence levels as a list, class ids as a list
        """

        # Create a blob from the input image
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (self.size, self.size), swapRB=True, crop=False)

        # Feed the blob to the network and process through the neural network layers
        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.ln)

        # Define empty lists to be populated later
        boxes = []
        initial_boxes = []
        final_boxes = []

        confidences = []
        final_confidences = []

        class_ids = []
        final_class_ids = []

        # Iterate through all results
        for output in layer_outputs:
            for detection in output:
                # Extract class id information
                scores = detection[5:]
                # Find the maximum match percentage among all classes and remember the class
                class_id = np.argmax(scores)
                # Record the maximum match percentage
                confidence = scores[class_id]
                # If the confidence level is above a certain threshold
                if confidence > self.confidence_idx and class_id == 0:
                    # Read the coordinates and find the corner coordinates to create a rectangle
                    box = np.around(detection[0:4], 2)
                    initial_boxes.append(box)
                    (centerX, centerY, width, height) = box
                    x = centerX - (width / 2)
                    y = centerY - (height / 2)
                    # Populate the corresponding lists with these data
                    boxes.append([x, y, width, height])
                    confidences.append(confidence)
                    class_ids.append(class_id)
        # Function to remove overlapping detections based on their intersection area
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_idx, self.threshold_idx)

        # Add remaining detections to the final result
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
        :param boxes: Boxes (rectangle coordinates for drawing)
        :param image: Image for drawing
        :param color: Color
        :param thickness: Font and rectangle thickness
        :param confidences: List of corresponding confidence percentages (to be displayed as text above the rectangle)
        :param classes: List of corresponding class ids (to be displayed as text above the rectangle)
        :param labels: List of corresponding class names (to be displayed as text above the rectangle)
        :return: Image with drawn recognition results
        """
        (H, W) = image.shape[:2]
        copy = image.copy()
        # If there are no recognition results, return the same image
        if boxes is None:
            return copy
        # If in addition to rectangle coordinates, optional parameters confidences, classes, and labels are given
        if confidences is not None:
            # Round to two decimal places
            confidences = np.around(confidences, 2)
            # For each element
            for bb, conf, class_id in zip(boxes, confidences, classes):
                if class_id != 0:
                    continue
                # Calculate the coordinates
                (centerX, centerY, width, height) = bb * np.array([W, H, W, H])
                x1 = int(centerX - (width / 2))
                y1 = int(centerY - (height / 2))
                x2 = int(centerX + (width / 2))
                y2 = int(centerY + (height / 2))
                # Draw the rectangle
                cv2.rectangle(copy, (x1, y1), (x2, y2), color, thickness)
                # Overlay the text
                cv2.putText(copy, '{}: {:.2f}'.format(labels[class_id], conf), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, color, thickness)
                # Draw a point in the center
                cv2.circle(copy, (int(centerX), int(centerY)), 1, color, -1)
        # Do the same but draw only the rectangles
        else:
            for bb in boxes:
                (centerX, centerY, width, height) = bb * np.array([W, H, W, H])
                x1 = int(centerX - (width / 2))
                y1 = int(centerY - (height / 2))
                x2 = int(centerX + (width / 2))
                y2 = int(centerY + (height / 2))
                cv2.rectangle(copy, (x1, y1), (x2, y2), color, thickness)
        return copy
