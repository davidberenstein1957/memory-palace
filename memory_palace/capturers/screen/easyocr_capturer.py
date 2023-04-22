import logging
import threading

import cv2
import easyocr
import numpy as np
from PIL import ImageGrab

from memory_palace.processors.haystack_processor import HaystackProcessor

_LOGGER = logging.getLogger(__name__)


class EasyOCRCapturer(threading.Thread):
    def __init__(self, processor = None, type="screen", subtype="easyocr") -> None:
        super().__init__()
        self.running = False
        if processor is None:
            processor = HaystackProcessor()
        self.processor = processor

    def run(self):
        self.running = True
        while self.running:
            # Initialize the EasyOCR reader
            reader = easyocr.Reader(['en'])

            # Capture the screen
            screen = np.array(ImageGrab.grab())

            # Convert the captured screen to grayscale
            gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

            # Perform OCR using EasyOCR
            result = reader.readtext(gray)

            # Print the OCR result
            print(result)


    def stop(self):
        self.running = False
        self.join()