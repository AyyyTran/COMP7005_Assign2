import socket
import argparse
import os
import sys

BUFFER_SIZE = 4096  

def send_file_content(client_socket, file_path):
    if not file_path.endswith('.txt'):
        print("Error: Only .txt files are supported.")
        client_socket.close()
        sys.exit(1)

    if not os.access(file_path, os.R_OK):
        print(f"Error: No read permission for the file '{file_path}'.")
        client_socket.close()
        sys.exit(1)

    try:
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    print("Finished sending file data.")
                    break
                client_socket.sendall(data)
        client_socket.shutdown(socket.SHUT_WR)
        print("Client socket shutdown.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        client_socket.close()
        sys.exit(1)
    except socket.error as e:
        print(f"Error sending file content: {e}")
        client_socket.close()
        sys.exit(1)

def receive_response(client_socket):
    try:
        response = client_socket.recv(BUFFER_SIZE).decode()
        print(f"Server response: {response}")
    except socket.error as e:
        print(f"Error receiving response: {e}")
        sys.exit(1)

def start_client(server_ip, server_port, file_path):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((server_ip, server_port))
        print(f"Connected to server at {server_ip}:{server_port}")

        send_file_content(client_socket, file_path)
        receive_response(client_socket)
    except socket.gaierror:
        print(f"Error: Unable to resolve the server address '{server_ip}'. Please check if the IP address or hostname is correct.")
        sys.exit(1)
    except socket.timeout:
        print(f"Error: Connection to {server_ip}:{server_port} timed out.")
        sys.exit(1)
    except socket.error as e:
        print(f"Error: Could not connect to {server_ip}:{server_port}. Please check if the IP address is correct and the server is running.")
        print(f"Details: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nClient interrupted by user during connection attempt. Exiting...")
        sys.exit(1)
    finally:
        if 'client_socket' in locals():
            client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send file content to TCP server.')
    parser.add_argument('--ip', type=str, required=True, help='Server IP address')
    parser.add_argument('--port', type=int, required=True, help='Server port number')
    parser.add_argument('--file', type=str, required=True, help='Path to the .txt file to send')

    args = parser.parse_args()

    if len(sys.argv) > 7:  
        print("Error: Too many arguments provided.")
        sys.exit(1)

    if not args.file.endswith('.txt'):
        print("Error: Only .txt files are allowed.")
        sys.exit(1)

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)

    if not (1024 <= args.port <= 65535):
        print(f"Error: Port number {args.port} is invalid. It must be between 1024 and 65535.")
        sys.exit(1)

    start_client(args.ip, args.port, args.file)
