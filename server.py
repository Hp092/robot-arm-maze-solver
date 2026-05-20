# import socket
# import time
#
# def send_tcp_packet(server_ip, server_port, message):
#     try:
#         # Create a TCP socket
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#         # Connect to the server
#         client_socket.connect((server_ip, server_port))
#         print(f"Connected to {server_ip}:{server_port}")
#
#         # Send the message
#         client_socket.sendall(message.encode('utf-8'))
#         print(f"Sent: {message}")
#
#         # Optionally receive a response (if server sends one)
#         response = client_socket.recv(1024).decode('utf-8')
#         print(f"Received: {response}")
#
#     except socket.error as e:
#         print(f"Error: {e}")
#
#     finally:
#         # Close the connection
#         client_socket.close()
#         print("Connection closed.")
#
# if __name__ == "__main__":
#     # Replace with the correct IP and port
#     SERVER_IP = "192.168.1.159"
#     SERVER_PORT = 5001
#     # MESSAGE = "set_angles(0, -90, 0, -90, 0, 0, 700)"
#     MESSAGE = "set_angles(8.63, -130.20, -128.53, -11.27, 90.00, 1.38, 700)"   # 0
#     send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(48.88, -132.76, -119.26, -17.98, 90.00, 41.63, 700)" # 1
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(53.23, -135.13, -112.15, -22.72, 90.00, 45.99, 700)" # 2
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(57.39, -133.29, -117.60, -19.11, 90.00, 50.14, 700)" # 3
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(60.21, -135.41, -111.36, -23.23, 90.00, 52.96, 700)" # 4
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(55.24, -139.28, -101.10, -29.62, 90.00, 47.99, 700)" # 5
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(57.37, -141.72, -95.05, -33.23, 90.00, 50.13, 700)" # 6
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(60.95, -139.47, -100.63, -29.90, 90.00, 53.70, 700)" # 7
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(61.91, -140.68, -97.59, -31.73, 90.00, 54.66, 700)" # 8
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(60.21, -135.41, -111.36, -23.23, 90.00, 52.96, 500)" # 5
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    # time.sleep(5)
    # MESSAGE = "set_angles(60.21, -135.41, -111.36, -23.23, 90.00, 52.96, 500)" # 5
    # send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)

import socket
import time
import csv

def send_tcp_packet(server_ip, server_port, message):
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((server_ip, server_port))
        print(f"Connected to {server_ip}:{server_port}")

        # Send the message
        client_socket.sendall(message.encode('utf-8'))
        print(f"Sent: {message}")

        # Optionally receive a response (if server sends one)
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {response}")

    except socket.error as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        client_socket.close()
        print("Connection closed.")


if __name__ == "__main__":
    # Replace with the correct IP and port
    SERVER_IP = "192.168.1.159"
    SERVER_PORT = 5001

    # Path to the CSV file containing joint angles
    csv_file_path = "Lab4\Lab4\ik_joint_angles.csv"

    # Read the joint angles from the CSV file
    try:
        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)

            # Skip the header
            next(csv_reader)

            MESSAGE = "set_angles(8.63, -130.20, -128.53, -11.27, 90.00, 1.38, 1000)"   # home position
            send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
            time.sleep(1)

            count =0
            for row in csv_reader:
                count+= 1
                # Construct the message from the joint angles
                print("row number is: \n", count)
                joint_angles = [float(angle) for angle in row]
                MESSAGE = f"set_angles({joint_angles[0]:.2f}, {joint_angles[1]:.2f}, {joint_angles[2]:.2f}, {joint_angles[3]:.2f}, {joint_angles[4]:.2f}, {joint_angles[5]:.2f}, 1000)"

                # Send the TCP packet
                send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)

                # Wait for 5 seconds before sending the next message
                time.sleep(1)
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")