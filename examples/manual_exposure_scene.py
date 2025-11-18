import cv2

from pupil_labs.neon_usb import SceneCamera

camera = SceneCamera()

counter = 0
while True:
    counter += 1
    print(camera.exposure)
    frame = camera.get_frame()
    image = frame.bgr
    camera.exposure = 50 + (counter % 125) * 10
    cv2.imshow("Neon Scene Camera", image)
    cv2.waitKey(1)
