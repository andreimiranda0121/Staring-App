from imutils.video import VideoStream
import cv2
import time
import f_detector
import imutils
import numpy as np
import config as cfg
import random

# Instantiate the detector
detector = f_detector.eye_blink_detector()

# Initialize variables for the blink detector
COUNTER = 0
TOTAL = 0
prev_total = 0  # Variable to store the previous value of TOTAL

# Load the image for pop-up

# Start video stream
vs = VideoStream(src=0).start()

try:
    while True:
        start_time = time.time()
        im = vs.read()

        # Check if frame retrieval is successful
        if im is None:
            print("Error: Unable to retrieve frame from the video stream.")
            break

        im = cv2.flip(im, 1)
        im = imutils.resize(im, width=800)  # Adjust the width as needed
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        # Detect faces
        rectangles = detector.detector_faces(gray, 0)
        boxes_face = f_detector.convert_rectangles2array(rectangles, im)

        if len(boxes_face) != 0:
            # Select the face with the largest area
            areas = f_detector.get_areas(boxes_face)
            index = np.argmax(areas)
            rectangles = rectangles[index]
            boxes_face = np.expand_dims(boxes_face[index], axis=0)

            # Blink detector
            COUNTER, TOTAL = detector.eye_blink(gray, rectangles, COUNTER, TOTAL)

            # Add bounding box
            img_post = f_detector.bounding_box(im, boxes_face, ['blinks: {}'.format(TOTAL)])
        else:
            img_post = im

        # Visualization
        end_time = time.time() - start_time
        FPS = 1 / end_time
        cv2.putText(img_post, f"FPS: {round(FPS, 3)}", (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('blink_detection', img_post)

        # Show popup image when a blink is detected
        if TOTAL > prev_total:
            random_number = random.randint(0,4)
            image_list = ['TEST.jpg','scary-face-4.jpg','comedy-face.jpg','scary-face-1.jpg','scary-face-2.jpg']
            popup_image = cv2.imread("C:\\Users\\Andrei\\Desktop\\BSCS3 SEN02\\eye_blink_detection\\"+image_list[random_number])
            cv2.namedWindow('Popup Image', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('Popup Image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('Popup Image', popup_image)
            cv2.waitKey(3000)  # Wait for 3000 milliseconds (3 seconds)
            cv2.destroyWindow('Popup Image')
            prev_total = TOTAL  # Update prev_total after displaying the image

        # Check if the user pressed the 'X' button to close the window
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty('blink_detection', cv2.WND_PROP_VISIBLE) < 1:
            break

finally:
    # Stop the video stream and close all windows
    vs.stop()
    cv2.destroyAllWindows()
