import time

import cv2

from pupil_labs.neon_usb.cameras.eye import EyeCameraUVC

camera = EyeCameraUVC()

counter = 0
while True:
    counter += 1
    frame = camera.get_frame()
    image = frame.bgr
    print("exposure:", camera.exposure)
    camera.exposure = (counter % 50, (counter * 2) % 50)
    cv2.imshow("Neon Sensor Module", image)
    cv2.waitKey(1)
    time.sleep(0.05)
