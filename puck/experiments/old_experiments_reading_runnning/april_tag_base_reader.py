import cv2 as cv
from matplotlib import pyplot as plt

input = cv.imread("puck/apriltag_stills/test_6.png")
DICT = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_16H5)
detector = cv.aruco.ArucoDetector(dictionary=DICT)
corners, ids, _ = detector.detectMarkers(input)
copy = input.copy()
copy = cv.aruco.drawDetectedMarkers(copy, corners, ids)
plt.imshow(copy)
plt.show()