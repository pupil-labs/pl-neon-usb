import cv2

from pupil_labs.neon_usb.cameras.eye import EyeCamera

camera = EyeCamera()

counter = 0
while True:
    counter += 1
    frame = camera.get_frame()
    image = frame.bgr
    print("exposure:", camera.exposure)
    camera.exposure = (counter % 200, counter % 400)
    cv2.imshow("Neon Sensor Module", image)
    cv2.waitKey(1)
