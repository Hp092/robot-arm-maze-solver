import cv2
import numpy as np

# Function to check if the camera is connected successfully
def checkCamera():
    camera_index = 0  # Camera index (0 is usually the default camera)
    cap = cv2.VideoCapture(camera_index)  # Initialize camera capture

    # Check if the camera is successfully connected
    if cap.isOpened():
        print("Camera connected successfully!")
    else:
        print("Failed to connect to the camera.")

    cap.release()  # Release the camera resource


# Load a predefined ArUco dictionary (6x6 grid with 250 possible IDs)
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Create default parameters for ArUco marker detection
aruco_params = cv2.aruco.DetectorParameters()

# Open the camera (camera index 0)
cap = cv2.VideoCapture(0)

# Main loop to capture and process frames from the camera
while True:
    # Capture a single frame from the camera
    ret, frame = cap.read()

    # Check if the frame was successfully captured
    if not ret:
        print("Failed to grab frame.")
        break

    # Convert the captured frame to grayscale for ArUco detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect ArUco markers in the frame
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)

    # If markers are detected, process them
    if ids is not None:
        # Loop through each detected marker
        for i, corner in enumerate(corners):
            # Draw a polygon around the detected marker
            cv2.polylines(frame, [np.int32(corner)], True, (0, 255, 0), 2)

            # Calculate the center of the marker
            x_center = int((corner[0][0][0] + corner[0][2][0]) / 2)  # X-coordinate of the center
            y_center = int((corner[0][0][1] + corner[0][2][1]) / 2)  # Y-coordinate of the center

            # Retrieve the ID of the marker
            marker_id = ids[i][0]

            # Display the marker ID and its center coordinates on the frame
            cv2.putText(frame, f"ID: {marker_id} X: {x_center} Y: {y_center}", (x_center, y_center),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Display the frame with the detected markers
    cv2.imshow('ArUco Marker Detection', frame)

    # Exit the loop when the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera resource
cap.release()

# Close all OpenCV windows
cv2.destroyAllWindows()
