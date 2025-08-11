# File: object_tracking_uart.py (Run this on Raspberry Pi 5)

import cv2
import numpy as np
import serial
from picamera2 import Picamera2
from time import sleep
import time

# Initialize camera
picam2 = Picamera2()

# Autofocus (if supported)
camera_controls = {"AfMode": 1}
picam2.set_controls(camera_controls)

# Configure video preview
video_config = picam2.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"},
    controls=camera_controls
)
picam2.configure(video_config)

# Initialize UART communication (RPi 5 to Pico via UART1)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
time.sleep(2)  # Give time for the Pico to initialize

# Start camera
picam2.start()
sleep(1)

# HSV range for black
lower_hsv = np.array([0, 0, 0])
upper_hsv = np.array([180, 100, 60])

frame_width, frame_height = 640, 480
frame_center = (frame_width // 2, frame_height // 2)

print("Tracking started. Press 'q' to stop.")

try:
    while True:
        frame = picam2.capture_array()
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower_hsv, upper_hsv)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            (x, y), radius = cv2.minEnclosingCircle(largest)

            if radius > 5:
                center = (int(x), int(y))
                error_x = center[0] - frame_center[0]
                error_y = center[1] - frame_center[1]

                # Send only error_x
                message = f"{error_x},0\n"
                ser.write(message.encode())

                # Debug output
                print(f"Sent error_x: {error_x}")

                # Draw on frame
                cv2.circle(frame, center, int(radius), (0, 255, 0), 2)
                cv2.circle(frame, frame_center, 5, (255, 0, 0), -1)

        cv2.imshow("RPi Cam Feed", frame)
        cv2.imshow("Color Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
    ser.close()
