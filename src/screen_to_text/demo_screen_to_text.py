import cv2
import easyocr
import numpy as np
from PIL import ImageGrab

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
