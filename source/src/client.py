import socket
import argparse
import os

BUFFER_SIZE = 4096  # Same buffer size as server

def send_file_content(client_socket, file_path):
    """Send the file content to the server."""
    try:
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:  # End of file
                    print("Finished sending file data.")  # Debugging line
                    break
                client_socket.sendall(data)
                print(f"Sent {len(data)} bytes to server.")  # Debugging line

        # Close the socket explicitly after sending the file to signal the end of transmission
        client_socket.shutdown(socket.SHUT_WR)  # Signal no more data will be sent
        print("Client socket shutdown for writing.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except socket.error as e:
        print(f"Error sending file content: {e}")
        sys.exit(1)

def receive_response(client_socket):
    """Receive the response from the server."""
    try:
        response = client_socket.recv(BUFFER_SIZE).decode()
        print(f"Server response: {response}")
    except socket.error as e:
        print(f"Error receiving response: {e}")
        sys.exit(1)

def start_client(server_ip, server_port, file_path):
    """Start the client, send the file content, and receive the server's response."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        print(f"Connected to server at {server_ip}:{server_port}")

        send_file_content(client_socket, file_path)
        receive_response(client_socket)
    finally:
        client_socket.close()

# ---- Entry Point with Argument Parsing ----

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send file content to TCP server.')
    parser.add_argument('--ip', type=str, required=True, help='Server IP address')
    parser.add_argument('--port', type=int, required=True, help='Server port number')
    parser.add_argument('--file', type=str, required=True, help='Path to the file to send')

    args = parser.parse_args()

    # Ensure the file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' does not exist.")
        sys.exit(1)

    start_client(args.ip, args.port, args.file)
