import csv
import cv2
import numpy as np
import heapq
import math

# Globals to store points clicked on the image
points = []

def click_event(event, x, y, flags, param):
    """
    Handle mouse click events to select points on the maze.
    """
    global pointsdeno
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((y, x))  # Append the point as (row, col)
        print(f"Point selected: ({x}, {y})")

def preprocess_maze(image):
    """
    Preprocess the maze image to create a binary image where white pixels represent paths
    and black pixels represent walls.
    """
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding to convert the image into black and white
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    return binary

def create_cost_array(maze_binary):
    """
    Create a cost array using the distance transform.
    """
    dist_transform = cv2.distanceTransform(maze_binary, cv2.DIST_L2, 5)
    cost_array = np.max(dist_transform) - dist_transform  # Invert distance values
    cost_array[maze_binary == 0] = np.inf  # Set walls to infinite cost
    return cost_array

def heuristic(point, end_point):
    """
    Heuristic function for A* (Manhattan distance).
    """
    return abs(point[0] - end_point[0]) + abs(point[1] - end_point[1])

def find_path_a_star_with_cost(maze_binary, cost_array, start_point, end_point):
    """
    Find a path using the A* algorithm, considering distance transform costs.
    """
    if maze_binary[start_point] == 0 or maze_binary[end_point] == 0:
        raise ValueError("Start or end point is on a wall. Please adjust the points.")

    rows, cols = maze_binary.shape
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start_point, end_point), 0, start_point))
    came_from = {}
    g_score = {start_point: 0}
    f_score = {start_point: heuristic(start_point, end_point)}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while open_set:
        _, current_g, current = heapq.heappop(open_set)
        if current == end_point:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_point)
            return path[::-1]

        for d in directions:
            neighbor = (current[0] + d[0], current[1] + d[1])
            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols):
                continue
            if maze_binary[neighbor] == 0:
                continue

            tentative_g = current_g + cost_array[neighbor]
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end_point)
                heapq.heappush(open_set, (f_score[neighbor], tentative_g, neighbor))

    raise ValueError("No path found between the specified start and end points.")

def simplify_path(path_indices, epsilon=5):
    """
    Simplify a path using the Douglas-Peucker algorithm to reduce unnecessary points.
    """
    def perpendicular_distance(point, line_start, line_end):
        if line_start == line_end:
            return math.sqrt((point[0] - line_start[0])*2 + (point[1] - line_start[1])*2)
        num = abs((line_end[1] - line_start[1]) * point[0] - (line_end[0] - line_start[0]) * point[1] +
                  line_end[0] * line_start[1] - line_end[1] * line_start[0])
        denom = math.sqrt((line_end[1] - line_start[1])**2 + (line_end[0] - line_start[0])**2)
        return num / denom

    def douglas_peucker(points, epsilon):
        if len(points) < 3:
            return points
        line_start, line_end = points[0], points[-1]
        max_distance, index = 0, 0
        for i in range(1, len(points) - 1):
            distance = perpendicular_distance(points[i], line_start, line_end)
            if distance > max_distance:
                index, max_distance = i, distance
        if max_distance > epsilon:
            left = douglas_peucker(points[:index + 1], epsilon)
            right = douglas_peucker(points[index:], epsilon)
            return left[:-1] + right
        return [line_start, line_end]

    return douglas_peucker(path_indices, epsilon)

def visualize_solution(maze_image, path_indices):
    """
    Overlay the solution path on the maze image as a connected line with waypoint coordinates.
    """
    solution_image = maze_image.copy()

    # Draw lines between consecutive waypoints
    for i in range(len(path_indices) - 1):
        start_point = (path_indices[i][1], path_indices[i][0])  # (x, y) format
        end_point = (path_indices[i + 1][1], path_indices[i + 1][0])  # (x, y) format
        cv2.line(solution_image, start_point, end_point, (0, 0, 255), 2)  # Draw red line with thickness 2

        # Display the waypoint coordinates in dark blue
        coord_text = f"{path_indices[i]}"
        cv2.putText(solution_image, coord_text, start_point, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (139, 0, 0), 1)

    # Add the last waypoint's coordinates
    last_point = (path_indices[-1][1], path_indices[-1][0])  # (x, y) format
    coord_text = f"{path_indices[-1]}"
    cv2.putText(solution_image, coord_text, last_point, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (139, 0, 0), 1)

    return solution_image

def save_path_to_csv(path_indices, csv_file):
    """
    Save the path indices to a CSV file.
    """
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Row", "Column"])
        writer.writerows(path_indices)

def solve_maze_with_camera(csv_file):
    global points

    print("Starting camera capture. Press 's' to capture the image, 'q' to quit.")
    cap = cv2.VideoCapture(1)  # Open the default camera
    if not cap.isOpened():
        raise RuntimeError("Cannot open the camera. Please check the connection.")

    while True:
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from camera.")

        cv2.imshow("Camera View - Press 's' to Capture", frame)
        key = cv2.waitKey(1)
        if key == ord('s'):
            captured_image = frame.copy()
            print("Image captured!")
            break
        elif key == ord('q'):
            print("Exiting camera capture.")
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

    cleaned_maze = preprocess_maze(captured_image)
    cost_array = create_cost_array(cleaned_maze)
    print("Select start and end points on the maze image (left-click).")
    cv2.imshow("Select Points", captured_image)
    cv2.setMouseCallback("Select Points", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    if len(points) != 2:
        raise ValueError("Please select exactly two points: start and end.")
    start_point, end_point = points
    print(f"Start Point: {start_point}, End Point: {end_point}")
    path_indices = find_path_a_star_with_cost(cleaned_maze, cost_array, start_point, end_point)

    # Simplify the path using Douglas-Peucker algorithm
    simplified_path = simplify_path(path_indices, epsilon=10)

    # Save the simplified path to a CSV file
    save_path_to_csv(simplified_path, csv_file)

    # Visualize the solution with waypoint coordinates
    solved_maze = visualize_solution(captured_image, simplified_path)
    cv2.imshow("Solved Maze", solved_maze)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return simplified_path

# Main script execution
output_csv_path = r"Lab4\Lab4\waypoints.csv"
simplified_path = solve_maze_with_camera(output_csv_path)
print(f"Simplified Path saved to {output_csv_path}")