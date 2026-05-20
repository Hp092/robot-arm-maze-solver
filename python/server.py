import socket
import time

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
    MESSAGE = "set_angles(8.63, -130.20, -128.53, -11.27, 90.00, 1.38, 500)"
    send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    time.sleep(5)
    MESSAGE = "set_angles(61.84, -128.46, -141.26, -0.28, 90.00, 54.60, 500)"
    send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    time.sleep(5)
    MESSAGE = "set_angles(43.98, -147.14, -82.29, -40.57, 90.00, 36.73 , 500)"
    send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    time.sleep(5)
    MESSAGE = "set_angles(67.44, -131.76, -122.60, -15.64, 90.00, 60.20, 500)"
    send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)
    time.sleep(5)
    MESSAGE = "set_angles(70.99, -138.49, -103.11, -28.40, 90.00, 63.74, 500)"
    send_tcp_packet(SERVER_IP, SERVER_PORT, MESSAGE)