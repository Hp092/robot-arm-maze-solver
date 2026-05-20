import socket
import time
import csv

def transmit_packet(target_ip, target_port, data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, target_port))
        print(f"Connected to {target_ip}:{target_port}")
        sock.sendall(data.encode('utf-8'))
        print(f"Sent: {data}")
        response = sock.recv(1024).decode('utf-8')
        print(f"Received: {response}")
    except socket.error as err:
        print(f"Error: {err}")
    finally:
        sock.close()
        print("Connection closed.")

if __name__ == "__main__":
    TARGET_IP = "192.168.1.159"
    TARGET_PORT = 5001
    FILE_PATH = "Lab4\Lab4\ik_joint_angles.csv"

    try:
        with open(FILE_PATH, mode='r') as file:
            reader = csv.reader(file)
            next(reader)

            command = "set_angles(8.63, -130.20, -128.53, -11.27, 90.00, 1.38, 1000)"
            transmit_packet(TARGET_IP, TARGET_PORT, command)
            time.sleep(1)

            row_count = 0
            for record in reader:
                row_count += 1
                print("Processing row:", row_count)
                angles = [float(value) for value in record]
                command = f"set_angles({angles[0]:.2f}, {angles[1]:.2f}, {angles[2]:.2f}, {angles[3]:.2f}, {angles[4]:.2f}, {angles[5]:.2f}, 1000)"
                transmit_packet(TARGET_IP, TARGET_PORT, command)
                time.sleep(1)
    except FileNotFoundError:
        print(f"Error: File '{FILE_PATH}' not found.")
    except Exception as err:
        print(f"An error occurred: {err}")
