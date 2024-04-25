import cv2
import numpy as np
import os


class ObjectDetection:
    def __init__(
        self,
        weights_path="yolov4.weights",
        cfg_path="yolov4.cfg",
        classes_path="classes.txt",
    ):

        # Set non-maximum suppression threshold
        self.nmsThreshold = 0.4
        # Set confidence threshold for object detection
        self.confThreshold = 0.5
        # Set image size for consistency
        self.image_size = 608

        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Update paths to use current directory
        weights_path = os.path.join(current_dir, weights_path)
        cfg_path = os.path.join(current_dir, cfg_path)
        classes_path = os.path.join(current_dir, classes_path)

        # Load YOLOv4 network
        net = cv2.dnn.readNet(weights_path, cfg_path)

        # Enable GPU CUDA for faster inference
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.model = cv2.dnn_DetectionModel(net)

        # Initialize empty lists for classes and colors
        self.classes = []
        self.load_class_names(classes_path)
        self.colors = np.random.uniform(0, 255, size=(80, 3))

        # Set input parameters for the model
        self.model.setInputParams(
            size=(self.image_size, self.image_size), scale=1 / 255
        )

    def load_class_names(self, classes_path):
        with open(classes_path, "r") as file_object:
            for class_name in file_object.readlines():
                class_name = class_name.strip()
                self.classes.append(class_name)

    def detect(self, frame):
        return self.model.detect(
            frame, nmsThreshold=self.nmsThreshold, confThreshold=self.confThreshold
        )
